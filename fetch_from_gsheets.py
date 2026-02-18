import os
import csv
import json
from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# !!! ЗДЕСЬ ВСТАВЬТЕ ВАШ ID ТАБЛИЦЫ !!!
SPREADSHEET_ID = "1rZ8OgKe-lJWTASpfwLWwEC1sOdvFCeu1RmxeQ8v3NyQ"

# Имена листов в том порядке, в каком они есть в таблице
# Если ваши листы называются иначе, исправьте здесь
SHEET_NAMES = ["manuscripts", "spells", "categories", "spell_categories"]

# Папка для сохранения CSV
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def fetch_sheet_to_csv(sheet_name):
    """Читает лист и сохраняет как CSV с разделителем ';'."""
    # Получаем лист по имени
    worksheet = sh.worksheet(sheet_name)
    # Читаем все значения (список списков)
    records = worksheet.get_all_values()
    if not records:
        return
    # Первая строка — заголовки столбцов
    headers = records[0]
    # Остальные строки — данные
    rows = records[1:]

    # Путь для сохранения
    csv_path = DATA_DIR / f"{sheet_name}.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"✓ {sheet_name}.csv сохранён, {len(rows)} строк")

if __name__ == "__main__":
    # Авторизация через сервисный аккаунт
    # Ключ берётся из переменной окружения (секрета GitHub)
    creds_json = os.environ.get("GCP_SERVICE_ACCOUNT_KEY")
    if not creds_json:
        raise ValueError("GCP_SERVICE_ACCOUNT_KEY environment variable not set")

    # Загружаем ключ из строки JSON
    creds_dict = json.loads(creds_json)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc = gspread.authorize(credentials)

    # Открываем таблицу по ID
    sh = gc.open_by_key(SPREADSHEET_ID)

    # Обрабатываем каждый лист
    for sheet_name in SHEET_NAMES:
        try:
            fetch_sheet_to_csv(sheet_name)
        except Exception as e:
            print(f"Ошибка при обработке листа {sheet_name}: {e}")

            raise  # Если ошибка, прекращаем выполнение
