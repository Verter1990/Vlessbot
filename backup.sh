#!/bin/bash

# Перейти в директорию проекта
# Убедитесь, что этот путь правильный на вашем сервере!
cd /root/Vlessbot2 || exit

# Директория для хранения бэкапов
BACKUP_DIR="./backups"

# Создать директорию, если она не существует
mkdir -p $BACKUP_DIR

# Формат имени файла с датой
DATE=$(date +%Y-%m-%d_%H-%M-%S)
FILE_NAME="backup-$DATE.sql.gz"

# Полный путь к файлу бэкапа
BACKUP_FILE="$BACKUP_DIR/$FILE_NAME"

# Загрузить переменные из .env файла, чтобы получить доступ к POSTGRES_USER
source .env

# Команда для создания бэкапа
# -T флаг для docker-compose exec, чтобы избежать проблем с tty
# pg_dumpall создает полный дамп базы данных
# gzip сжимает его на лету
echo "Creating backup..."
docker-compose exec -T db pg_dumpall -c -U $POSTGRES_USER | gzip > $BACKUP_FILE

# Проверить, успешно ли создан бэкап
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
else
    echo "Backup failed!"
    rm $BACKUP_FILE
    exit 1
fi

# Удалить бэкапы старше 7 дней
echo "Cleaning up old backups..."
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -delete

echo "Cleanup complete."
