#!/bin/bash
# WeBro FM - Single setup command
# Run: bash deploy/setup.sh

set -e

cd /var/www/webrofm/WeBroFm-backend || { echo "Directory not found"; exit 1; }

source venv/bin/activate

echo ">>> Pulling latest code..."
git pull origin main

echo ">>> Copying production env..."
cp deploy/production.env .env

echo ">>> Running migrations..."
python manage.py migrate

echo ">>> Creating admin user..."
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
print('Admin: WeBroFm@Admin_Access / Admin@WeBroFm')
"

echo ">>> Restarting services..."
systemctl restart webro_fm
systemctl restart nginx

echo ""
echo "=============================="
echo "  SETUP COMPLETE ✅"
echo "=============================="
echo "  Admin Login: WeBroFm@Admin_Access"
echo "  Admin Pass:  Admin@WeBroFm"
echo "  Django Admin: https://api.webrofm.in/a8x9k2mz-admin/"
echo "  API:         https://api.webrofm.in/api/home/preload/"
echo "=============================="
