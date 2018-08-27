@echo off
echo Downloading Anaconda3 installer...
curl https://repo.anaconda.com/archive/Anaconda3-5.2.0-Windows-x86_64.exe -o Installers/Anaconda3.exe

echo Finished download. Running installer
Installers\Anaconda3.exe
echo Finished Anaconda3 install