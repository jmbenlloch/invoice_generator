@echo OFF
set VINCLES=C:\Users\Administrator\invoice_generator
set CONDAPATH=C:\ProgramData\Miniconda3
call %CONDAPATH%\Scripts\activate.bat
start python %VINCLES%\app.py
