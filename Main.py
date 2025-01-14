import requests
from bs4 import BeautifulSoup
import sqlite3


def get_name(url, limit):
    pages = get_pages(url)
    arr = []
    for page in range(1, pages + 1):
        new_url = url.format(page)
        soup = get_HTML(new_url)
        names = soup.find_all('div', class_='catalog-object-name', limit=limit)
        for name in names:
            arr.append(name.text.strip())
    return arr


def get_done(url, limit):
    pages = get_pages(url)
    arr = []
    for page in range(1, pages + 1):
        new_url = url.format(page)
        soup = get_HTML(new_url)
        dones = soup.find_all('span', class_='ready', limit=limit)
        for done in dones:
            arr.append(done.text.strip())
    return arr


def get_HTML(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def get_pages(url) -> int:
    soup = get_HTML(url)
    find_pages = soup.find_all('a', class_='page-pagination-link')
    return len(find_pages) - 1


def get_sales(url):
    array_sales = []
    for page in range(1, get_pages(url) + 1):
        new_url = url.format(page)
        soup = get_HTML(new_url)
        find_sales = soup.find_all('div', class_='catalog-object-sale')

        for sale_block in find_sales:
            arr_sales = []
            arr_sales.append(sale_block.text.strip())
            if '' in arr_sales:
                while '' in arr_sales:
                    arr_sales.remove('')
            array_sales.append(arr_sales)
    return array_sales


def get_all_info(url):
    sales = get_sales(url)
    names = get_name(url, len(sales))
    dones = get_done(url, len(sales))
    allinfo = {}
    for sale, name, done in zip(sales, names, dones):
        arr = []
        for cell in sale:
            arr.append(cell)
        arr = [arr, done]
        allinfo[name] = arr
    return allinfo


def create_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS irkutsk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sales TEXT NOT NULL,
            done TEXT NOT NULL
        )
    """)
    conn.commit()  # Сохраняем изменения


def insert_data_to_db(conn, data):
    cur = conn.cursor()
    for name, details in data.items():
        sales = ', '.join(details[0])  # Преобразуем список продаж в строку
        done = details[1]
        cur.execute("""
            INSERT INTO irkutsk (name, sales, done)
            VALUES (?, ?, ?)
        """, (name, sales, done))
    conn.commit()  # Сохраняем изменения


# Основной код
start_url = 'https://irk.sibdom.ru/novostroyki/Irkutskaya-oblast/?page={}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

# Получение всех данных
all_info = get_all_info(start_url)

# Подключение к базе данных SQLite
conn = sqlite3.connect("irkutsk.db")

# Создание таблицы
create_table(conn)

# Сохранение данных в базе
insert_data_to_db(conn, all_info)

# Проверка сохранённых данных
cur = conn.cursor()
cur.execute("SELECT * FROM irkutsk")
rows = cur.fetchall()
for row in rows:
    print(row)

# Закрываем соединение
conn.close()
