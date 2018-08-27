@echo off
echo Running Git installer...
Installers\Git-2.18.0-64-bit.exe
echo Finished Git install

echo Logging in to GitHub account...
git config --global user.name "DWPeerNode"
git config --global user.email "DeltaWPeerNode@gmail.com"
git config --global credential.helper wincred  

echo Cloning repository
git clone https://github.com/Dynamitelaw/UDC7pAPxtknuBxa8