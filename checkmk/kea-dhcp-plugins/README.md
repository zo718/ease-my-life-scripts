# Kea DHCP plugin for Checkmk

***This started because I needed DHCP usage metrics at work. With ChatGPT’s help reviewing the code, I built this plugin and figured others might benefit too.*** \
\
This directory contains a Checkmk extension that monitors Kea DHCP IPv4 subnets, including utilization and reservations per subnet.


The package consists of:

-   `kea_dhcp-1.3.6.mkp`\
    A Checkmk extension package for Checkmk 2.4 (Check API v2). It
    installs both:
    -   A Checkmk agent plugin that talks to the Kea control API.
    -   An agent based check plugin that turns that data into services
        and metrics.
-   `kea-dhcp.py`\
    A standalone copy of the agent plugin script. You can use it
    directly on a Kea server as a Checkmk agent plugin or for manual
    testing.

------------------------------------------------------------------------

## What the plugin does

The agent plugin:

-   Connects to the Kea DHCP control API over HTTP.

-   Calls Kea statistics and configuration commands such as:

    -   `statistic-get-all` or `statistics-get-all` to fetch per subnet
        statistics.
    -   `config-get` to read `Dhcp4` configuration and derive address
        pool sizes when needed.

-   Aggregates data per IPv4 subnet:

    -   Total number of addresses in the pool.
    -   Number of used addresses.
    -   Number of free addresses.
    -   Number of reservations (when available from the stats).

-   Prints a Checkmk agent section:

        <<<kea_dhcp:sep(59)>>>
        subnet_id;subnet_cidr;total;used;free;reservations
        10;10.0.10.0/24;254;120;134;5
        20;10.0.20.0/24;254;50;204;0

-   Optionally prints a debug section listing raw Kea statistic keys:

        <<<kea_dhcp_debug:sep(0)>>>
        leases-assigned
        total-leases
        addresses_total

The Checkmk agent based check:

-   Parses the `kea_dhcp` section and creates one service per subnet.
-   Computes utilization and evaluates against thresholds.
-   Publishes metrics such as `used` and `free`.

------------------------------------------------------------------------

## Requirements

-   Kea DHCP with control API enabled.
-   Checkmk 2.4.0 to 2.6.99.
-   Python 3 on the agent host.

------------------------------------------------------------------------

## Installation using the MKP

1.  Upload MKP.

2.  Bake and deploy agent.

3.  Verify agent output:

        check_mk_agent | grep -A5 '<<<kea_dhcp'

4.  Discover services in Checkmk.

------------------------------------------------------------------------

## Manual Installation

### Agent plugin (Kea host)

    sudo cp kea-dhcp.py /usr/lib/check_mk_agent/plugins/kea_dhcp
    sudo chmod +x /usr/lib/check_mk_agent/plugins/kea_dhcp

### Check plugin (Checkmk site)

Extract from MKP and place into:

    $OMD_ROOT/local/share/check_mk/agent_based/kea_dhcp.py

------------------------------------------------------------------------

## Configuration

Environment variables:

-   `KEA_API_URL`
-   `KEA_API_TIMEOUT`
-   `KEA_DEBUG`

Example wrapper:

    #!/bin/sh
    export KEA_API_URL="http://127.0.0.1:8000/"
    /usr/lib/check_mk_agent/plugins/kea_dhcp

------------------------------------------------------------------------

## Check Parameters

Thresholds:

-   `warn_util`
-   `crit_util`
-   `warn_free`
-   `crit_free`
-   `min_reservations`

------------------------------------------------------------------------

## Subnet Evaluation Logic

1.  Compute utilization.
2.  Apply thresholds.
3.  Report summary and metrics.

------------------------------------------------------------------------

## Troubleshooting

-   Ensure plugin is executable.
-   Verify API access.
-   Enable debug mode for raw keys.

------------------------------------------------------------------------

## License & Contributions

Use at your own risk. PRs welcome.
