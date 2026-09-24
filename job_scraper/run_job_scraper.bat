@echo off
REM Wrapper for Task Scheduler: runs the daily job scraper and logs output.
cd /d "C:\Users\yanng\Documents\CV\job_scraper"
echo ==== Run started %date% %time% ==== >> run_log.txt
python "C:\Users\yanng\Documents\CV\job_scraper\job_scraper.py" >> run_log.txt 2>&1
echo ==== Run finished %date% %time% ==== >> run_log.txt
