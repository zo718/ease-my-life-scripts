#!/bin/sh
#version 1.0 - Written by Alfredo Jo ® - 2025

#super basic script. Scans all printers currently installed and disables sharing

for printer in `lpstat -p | awk '{print $2}'`
do
echo DisableShared $printer
lpadmin -p $printer -o printer-is-shared=false
done
