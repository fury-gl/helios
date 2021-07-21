@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

if "%1" == "" goto help

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)


if "%1" == "clean" (
	:clean
	del /q /s %SOURCEDIR%\\api  %SOURCEDIR%\\reference
	rmdir %SOURCEDIR%\\api  %SOURCEDIR%\\reference
	%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% clean
	exit /B
)


if "%1" == "html-examples" (
	del /q /s  %SOURCEDIR%\\auto_examples %SOURCEDIR%\\auto_tutorials 
	rmdir %SOURCEDIR%\\auto_examples %SOURCEDIR%\\auto_tutorials 
	%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
	echo "Build finished. The HTML pages are in %BUILDDIR%"
	exit /B
)

%SPHINXBUILD% -D plot_gallery=0 -b html %SPHINXOPTS% "%SOURCEDIR%" "%BUILDDIR%/html"

goto end

:end
popd