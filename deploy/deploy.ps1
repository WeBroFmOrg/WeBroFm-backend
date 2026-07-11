# WeBro FM - Production Deploy Script
# Run this in PowerShell as Administrator

$hostname = "187.127.164.188"
$username = "root"
$password = "ycOAG0#+,/8(E(o5"

Write-Host "=== Connecting to $hostname ===" -ForegroundColor Cyan

# Create SSH command
$commands = @"
cd /var/www/webrofm/WeBroFm-backend
source venv/bin/activate
git pull origin main 2>&1
echo "=== GIT PULL DONE ==="

cp deploy/production.env .env 2>&1
echo "=== ENV UPDATED ==="

python manage.py migrate 2>&1
echo "=== MIGRATIONS DONE ==="

python manage.py shell -c "
from accounts.models import CustomUser
CustomUser.objects.filter(phone_number='WeBroFm@Admin_Access').delete()
u = CustomUser.objects.create(
    phone_number='WeBroFm@Admin_Access',
    full_name='Admin',
    email='admin@webrofm.in',
    is_staff=True, is_superuser=True, is_active=True
)
u.set_password('Admin@WeBroFm')
u.save()
print('ADMIN CREATED')
" 2>&1
echo "=== ADMIN USER DONE ==="

systemctl restart webro_fm 2>&1
echo "=== SERVICE RESTARTED ==="

curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://api.webrofm.in/api/home/preload/
echo "=== VERIFIED ==="
"@

# Create temp SSH script
$tmpScript = "$env:TEMP\deploy.sh"
$commands | Out-File -FilePath $tmpScript -Encoding ASCII

# Upload script and run via SSH
Write-Host "`nDeploying... (yeh 30-60 sec lagega)" -ForegroundColor Yellow

try {
    # Upload the deploy script
    scp -o StrictHostKeyChecking=accept-new $tmpScript "${username}@${hostname}:/tmp/deploy.sh" 2>&1
    Write-Host "Script uploaded!" -ForegroundColor Green
    
    # Run it
    ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30 ${username}@${hostname} "bash /tmp/deploy.sh" 2>&1
    
    Write-Host "`n=== DEPLOY COMPLETE ===" -ForegroundColor Green
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "`nManual deploy instructions:" -ForegroundColor Yellow
    Write-Host "1. ssh root@187.127.164.188" -ForegroundColor White
    Write-Host "2. cd /var/www/webrofm/WeBroFm-backend && source venv/bin/activate" -ForegroundColor White
    Write-Host "3. git pull origin main" -ForegroundColor White
    Write-Host "4. cp deploy/production.env .env" -ForegroundColor White
    Write-Host "5. python manage.py migrate" -ForegroundColor White
    Write-Host "6. systemctl restart webro_fm" -ForegroundColor White
    Write-Host "7. [Create admin user manually]" -ForegroundColor White
}
