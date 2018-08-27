@echo off
set /p gpu="Do you have a CUDA compatible NVIDIA GPU? (Y/N): "

IF %gpu%==y (
    goto INSTALL_GPU_VERSION
) 
IF %gpu%==Y (
    goto INSTALL_GPU_VERSION
)

IF %gpu%==n (
    goto INSTALL_CPU_VERSION
)
IF %gpu%==N (
    goto INSTALL_CPU_VERSION
)


:INSTALL_CPU_VERSION
echo Installing CPU version of Tensorflow...
pip3 install --upgrade tensorflow
goto TEST_INTSALL


:INSTALL_GPU_VERSION
echo Downloading CUDA...
curl https://developer.download.nvidia.com/compute/cuda/9.0/secure/Prod/local_installers/cuda_9.0.176_win10.exe?EvoUIgKGgw8mWn0Sv_VSsE6-7LtEgjDpw9aXQK-GpRT4Zo-CiIiGWnVHfpe0L8nWQVBUN1hp7g01kBMS6gkeCIaE6BofX2TREpPs5b5SxMAJYSlE7YXJcR3n4G9zfc-4ofQgBEl_AY4AbxJNM-zfqzRrDCVlw4Q4QJt5RnuPWfEEceU -o Installers/CUDAinstall.exe
echo Running CUDA Installer...
Installers\CUDAinstall.exe

echo Copying over cuDNN files...
copy Installers\cuda\bin\cudnn64_7.dll to C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.0\bin.
copy Installers\cuda\ include\cudnn.h to C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.0\include.
copy Installers\cuda\lib\x64\cudnn.lib to C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.0\lib\x64.

echo Installing GPU version of Tensorflow...
pip3 install --upgrade tensorflow-gpu

goto TEST_INTSALL


:TEST_INTSALL
echo Testing Tensorflow install...
python HelperBatchFiles\TestTensorflowInstall.py