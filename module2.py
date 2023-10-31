import os
import json
import requests
from bs4 import BeautifulSoup

# Функция для скачивания картинок и сохранения ссылки в JSON
def download_and_save_image(image_url, image_filename):
    image_directory = "img"
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)

    image_path = os.path.join(image_directory, image_filename)

    response = requests.get(image_url)

    if response.status_code == 200:
        with open(image_path, 'wb') as file:
            file.write(response.content)
        return image_path
    else:
        print(f"Не удалось скачать изображение: {image_url}")
        return None


def download_image(image_url, product_link):
    # Получаем последний слаг из ссылки на продукт
    product_slug = product_link.rstrip('/').split('/')[-1]

    # Определяем путь для сохранения изображения
    image_path = os.path.join('img', f"{product_slug}.jpg")

    # Скачиваем изображение
    response = requests.get(image_url, stream=True)
    with open(image_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    return image_path


# Загрузка данных из первого этапа парсинга (book_database.json)
with open('book_database.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Парсим страницы книг
for item in data:
    url = item['link']

    # В переменную сохраним юзер-агент, что-бы браузер не считал наши обращения как действия бота
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.find('div', class_='short-text')

    # Получим описание книги
    if text:
        description = text.get_text(strip=True)
        item['description'] = description
    else:
        item['description'] = 'Описание не найдено'

    # Получаем адрес картинки, качаем ее и заносим данные в элементы для дальнейшей записи в 'book_database.json'
    full_img_elem = soup.find('div', class_='full-img')
    if full_img_elem:
        image_url = item['URL'] + full_img_elem.find('img')['src']
        image_filename = image_url.split('/')[-1]
        image_path = download_and_save_image(image_url, image_filename)
        item['image_url'] = image_url
        item['image_path'] = image_path
    else:
        item['image_url'] = 'Картинка не найдена'
        item['image_path'] = None

# Обновление JSON-файла с новой информацией
with open('book_database.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    with open('book_database.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for product in data:
        product_link = product['link']
        image_url = product['image_url']

        # Переименовываем изображение и получаем его новый путь
        new_image_path = download_image(image_url, product_link)

        # Обновляем информацию в словаре продукта
        product['image_path'] = new_image_path

    # Обновляем JSON-файл
    with open('book_database.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()