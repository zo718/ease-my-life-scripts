#target illustrator

// Set to true if you also want PDFs
var EXPORT_PDF = false;

function toStr(v) {
    if (v === undefined || v === null) return "";
    return "" + v;
}

function trimStr(s) {
    s = toStr(s);
    // remove leading and trailing whitespace
    s = s.replace(/^\s+/, "");
    s = s.replace(/\s+$/, "");
    return s;
}

function isEmptyStr(s) {
    return trimStr(s) === "";
}

function main() {
    // Pick TSV file
    var dataFile = File.openDialog("Select the TSV file exported from Google Sheets", "*.tsv");
    if (!dataFile) {
        alert("No data file selected.");
        return;
    }

    // Pick template
    var templateFile = File.openDialog("Select your Illustrator template (with placeholders)", "*.ai");
    if (!templateFile) {
        alert("No template selected.");
        return;
    }

    // Pick output folder
    var outFolder = Folder.selectDialog("Select output folder for generated labels");
    if (!outFolder) {
        alert("No output folder selected.");
        return;
    }

    // Read TSV
    dataFile.encoding = "UTF-8";
    dataFile.open("r");
    var content = dataFile.read();
    dataFile.close();

    if (isEmptyStr(content)) {
        alert("The TSV file appears to be empty.");
        return;
    }

    var lines = content.split(/\r\n|\n|\r/);

    // Find header row (first non empty line)
    var headerRowIndex = -1;
    for (var i = 0; i < lines.length; i++) {
        if (!isEmptyStr(lines[i])) {
            headerRowIndex = i;
            break;
        }
    }
    if (headerRowIndex === -1) {
        alert("Could not find a valid header row in the TSV.");
        return;
    }

    var rawHeaders = lines[headerRowIndex].split("\t");
    var headers = [];
    for (i = 0; i < rawHeaders.length; i++) {
        var h = toStr(rawHeaders[i]);
        h = h.replace(/^\uFEFF/, ""); // remove BOM if present
        h = trimStr(h);
        headers[i] = h;
    }

    function getCol(name) {
        var target = name.toLowerCase();
        for (var j = 0; j < headers.length; j++) {
            if (toStr(headers[j]).toLowerCase() === target) {
                return j;
            }
        }
        return -1;
    }

    // Required columns
    var idxName     = getCol("Name");
    var idxLast     = getCol("Last");
    var idxAddress1 = getCol("Address1");
    var idxAddress2 = getCol("Address2");
    var idxCity     = getCol("City");
    var idxState    = getCol("State");
    var idxZip      = getCol("Zip");
    var idxCountry  = getCol("Country");

    if (idxName === -1 || idxLast === -1 || idxAddress1 === -1 ||
        idxCity === -1 || idxState === -1 || idxCountry === -1) {

        alert(
            "Missing one of the required columns: Name, Last, Address1, City, State, Country.\n\n" +
            "Found columns:\n" + headers.join(", ")
        );
        return;
    }

    function isRowEmpty(line) {
        if (isEmptyStr(line)) return true;
        var cells = line.split("\t");
        for (var k = 0; k < cells.length; k++) {
            if (!isEmptyStr(cells[k])) return false;
        }
        return true;
    }

    function val(cols, idx) {
        if (!cols || idx < 0 || idx >= cols.length) return "";
        var v = toStr(cols[idx]);
        v = v.replace(/^\uFEFF/, "");
        return trimStr(v);
    }

    function replacePlaceholder(doc, placeholder, value) {
        value = toStr(value);
        var frames = doc.textFrames;
        for (var t = 0; t < frames.length; t++) {
            var tf = frames[t];
            var txt = toStr(tf.contents);
            if (txt.indexOf(placeholder) !== -1) {
                tf.contents = txt.split(placeholder).join(value);
            }
        }
    }

    var createdCount = 0;

    // Loop over data rows
    for (var r = headerRowIndex + 1; r < lines.length; r++) {
        var line = lines[r];
        if (isRowEmpty(line)) continue;

        var cols = line.split("\t");

        var first    = val(cols, idxName);
        var last     = val(cols, idxLast);
        var address1 = val(cols, idxAddress1);
        var address2 = val(cols, idxAddress2);
        var city     = val(cols, idxCity);
        var state    = val(cols, idxState);
        var zip      = val(cols, idxZip);
        var country  = val(cols, idxCountry);

        if (isEmptyStr(first) && isEmptyStr(last) && isEmptyStr(address1) && isEmptyStr(city) && isEmptyStr(country)) {
            continue;
        }

        var fullName = trimStr((first + " " + last).replace(/\s+/g, " "));

        // Use state if present, otherwise country
        var region = !isEmptyStr(state) ? state : country;

        // Build City, Region Zip
        var cityStateZip = "";
        if (!isEmptyStr(city))   cityStateZip += city;
        if (!isEmptyStr(region)) cityStateZip += (cityStateZip ? ", " : "") + region;
        if (!isEmptyStr(zip))    cityStateZip += (cityStateZip ? " " : "") + zip;

        // Open template
        var doc = app.open(templateFile);

        // Replace placeholders in template
        replacePlaceholder(doc, "%%FULLNAME%%",     fullName);
        replacePlaceholder(doc, "%%ADDRESS1%%",     address1);
        replacePlaceholder(doc, "%%ADDRESS2%%",     address2);
        replacePlaceholder(doc, "%%CITYSTATEZIP%%", cityStateZip);

        // Build safe file name
        var baseName = !isEmptyStr(fullName) ? fullName : ("label_" + r);
        var safeName = baseName.replace(/[^a-zA-Z0-9_\-]/g, "_");
        if (isEmptyStr(safeName)) {
            safeName = "label_" + r;
        }

        // Save AI
        var aiFile = new File(outFolder.fsName + "/" + safeName + ".ai");
        var aiOpts = new IllustratorSaveOptions();
        aiOpts.embedICCProfile = true;

        try {
            doc.saveAs(aiFile, aiOpts);
        } catch (e) {
            alert("Could not save AI file for " + baseName + ":\n" + e);
        }

        // Optional PDF
        if (EXPORT_PDF) {
            try {
                var pdfFile = new File(outFolder.fsName + "/" + safeName + ".pdf");
                var pdfOpts = new PDFSaveOptions();
                pdfOpts.preserveEditability = false;
                doc.saveAs(pdfFile, pdfOpts);
            } catch (e2) {
                alert("Could not save PDF file for " + baseName + ":\n" + e2);
            }
        }

        doc.close(SaveOptions.DONOTSAVECHANGES);
        createdCount++;
    }

    alert("Done! Created " + createdCount + " labels in:\n" + outFolder.fsName);
}

main();
