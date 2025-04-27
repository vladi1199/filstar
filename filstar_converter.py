import csv
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# Зареждаме променливите от .env файл
load_dotenv()

# Set base_path depending on the environment (GitHub Actions or local)
if os.getenv('GITHUB_ACTIONS') == 'true':  # Check if running in GitHub Actions
    base_path = os.getcwd()  # GitHub Actions uses the current working directory (root of repo)
else:
    base_path = '/Users/vladimir/Desktop/Python/Филстар'  # Local path for local execution

# Път към CSV файла (using dynamic base_path)
csv_file_path = os.path.join(base_path, 'results_filstar.csv')

# Път към директорията за запис на XML файла (using dynamic base_path)
xml_file_path = os.path.join(base_path, 'filstar_xml.xml')

# Четене на данни от CSV файл
with open(csv_file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)  # Използване на запетая по подразбиране
    # Печат на имената на колоните за диагностика
    print(reader.fieldnames)

    products = []
    for row in reader:
        # Премахване на водещи и следващи интервали от имената на колоните
        row = {key.strip(): value for key, value in row.items()}
        products.append(row)

# Създаване на основен XML елемент
root = ET.Element('products')

# Обработка на всеки продукт
for product in products:
    # Проверка дали всички необходими колони съществуват
    if 'SKU' in product and 'Цена' in product and 'Бройки' in product and 'Наличност' in product:
        item = ET.SubElement(root, 'item')
        ET.SubElement(item, 'sku').text = product['SKU']
        ET.SubElement(item, 'price').text = product['Цена']
        ET.SubElement(item, 'quantity').text = product['Бройки']
        ET.SubElement(item, 'availability').text = 'in_stock' if product['Наличност'] == 'Наличен' else 'out_of_stock'
    else:
        print(f"Пропуснат продукт: {product} - липсваща информация!")

# Създаване на XML дърво и запис в файл
tree = ET.ElementTree(root)

# Проверка дали директорията съществува, ако не - създаване на директорията
os.makedirs(os.path.dirname(xml_file_path), exist_ok=True)

# Записване на XML файла
tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)

print(f"XML файлът е записан в: {xml_file_path}")
