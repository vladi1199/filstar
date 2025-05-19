import csv
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# Зареждаме променливите от .env файл
load_dotenv()

# Set base_path depending on the environment (GitHub Actions or local)
if os.getenv('GITHUB_ACTIONS') == 'true':
    base_path = os.getcwd()
else:
    base_path = '/Users/vladimir/Desktop/Python/Филстар'

# Път към CSV файла
csv_file_path = os.path.join(base_path, 'results_filstar.csv')

# Четене на данни от CSV файл
with open(csv_file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    products = []
    for row in reader:
        row = {key.strip(): value for key, value in row.items()}
        products.append(row)

# Размер на всяка партида (chunk)
CHUNK_SIZE = 1400

# Функция за записване на продукти в XML файл
def write_products_to_xml(product_chunk, index):
    root = ET.Element('products')
    for product in product_chunk:
        if 'SKU' in product and 'Цена' in product and 'Бройки' in product and 'Наличност' in product:
            item = ET.SubElement(root, 'item')
            ET.SubElement(item, 'sku').text = product['SKU']
            ET.SubElement(item, 'price').text = product['Цена']
            ET.SubElement(item, 'quantity').text = product['Бройки']
            ET.SubElement(item, 'availability').text = 'in_stock' if product['Наличност'] == 'Наличен' else 'out_of_stock'
        else:
            print(f"Пропуснат продукт: {product} - липсваща информация!")

    tree = ET.ElementTree(root)
    xml_file_name = f"filstar_xml_{index}.xml"
    xml_file_path = os.path.join(base_path, xml_file_name)
    os.makedirs(os.path.dirname(xml_file_path), exist_ok=True)
    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    print(f"✅ Записан файл: {xml_file_path} ({len(product_chunk)} продукта)")

# Разделяне и записване на продуктите
for i in range(0, len(products), CHUNK_SIZE):
    chunk = products[i:i + CHUNK_SIZE]
    file_index = (i // CHUNK_SIZE) + 1
    write_products_to_xml(chunk, file_index)
