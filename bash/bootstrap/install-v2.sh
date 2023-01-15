#!/bin/bash
# https://habr.com/ru/company/otus/blog/710502/

# Этот сценарий устанавливает и активирует необходимые пакеты, включая брандмауэр ufw и средство предотвращения вторжений fail2ban. Затем он настраивает различные расширенные механизмы сетевой безопасности Linux, включая защиту от спуфинга IP, файлы cookie SYN, проверку исходного адреса и файлы cookie TCP SYN.

# Сценарий также настраивает фаирволл ufw так, чтобы он по умолчанию блокировал все входящие подключения и разрешал исходящие. Это может помочь предотвратить несанкционированный доступ к вашей системе и защитить от потенциальных угроз.

# Наконец, сценарий включает и запускает службу fail2ban, которая может помочь предотвратить атаки брутфорс путем блокировки IP-адресов, которые неоднократно не проходили аутентификацию.

# С помощью этого сценария вы можете автоматизировать процесс настройки расширенных механизмов сетевой безопасности Linux и повысить безопасность своих систем.

# Install necessary packages
apt update
apt install -y ufw fail2ban

# Enable the firewall
ufw enable

# Allow SSH connections
ufw allow ssh

# Block all incoming connections by default
ufw default deny incoming

# Allow outgoing connections
ufw default allow outgoing

# Enable IP spoofing protection
echo "nospoof on" >> /etc/host.conf

# Enable SYN cookies
echo "net.ipv4.tcp_syncookies = 1" >> /etc/sysctl.conf

# Enable source address verification
echo "net.ipv4.conf.all.rp_filter = 1" >> /etc/sysctl.conf

# Enable TCP SYN cookies
echo "net.ipv4.tcp_syncookies = 1" >> /etc/sysctl.conf

# Enable TCP SYN-ACK cookies
echo "net.ipv4.tcp_synack_retries = 5" >> /etc/sysctl.conf

# Enable IP spoofing protection
echo "net.ipv4.conf.all.rp_filter = 1" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.rp_filter = 1" >> /etc/sysctl.conf

# Enable SYN cookies
echo "net.ipv4.tcp_syncookies = 1" >> /etc/sysctl.conf

# Enable source address verification
echo "net.ipv4.conf.all.rp_filter = 1" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.rp_filter = 1" >> /etc/sysctl.conf

# Enable TCP SYN cookies
echo "net.ipv4.tcp_syncookies = 1" >> /etc/sysctl.conf

# Enable TCP SYN-ACK cookies
echo "net.ipv4.tcp_synack_retries = 5" >> /etc/sysctl.conf

# Enable TCP SYN cookies
echo "net.ipv4.tcp_syncookies = 1" >> /etc/sysctl.conf

# Enable TCP SYN-ACK cookies
echo "net.ipv4.tcp_synack_retries = 5" >> /etc/sysctl.conf

# Enable fail2ban
systemctl enable fail2ban
systemctl start fail2ban
