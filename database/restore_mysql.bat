@echo off
setlocal
if "%~1"=="" (
  echo Usage: restore_mysql.bat ^<backup.sql^>
  exit /b 1
)
if "%MYSQL_HOST%"=="" set "MYSQL_HOST=127.0.0.1"
if "%MYSQL_PORT%"=="" set "MYSQL_PORT=3306"
if "%MYSQL_USER%"=="" set "MYSQL_USER=root"

mysql --host="%MYSQL_HOST%" --port="%MYSQL_PORT%" --user="%MYSQL_USER%" --password="%MYSQL_PASSWORD%" < "%~1"
if errorlevel 1 exit /b 1
echo MySQL restore completed from: %~1
