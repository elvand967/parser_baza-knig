# D:\Python\myProject\parser_baza-knig\module2.py
import mimetypes
import time
import random
import os
import json
import requests
from bs4 import BeautifulSoup
import datetime
from transliterate import translit  # Убедитесь, что у вас установлен модуль transliterate

from module1 import URL, HEADERS


# Функция для загрузки данных из JSON
def load_data_from_json(file_path, n, x):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Отфильтруем словари, оставив только те, где "page" в диапазоне от n до x
    filtered_data = [item for item in data if n >= item['page'] >= x]

    return filtered_data



def parser_page(dict_page, URL = URL, HEADERS = HEADERS):
    # Извлекаем URL страницы из словаря
    page_url = dict_page.get("link")

    if page_url:
        try:
            # Делаем GET-запрос к странице
            response = requests.get(page_url, headers=HEADERS)
            response.raise_for_status()  # Проверяем успешность запроса

            # Создаем объект BeautifulSoup для парсинга страницы
            soup = BeautifulSoup(response.text, "html.parser")

            # Извлекаем URL картинки
            img_element = soup.find("div", class_="full-img").find("img")
            img_src = img_element.get("src")

            if img_src:
                # Добавляем префикс URL сайта, если необходимо
                if not img_src.startswith("http"):
                    img_src = f"{URL}/{img_src}"

                # Получаем имя файла из URL
                img_filename = os.path.basename(img_src)
                img_save_path = os.path.join("img_downloads", img_filename)

                # Создаем директорию, если она не существует
                os.makedirs("img_downloads", exist_ok=True)

                # Скачиваем и сохраняем изображение
                response = requests.get(img_src, headers=HEADERS)
                response.raise_for_status()

                # Получим исходное расширение изображения
                content_type = response.headers.get('content-type')
                if content_type:
                    ext = mimetypes.guess_extension(content_type)
                    if ext:
                        ext = ext.lstrip('.')
                    else:
                        ext = "jpg"
                else:
                    ext = "jpg"

                # Вызываем функцию для переименования изображения
                img_filename = rename_and_save_image(response.content, dict_page['title'], ext)

                # Сохранение изображения
                img_save_path = os.path.join("img_downloads", img_filename)
                with open(img_save_path, "wb") as img_file:
                    img_file.write(response.content)

                # Обновляем словарь dict_page_new
                dict_page_new = dict(dict_page)
                dict_page_new["image_file"] = img_filename

                # Вызываем функцию для сохранения данных в JSON
                save_to_json(dict_page_new, "book_database2.json")

            else:
                print("Изображение не найдено на странице.")

        except Exception as e:
            print(f"Ошибка при парсинге страницы {page_url}: {e}")
    else:
        print("URL страницы отсутствует в словаре.")


def rename_and_save_image(img_url, title, ext):
    # Транслитерация кириллического текста в латиницу
    latin_title = translit(title, reversed=True)

    # Получение текущей даты в формате "MMDD"
    current_date = datetime.datetime.now().strftime("%m%d")

    # Формирование имени файла изображения
    img_filename = f"{latin_title}_{current_date}.{ext}"

    return img_filename



# Эта функция будет добавлена позже
def save_to_json(data, file_path):
    pass


# Функция main
def main():
    # Опредилим путь к '*.json'
    file_path = 'book_database.json'

    # опредилим предварительные по погинации страницы для парсинга
    n = 5049
    x = 5049

    # Вызовим функцию для загрузки данных из JSON
    data = load_data_from_json(file_path, n, x)

    # Запустим цикл по словарям
    for dict_page in data:
        print(f"Парсинг страницы: {dict_page['title']}")

        # Засекаем начало времени
        start_time = time.time()

        parser_page(dict_page)

        # Засекаем конец времени и рассчитываем время
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Время парсинга: {elapsed_time:.2f} сек")
        t = random.randint(1, 3)
        print(f'Задержка {t} seconds')
        time.sleep(t)


if __name__ == "__main__":
    main()