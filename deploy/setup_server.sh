#!/bin/bash
set -e

# ──────────────────────────────────────────────
# WeBro FM - Complete Server Setup (Hostinger KVM2)
# ──────────────────────────────────────────────

### CONFIG - Change these ###
DOMAIN="api.webrofm.in"
DJANGO_USER="root"
REPO_URL="https://github.com/WeBroFmOrg/WeBroFm-backend.git"
# ──────────────────────────

echo "=== Step 1: System Update & Dependencies ==="
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server ffmpeg git certbot python3-certbot-nginx ufw

echo "=== Step 2: PostgreSQL Setup ==="
sudo -u postgres psql -c "CREATE DATABASE webrofm;"
sudo -u postgres psql -c "CREATE USER webrofm_user WITH PASSWORD 'WebroFm@2024Strong!';"
sudo -u postgres psql -c "ALTER ROLE webrofm_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE webrofm_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE webrofm_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE webrofm TO webrofm_user;"

echo "=== Step 3: Redis Setup ==="
systemctl enable redis-server
systemctl start redis-server
redis-cli ping

echo "=== Step 4: Code Clone ==="
mkdir -p /var/www/webrofm
cd /var/www/webrofm
git clone $REPO_URL
cd WeBroFm-backend

echo "=== Step 5: Python Virtual Env ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

echo "=== Step 6: Generate SECRET_KEY & .env ==="
SECRET=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

cat > .env <<ENVEOF
DEBUG=False
SECRET_KEY=$SECRET
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

R2_ACCESS_KEY_ID=your_r2_key
R2_SECRET_ACCESS_KEY=your_r2_secret
R2_BUCKET_NAME=webrofm
R2_ENDPOINT_URL=https://e75d0e418e83eb4f77917abd63f8ec0f.r2.cloudflarestorage.com
R2_PUBLIC_URL=

CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=https://$DOMAIN

ENABLE_DEV_LOGIN=False

ALLOWED_HOSTS=$DOMAIN,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://$DOMAIN
ENVEOF

echo "=== Step 7: Migrate & Collect Static ==="
python manage.py migrate
python manage.py collectstatic --noinput

echo "=== Step 8: Gunicorn Systemd Service ==="
mkdir -p /var/log/webrofm

cat > /etc/systemd/system/webro_fm.service <<'SERVICEEOF'
[Unit]
Description=WeBro FM Django
After=network.target redis-server.service postgresql.service

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/var/www/webrofm/WeBroFm-backend
EnvironmentFile=/var/www/webrofm/WeBroFm-backend/.env
ExecStart=/var/www/webrofm/WeBroFm-backend/venv/bin/gunicorn \
    webro_fm_backend.wsgi:application \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/webrofm/access.log \
    --error-logfile /var/log/webrofm/error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable webro_fm
systemctl start webro_fm
systemctl status webro_fm --no-pager

echo "=== Step 9: Nginx Setup ==="
cat > /etc/nginx/sites-available/webro_fm <<NGINXEOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 100M;
    gzip on;
    gzip_types application/json text/plain text/css application/javascript;

    location /static/ {
        alias /var/www/webrofm/WeBroFm-backend/staticfiles/;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/webro_fm /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo "=== Step 10: SSL via Certbot ==="
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN || echo "SSL failed - run manually later: certbot --nginx -d $DOMAIN"

echo "=== Step 11: Firewall ==="
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo ""
echo "============================================"
echo "  ✅ DEPLOY COMPLETE!"
echo "  🌐 https://$DOMAIN/api/home/preload/"
echo "============================================"
echo ""
echo "⚠️  DON'T FORGET:"
echo "   1. Update R2 keys in .env (nano .env)"
echo "   2. Restart: systemctl restart webro_fm"
echo "   3. Add A record: $DOMAIN → $(curl -s ifconfig.me)"
echo "============================================"
