@echo off
setlocal
if "%MYSQL_DATABASE%"=="" set "MYSQL_DATABASE=book_big_data"
if "%MYSQL_HOST%"=="" set "MYSQL_HOST=127.0.0.1"
if "%MYSQL_PORT%"=="" set "MYSQL_PORT=3306"
if "%MYSQL_USER%"=="" set "MYSQL_USER=root"
if "%BACKUP_DIRECTORY%"=="" set "BACKUP_DIRECTORY=%~dp0..\backups\mysql"
if not exist "%BACKUP_DIRECTORY%" mkdir "%BACKUP_DIRECTORY%"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%i"
set "OUTPUT=%BACKUP_DIRECTORY%\book_big_data_%STAMP%.sql"

mysqldump --host="%MYSQL_HOST%" --port="%MYSQL_PORT%" --user="%MYSQL_USER%" --password="%MYSQL_PASSWORD%" --single-transaction --databases "%MYSQL_DATABASE%" > "%OUTPUT%"
if errorlevel 1 exit /b 1
echo MySQL backup created: %OUTPUT%
