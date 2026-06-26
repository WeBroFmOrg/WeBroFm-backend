#!/bin/bash
set -e
cd /var/www/webrofm/WeBroFm-backend
source venv/bin/activate
SECRET=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
cat > .env <<ENVEOF
DEBUG=False
SECRET_KEY=${SECRET}
DB_ENGINE=postgres
DB_NAME=webrofm
DB_USER=webrofm_user
DB_PASSWORD=WebroFm@2024Strong!
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
TWILIO_ACCOUNT_SID=ACa02c5bee507406b6787bef89c38e9020
TWILIO_AUTH_TOKEN=dafd5076730ecf175af2bb4b1d2cf4cf
TWILIO_PHONE_NUMBER=+12293213556
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=webrofm
R2_ENDPOINT_URL=https://e75d0e418e83eb4f77917abd63f8ec0f.r2.cloudflarestorage.com
R2_PUBLIC_URL=
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=https://api.webrofm.in
ENABLE_DEV_LOGIN=False
ALLOWED_HOSTS=api.webrofm.in,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://api.webrofm.in
ENVEOF
echo ".env created successfully"
