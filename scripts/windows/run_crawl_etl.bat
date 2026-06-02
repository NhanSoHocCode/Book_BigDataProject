@echo off
setlocal
set "PROJECT_ROOT=%~dp0..\.."

python "%PROJECT_ROOT%\crawler_etl\crawlers\tiki_crawler.py"
if errorlevel 1 exit /b 1
python "%PROJECT_ROOT%\crawler_etl\crawlers\fahasa_crawler.py"
if errorlevel 1 exit /b 1
python "%PROJECT_ROOT%\crawler_etl\etl\merge_to_csv.py"
if errorlevel 1 exit /b 1

echo Crawl and ETL completed.
