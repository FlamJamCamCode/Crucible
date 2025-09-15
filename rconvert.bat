@echo off
REM keep a counter for files converted
set /A nfile=0
REM do not copy empty folders or any files
@echo Copying directory structure from %0 to %1 ...
xcopy /T %1 %2
REM walk directory structure and convert each file in quiet mode
for /R %1 %%v in (*.md) do (
    echo converting "%%~nxv" ...
    pandoc "%%v" -o "%2\%%~nv.pdf"
    set /A nfile+=1
)
echo Done! Converted %nfile% file(s)