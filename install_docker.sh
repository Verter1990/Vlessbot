#!/bin/bash
# Скрипт для установки Git, Docker и Docker Compose на Ubuntu

# Останавливаем выполнение в случае ошибки
set -e

# --- 1. Обновление системы ---
echo "[INFO] Обновление списка пакетов..."
sudo apt-get update

# --- 2. Установка Git ---
echo "[INFO] Установка Git..."
sudo apt-get install git -y

# --- 3. Установка Docker ---
echo "[INFO] Установка зависимостей для Docker..."
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common -y

echo "[INFO] Добавление GPG-ключа Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "[INFO] Добавление репозитория Docker..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "[INFO] Повторное обновление списка пакетов..."
sudo apt-get update

echo "[INFO] Установка Docker Engine..."
sudo apt-get install docker-ce docker-ce-cli containerd.io -y

# --- 4. Установка Docker Compose ---
echo "[INFO] Установка Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# --- 5. Настройка запуска Docker без sudo ---
echo "[INFO] Добавление текущего пользователя в группу docker..."
sudo usermod -aG docker ${USER}

echo "[SUCCESS] Установка завершена!"
echo "[IMPORTANT] Чтобы использовать Docker без sudo, выйдите с сервера и зайдите снова."
