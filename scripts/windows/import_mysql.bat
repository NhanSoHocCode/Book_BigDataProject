@echo off
setlocal
set "PROJECT_ROOT=%~dp0..\.."
if "%MYSQL_DATABASE%"=="" set "MYSQL_DATABASE=book_big_data"
if "%MYSQL_HOST%"=="" set "MYSQL_HOST=127.0.0.1"
if "%MYSQL_PORT%"=="" set "MYSQL_PORT=3306"
if "%MYSQL_USER%"=="" set "MYSQL_USER=root"

mysql --host="%MYSQL_HOST%" --port="%MYSQL_PORT%" --user="%MYSQL_USER%" --password="%MYSQL_PASSWORD%" < "%PROJECT_ROOT%\database\schema.sql"
if errorlevel 1 exit /b 1
python "%PROJECT_ROOT%\database\import_books.py"
if errorlevel 1 exit /b 1

echo MySQL import completed.
