#!/usr/bin/env bash
# Bootstrap + harden a fresh Contabo Ubuntu 24.04 VPS for ARW ML Lab.
# Usage (as root):  DEPLOY_USER=deploy CI_PUBKEY="ssh-ed25519 AAAA... arw-ci" bash bootstrap_contabo.sh
# Idempotent: safe to re-run.
set -euo pipefail
DEPLOY_USER="${DEPLOY_USER:-deploy}"
APP_DIR=/opt/arw-ml-lab
export DEBIAN_FRONTEND=noninteractive

# 1. Packages and patches
apt-get update -y && apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg ufw fail2ban unattended-upgrades needrestart jq git htop

# 2. Deploy user with the same key(s) root has, plus the CI deploy key
id "$DEPLOY_USER" >/dev/null 2>&1 || adduser --disabled-password --gecos "" "$DEPLOY_USER"
usermod -aG sudo "$DEPLOY_USER"
echo "$DEPLOY_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-$DEPLOY_USER   # unattended ops by Cursor; see note below
chmod 440 /etc/sudoers.d/90-$DEPLOY_USER
install -d -m 700 -o "$DEPLOY_USER" -g "$DEPLOY_USER" /home/$DEPLOY_USER/.ssh
touch /home/$DEPLOY_USER/.ssh/authorized_keys
cat /root/.ssh/authorized_keys >> /home/$DEPLOY_USER/.ssh/authorized_keys
[ -n "${CI_PUBKEY:-}" ] && echo "$CI_PUBKEY" >> /home/$DEPLOY_USER/.ssh/authorized_keys
sort -u -o /home/$DEPLOY_USER/.ssh/authorized_keys /home/$DEPLOY_USER/.ssh/authorized_keys
chown "$DEPLOY_USER:$DEPLOY_USER" /home/$DEPLOY_USER/.ssh/authorized_keys
chmod 600 /home/$DEPLOY_USER/.ssh/authorized_keys

# 3. Swap 4 GB
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
echo 'vm.swappiness=10' > /etc/sysctl.d/99-arw.conf && sysctl --system >/dev/null
timedatectl set-timezone UTC

# 4. Firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp
ufw --force enable

# 5. fail2ban
cat > /etc/fail2ban/jail.d/sshd.local <<'J'
[sshd]
enabled = true
maxretry = 5
findtime = 10m
bantime = 1h
J
systemctl enable --now fail2ban && systemctl restart fail2ban

# 6. Unattended security upgrades (no automatic reboot)
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'U'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
U
sed -i 's#^//\?\s*Unattended-Upgrade::Automatic-Reboot .*#Unattended-Upgrade::Automatic-Reboot "false";#' /etc/apt/apt.conf.d/50unattended-upgrades || true

# 7. Docker Engine + compose plugin (official repo)
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
cat > /etc/docker/daemon.json <<'D'
{ "log-driver": "json-file", "log-opts": { "max-size": "10m", "max-file": "3" }, "live-restore": true }
D
systemctl enable --now docker && systemctl restart docker
usermod -aG docker "$DEPLOY_USER"

# 8. App directory
install -d -m 750 -o "$DEPLOY_USER" -g "$DEPLOY_USER" "$APP_DIR" "$APP_DIR/backups" "$APP_DIR/caddy"
[ -f "$APP_DIR/.env" ] || install -m 600 -o "$DEPLOY_USER" -g "$DEPLOY_USER" /dev/null "$APP_DIR/.env"

# 9. Lock SSH down only if the deploy user has at least one key
if [ -s /home/$DEPLOY_USER/.ssh/authorized_keys ]; then
  cat > /etc/ssh/sshd_config.d/99-arw-hardening.conf <<'S'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
MaxAuthTries 3
X11Forwarding no
S
  sshd -t && systemctl restart ssh
else
  echo "Refusing to disable root/password login: /home/$DEPLOY_USER/.ssh/authorized_keys is empty" >&2; exit 1
fi
echo "bootstrap done: log in as $DEPLOY_USER with your key; root and passwords are now disabled"
