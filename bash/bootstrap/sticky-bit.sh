#!/bin/bash
# https://habr.com/ru/company/otus/blog/710502/

# проверить, установлен ли липкий бит в доступных для записи каталогах, и, если нет, установить его

# Find all world-writable directories
for dir in $(find / -type d -perm -0002); do
  # Check if the sticky bit is set
  if [ "$(stat -c "%a" "$dir")" -eq "2" ]; then
    # If the sticky bit is not set, set it
    chmod +t "$dir"
  fi
done