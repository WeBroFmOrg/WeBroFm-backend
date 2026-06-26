@echo off
REM ============================================
REM WebroFM - Quick Deploy Script
REM Update files to server via SCP
REM ============================================
REM Before running, set your server password or configure SSH key
REM Usage: Open PowerShell as Admin, then run this batch file

set SERVER=root@187.127.164.188
set REMOTE_DIR=/var/www/webrofm/backend

echo ========================================
echo  WebroFM Backend Sync
echo ========================================

echo [1/6] Syncing serializers.py...
scp "C:\Users\user\Desktop\Dev\WeBroFm\Backend\apps\content\serializers.py" %SERVER%:%REMOTE_DIR%/apps/content/serializers.py

echo [2/6] Syncing admin_views.py...
scp "C:\Users\user\Desktop\Dev\WeBroFm\Backend\apps\core\admin_views.py" %SERVER%:%REMOTE_DIR%/apps/core/admin_views.py

echo [3/6] Syncing urls.py...
scp "C:\Users\user\Desktop\Dev\WeBroFm\Backend\apps\core\urls.py" %SERVER%:%REMOTE_DIR%/apps/core/urls.py

echo [4/6] Restarting Gunicorn on server...
ssh %SERVER% "systemctl restart webro_fm"

echo [5/6] Checking status...
ssh %SERVER% "systemctl status webro_fm --no-pager | head -20"

echo [6/6] Done! Backend updated.
pause
