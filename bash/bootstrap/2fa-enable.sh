#!/bin/bash
# https://habr.com/ru/company/otus/blog/710502/
# Check if 2FA is installed
if ! which google-authenticator > /dev/null; then
  # If 2FA is not installed, install it
  apt update
  apt install -y libpam-google-authenticator
fi

# Check if the PAM module is configured
if ! grep -q "auth required pam_google_authenticator.so" /etc/pam.d/sshd; then
  # If the PAM module is not configured, configure it
  echo "auth required pam_google_authenticator.so" >> /etc/pam.d/sshd
fi

# Check if 2FA is enabled for the current user
if ! grep -q "auth required pam_google_authenticator.so" "$(grep "^$USER:" /etc/passwd | cut -d: -f6)/.profile"; then
  # If 2FA is not enabled for the current user, enable it
  google-authenticator
  echo "auth required pam_google_authenticator.so" >> "$(grep "^$USER:" /etc/passwd | cut -d: -f6)/.profile"
fi

# Restart the SSH daemon to apply changes
systemctl restart ssh
