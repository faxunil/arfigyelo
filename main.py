from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
import mysql.connector
import sys

if len(sys.argv) < 2:
    print("Kérlek, adj meg egy terméket a parancssorból. pl.: python main.py tojás")
    exit()

termek_neve = sys.argv[1]

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="arfigyelo"
)

mycursor = mydb.cursor()

driver = webdriver.Chrome()

url = f'https://arfigyelo.gvh.hu/kereses/{termek_neve}?order=relevance'
driver.get(url)

sleep(1)

html = driver.page_source

soup = BeautifulSoup(html, 'html.parser')

termek = soup.find_all('div', 'col')
    
num = 0

print(f'Dátum: {datetime.date.today()}')

for x in termek:
    product = x.find('div', 'card-title')
    chain = x.find_all('div', 'store-name')
    prices = x.find_all('span', 'price-amount')
    uprices = x.find_all('div', 'popover__inner-unit-amount')
    if product is not None:
        num += 1
        print(f'{num} {product.text}')
        for u, p, up in zip(chain, prices, uprices):
            if u is not None and u.text.strip() and p is not None and p.text.strip():
                price_value = p.text.strip().replace(',', '.').replace('\xa0', '').replace('Ft', '')
                unit_price_value = up.text.strip().replace(',', '.').replace('\xa0', '').replace('Ft/db', '')
                print(f'   Üzlet: {u.text.strip()}  Ár: {price_value}    Egységár: {unit_price_value}')
                sql = "INSERT INTO `prices` (`chain`, `product`, `price`, `unit_price`) VALUES (%s, %s, %s, %s);"
                val = (u.text.strip(), product.text, float(price_value), float(unit_price_value))
                mycursor.execute(sql, val)
                mydb.commit()

driver.quit()
