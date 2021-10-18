@CLS
@ECHO OFF
@ECHO ==================================
@ECHO Deployment Tool
@ECHO Nate Bachmeier - 2021
@ECHO ==================================

@SETLOCAL enableextensions enabledelayedexpansion
@SET base_path=%~dp0\..
@PUSHD %base_path%

@CALL docker build -t riv-deploy images/cdk-deploy
@CALL docker run -it -v %userprofile%\.aws:/root/.aws -v %cd%:/files -v /var/run/docker.sock:/var/run/docker.sock -w /files riv-deploy ship-it

@POPD