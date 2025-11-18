#!/bin/sh

#super basic script. Scans all printers currently installed and disables sharing

for printer in `lpstat -p | awk '{print $2}'`
do
echo DisableShared $printer
lpadmin -p $printer -o printer-is-shared=false
done
