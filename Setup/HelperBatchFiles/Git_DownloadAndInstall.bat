echo Downloading Git installer...
curl https://github.com/git-for-windows/git/releases/download/v2.18.0.windows.1/Git-2.18.0-64-bit.exe -o Installers/GitInstaller.exe

echo Finished download. Running installer
Installers\GitInstaller.exe
echo Finished Anaconda3 install