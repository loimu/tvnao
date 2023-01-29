Set PYTHON_EXEC=python
Set _VERSION=Python39-32
Set _LIB_PATH=%userprofile%\AppData\Local\Programs\Python\%_VERSION%\Lib\site-packages

del /Q /F /S build dist tvnao.spec
%PYTHON_EXEC% -m PyInstaller --noconfirm ^
  --paths "%_LIB_PATH%\PyQt5\Qt\bin" ^
  --name="tvnao" --onefile ^
  "Z:\\tvnao\run.py"
move .\"dist\tvnao.exe" "Z:\\tvnao-x86\tvnao.exe"
