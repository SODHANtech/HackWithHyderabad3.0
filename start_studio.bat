@echo off
title Hindsight Autonomous Application Studio V2
echo ========================================================
echo  Starting Hindsight Autonomous Application Studio V2
echo  Hack With Hyderabad 3.0 Edition
echo ========================================================
echo.
echo Launching server at http://127.0.0.1:8000 ...
echo Opening Studio at http://127.0.0.1:8000/studio ...
echo.

start "" "http://127.0.0.1:8000/studio"
python run.py
pause
