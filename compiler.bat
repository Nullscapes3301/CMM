@echo off
setlocal

chdir /d "%~dp0"

echo Compiling interpreter...

python -m PyInstaller --onefile ^
--distpath "dist" ^
"src\cmm.py"

if errorlevel 1 (
    exit /b 1
)

echo Compiling IDLE...

python -m PyInstaller --onefile ^
--distpath "dist" ^
"src\ide.pyw"

if errorlevel 1 (
    exit /b 1
)

rmdir /s /q build
del *.spec 2>nul

echo Compilation finished without errors.
echo Starting IDLE

start dist/IDLE.exe

endlocal