import zipfile, os, datetime

zip_file_name = datetime.datetime.now().strftime('vlessbot2_backup_%Y%m%d_%H%M%S.zip')

with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('.'):
        for file in files:
            # Exclude the backup file itself and any pyc files
            if file == zip_file_name or file.endswith('.pyc'):
                continue
            zipf.write(os.path.join(root, file))

print(f'Создан архив: {zip_file_name}')