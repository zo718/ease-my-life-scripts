#!/bin/sh
#version 1.0 - Written by Alfredo Jo ® - 2025
#Basic script that iterates over all remote Git branches in my laptop and removes them. Verified on macOS.

for i in `git branch -r|grep -v main`; do git branch -rd $i; done
