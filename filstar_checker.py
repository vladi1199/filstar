import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Зареждаме променливите от .env файл
load_dotenv()

# Set base_path depending on the environment (GitHub Actions or local)
if os.getenv('GITHUB_ACTIONS') == 'true':  # Check if running in GitHub Actions
    base_path = os.getcwd()  # GitHub Actions uses the current working directory (root of repo)
else:
    base_path = '/Users/vladimir/Desktop/Python/Филстар'  # Local path for local execution

# Конфигурация на драйвъра
def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

# Търсене на URL на първия продукт за даден SKU
def find_product_url(driver, sku):
    search_url = f"https://filstar.com/bg/products/search/?q={sku}"
    driver.get(search_url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='?sku=']"))
        )
        link_el = driver.find_element(By.CSS_SELECTOR, "a[href*='?sku=']")
        product_url = link_el.get_attribute("href")
        
        # Проверяваме дали SKU-то е част от URL-то
        if sku in product_url:
            return product_url
        else:
            print(f"❌ Продуктът за SKU {sku} не съвпада с очакваното URL.")
            return None
    except Exception as e:
        print(f"❌ Продукт с SKU {sku} не е намерен: {e}")
        return None

# Проверка на наличността, бройката и цената на продукта
def check_availability_and_price(driver, sku):
    try:
        # Проверяваме дали редът за конкретния SKU съществува
        try:
            row = driver.find_element(By.CSS_SELECTOR, f"tr[class*='table-row-{sku}']")
        except Exception as e:
            print(f"❌ Не беше намерен ред с SKU {sku}: {e}")
            return None, 0, None
        
        # Извличаме наличността и цената
        qty_input = row.find_element(By.CSS_SELECTOR, "td.quantity-plus-minus input")
        max_qty_attr = qty_input.get_attribute("data-max-qty-1")
        max_qty = int(max_qty_attr) if max_qty_attr and max_qty_attr.isdigit() else 0
        
        status = "Наличен" if max_qty > 0 else "Изчерпан"
        
        price_element = row.find_element(By.CSS_SELECTOR, "td div.custom-tooltip-holder")
        price_text = price_element.text.strip().split()[0]  # Взимаме само числото, без "лв."
        
        return status, max_qty, price_text
    except Exception as e:
        print(f"❌ Грешка при проверка на наличността и цената за SKU {sku}: {e}")
        return None, 0, None

# Четене на SKU кодове от CSV
def read_sku_codes(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        return [row[0].strip() for row in reader if row]

# Записване на резултатите в CSV
def save_results(results, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['SKU', 'Наличност', 'Бройки', 'Цена'])
        writer.writerows(results)

# Записване на ненамерени SKU кодове в нов CSV
def save_not_found(skus_not_found, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['SKU'])
        for sku in skus_not_found:
            writer.writerow([sku])

# Основна функция
def main():
    sku_file = os.path.join(base_path, 'sku_list_filstar.csv')  # Path for SKU CSV file
    result_file = os.path.join(base_path, 'results_filstar.csv')  # Path for saving results
    not_found_file = os.path.join(base_path, 'not_found_filstar.csv')  # Path for not found SKUs

    skus = read_sku_codes(sku_file)
    driver = create_driver()
    results = []
    not_found = []  # Списък за ненамерени SKU кодове

    for sku in skus:
        print(f"➡️ Обработва се SKU: {sku}")
        product_url = find_product_url(driver, sku)
        if product_url:
            print(f"  ✅ Намерен: {product_url}")
            driver.get(product_url)
            status, qty, price = check_availability_and_price(driver, sku)
            
            # Ако не се намери ред за SKU или ако има грешка при извличането на информацията, считаме за ненамерен
            if status is None or price is None:
                print(f"❌ Продукт с SKU {sku} не е валиден или не съдържа информация.")
                not_found.append(sku)  # Добавяме ненамерени SKU в списъка
            else:
                results.append([sku, status, qty, price])  # Записваме само намерените продукти
        else:
            not_found.append(sku)  # Добавяме ненамерени SKU в списъка

    driver.quit()
    
    # Записваме резултатите само за намерените SKU
    save_results(results, result_file)
    # Записваме ненамерени SKU в отделен CSV
    save_not_found(not_found, not_found_file)
    
    print(f"✅ Резултатите са записани в: {result_file}")
    print(f"❌ Ненамерените SKU са записани в: {not_found_file}")

if __name__ == '__main__':
    main()
