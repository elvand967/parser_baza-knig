# D:\Python\myProject\parser_baza-knig\module1.py

# pip install requests
import requests
# pip install requests bs4
from bs4 import BeautifulSoup
import json


# Вместо функции save используем функцию для сохранения в JSON
def save_to_json(comps, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(comps, file, ensure_ascii=False, indent=4)

# # функция заменена на def save_to_json(comps, filename), для сохранения
# def save(comps):
#     with open('book_database.txt', 'a') as file:
#         for comp in comps:
#             file.write(f"Книга: {comp['title']}\n")
#             file.write(f"Автор: {comp['author']}\n")
#             file.write(f"Читает: {comp['read_book']}\n")
#             file.write(f"Длительность: {comp['duration']}\n")
#             file.write(f"Цикл: {comp['cycle']}\n")
#             file.write(f"Жанр: {comp['genre']}\n")
#             file.write(f"Ссылка: {comp['link']}\n")
#             file.write(f"\n")


def parser():
    # Создадим переменную в которой будем хранить адрес сайта, который хотим парсить
    URL = 'https://baza-knig.ink/'

    # В переменную сохраним юзер-агент, что-бы браузер не считал наши обращения как действия бота
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    page = 5045
    while page > 5044:
        URLpage = URL + '/page/' + str(page)

        # отправим запрос на сервер
        response = requests.get(URLpage, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.findAll('div', class_='short')
        comps = []

        for item in items:
            author_elem = item.find('ul', class_='reset short-items').find_all('li')[0].find('a')
            read_book_elem = item.find('ul', class_='reset short-items').find_all('li')[1].find('a')
            duration_elem = item.find('ul', class_='reset short-items').find_all('li')[2].find('b')
            cycle_elem = item.find('ul', class_='reset short-items').find_all('li')[3].find('a')

            genre_elems = item.find('ul', class_='reset short-items').find_all('li')[4].find_all('a') if len(
                item.find('ul', class_='reset short-items').find_all('li')) > 4 else []

            comps.append({
                'title': item.find('div', class_='short-title').get_text(strip=True),
                'author': author_elem.get_text(strip=True) if author_elem else 'Не найдено',
                'read_book': read_book_elem.get_text(strip=True) if read_book_elem else 'Не найдено',
                'duration': duration_elem.get_text(strip=True) if duration_elem else 'Не найдено',
                'cycle': cycle_elem.get_text(strip=True) if cycle_elem else 'Не найдено',
                'genre': ', '.join(
                    [genre.get_text(strip=True) for genre in genre_elems]) if genre_elems else 'Не найдено',
                'link': item.find('div', class_='short-title').find('a').get('href'),
                'URL': URL,  # Домашняя страница сайта
            })

        for comp in comps:
            print(f"Книга: {comp['title']}\nАвтор: {comp['author']}\nЧитает: {comp['read_book']}\n"
                  f"Длительность: {comp['duration']}\nЦикл: {comp['cycle']}\n"
                  f"Жанр: {comp['genre']}\nСсылка: {comp['link']}\n")

        # save(comps)

        # Сохраняем список ссылок в JSON файл
        save_to_json(comps, 'book_database.json')

        page = page - 1


if __name__ == "__main__":
    parser()