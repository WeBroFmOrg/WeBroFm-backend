#!/bin/bash
# WebroFM Backend Production Deployment Script
# Usage: bash deploy.sh

set -e

echo "=== WebroFM Backend Deployment ==="

# 1. Load env
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env and configure."
    exit 1
fi

# 2. System deps
echo "[1/6] Installing system dependencies..."
apt update -y
apt install -y python3 python3-venv python3-pip nginx redis-server ffmpeg

# 3. Python venv
echo "[2/6] Setting up Python virtual environment..."
if [ ! -d venv ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Django setup
echo "[3/6] Running Django migrations..."
python manage.py migrate --run-syncdb
python manage.py collectstatic --noinput

# 5. Nginx
echo "[4/6] Configuring Nginx..."
cp deploy/webro_fm.nginx /etc/nginx/sites-available/webro_fm
if [ ! -f /etc/nginx/sites-enabled/webro_fm ]; then
    ln -s /etc/nginx/sites-available/webro_fm /etc/nginx/sites-enabled/
fi
nginx -t && systemctl restart nginx

# 6. Systemd service
echo "[5/6] Installing systemd service..."
cp deploy/webro_fm.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable webro_fm
systemctl restart webro_fm

echo "[6/6] Deployment complete!"
echo "=== Check status: systemctl status webro_fm ==="
