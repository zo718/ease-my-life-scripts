#!/usr/bin/env python3
# kea_dhcp - Checkmk agent plugin for Kea DHCP (v1.3.x)
# Outputs: <<<kea_dhcp:sep(0)>>>
# Columns: subnet_id;subnet_cidr;total;used;free;reservations
# KEA_DEBUG=1 adds <<<kea_dhcp_debug:sep(0)>>> with stat keys seen.

import os, json, re, urllib.request

API_URL = os.environ.get("KEA_API_URL", "http://10.200.1.68:8000/")
TIMEOUT = float(os.environ.get("KEA_API_TIMEOUT", "5.0"))
DEBUG = os.environ.get("KEA_DEBUG", "0") not in ("0", "", "false", "False", "no", "No")

def _call(command, arguments=None, service=None):
    body = {"command": command}
    if arguments is not None:
        body["arguments"] = arguments
    body["service"] = service or ["dhcp4"]
    url = API_URL.rstrip("/") + "/"
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"))
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _get_stats():
    for cmd in ("statistic-get-all", "statistics-get-all"):
        try:
            return _call(cmd, {})
        except Exception:
            continue
    return []

def _fetch_config():
    try:
        res = _call("config-get", {})
        for r in res:
            cfg = r.get("arguments", {}).get("Dhcp4", {})
            if cfg:
                return cfg
    except Exception:
        pass
    return {}

def _pool_total(p):
    rng = p.get("pool", "")
    if "-" not in rng:
        return 0
    start, end = [x.strip() for x in rng.split("-", 1)]
    def ip2i(a):
        o = list(map(int, a.split(".")))
        return (o[0]<<24) + (o[1]<<16) + (o[2]<<8) + o[3]
    return max(0, ip2i(end) - ip2i(start) + 1)

def main():
    seen_names = []
    stats_raw = _get_stats()
    per_subnet = {}

    def put(sid, key, val):
        d = per_subnet.setdefault(str(sid), {})
        d[key] = int(val)

    for item in stats_raw or []:
        args = item.get("arguments", {}) or {}

        if isinstance(args, dict):
            for k, v in args.items():
                seen_names.append(str(k))
                m = re.match(r"subnet\[(\d+)\]\.(.+)", str(k))
                if not m:
                    continue
                sid, metric = m.group(1), m.group(2).lower()
                val = None
                if isinstance(v, list) and v:
                    last = v[-1]
                    if isinstance(last, list) and last:
                        val = last[0]
                    elif isinstance(last, (int, float)):
                        val = last
                if val is None:
                    continue
                if metric in ("assigned-addresses", "leases-assigned", "total-leases", "addresses_assigned"):
                    put(sid, "used", val)
                elif metric in ("total-addresses", "addresses_total", "total_addresses"):
                    put(sid, "total", val)
                elif "declined" in metric:
                    put(sid, "declined", val)
                elif "reservation" in metric:
                    put(sid, "reservations", val)

        for group_key in ("statistics", "subnet4", "dhcp4", "stats", "result"):
            entries = args.get(group_key)
            if isinstance(entries, list):
                for st in entries:
                    name = st.get("name") or st.get("stat-name") or ""
                    if name:
                        seen_names.append(str(name))
                    value = st.get("value") or st.get("sum") or st.get("count") or 0
                    sid = st.get("subnet-id") or st.get("subnet_id")
                    if sid is not None:
                        key = (st.get("name") or "").lower()
                        if "assigned" in key:
                            put(sid, "used", value)
                        elif "total-addresses" in key or "addresses_total" in key:
                            put(sid, "total", value)
                        elif "reservation" in key:
                            put(sid, "reservations", value)
                        continue
                    m = re.match(r"subnet\[(\d+)\]\.(.+)", str(name))
                    if m:
                        sid = m.group(1)
                        metric = m.group(2).lower()
                        if metric in ("assigned-addresses", "leases-assigned", "total-leases", "addresses_assigned"):
                            put(sid, "used", value)
                        elif metric in ("total-addresses", "addresses_total", "total_addresses"):
                            put(sid, "total", value)
                        elif "declined" in metric:
                            put(sid, "declined", value)
                        elif "reservation" in metric:
                            put(sid, "reservations", value)

    cfg = _fetch_config()
    subnets = cfg.get("subnet4", [])
    for s in subnets:
        sid = str(s.get("id", "unknown"))
        cidr = s.get("subnet", "")
        total_from_pools = sum(_pool_total(p) for p in s.get("pools", []))
        per_subnet.setdefault(sid, {})
        per_subnet[sid].setdefault("total", int(total_from_pools))
        per_subnet[sid]["cidr"] = cidr
        resv_count = len(s.get("reservations", []))
        if resv_count:
            per_subnet[sid]["reservations"] = int(per_subnet[sid].get("reservations", 0)) + resv_count

    global_res = cfg.get("reservations", [])
    for r in global_res:
        sid = str(r.get("subnet-id") or r.get("subnet_id") or "")
        if sid:
            per_subnet.setdefault(sid, {})
            per_subnet[sid]["reservations"] = int(per_subnet[sid].get("reservations", 0)) + 1

    print("<<<kea_dhcp:sep(0)>>>")
    for sid, d in sorted(per_subnet.items(), key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else 999999):
        total = int(d.get("total", 0))
        used = int(d.get("used", 0))
        free = max(0, total - used) if total else 0
        resv = int(d.get("reservations", 0))
        cidr = d.get("cidr", "")
        if cidr or total or used or resv:
            print(f"{sid};{cidr};{total};{used};{free};{resv}")

    if DEBUG:
        print("<<<kea_dhcp_debug:sep(0)>>>")
        uniq = []
        for n in seen_names:
            if n not in uniq:
                uniq.append(n)
        for n in uniq[:300]:
            print(n)
        if len(uniq) > 300:
            print(f"... ({len(uniq)-300} more)")

if __name__ == "__main__":
    main()
