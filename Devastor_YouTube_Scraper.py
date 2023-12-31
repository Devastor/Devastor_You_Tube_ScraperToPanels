import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
from bs4 import BeautifulSoup
from io import BytesIO
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import sys
import threading

def read_queries(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.readlines()

def setup_driver():
    options = Options()
    driver = webdriver.Chrome(options=options)
    return driver

def search_on_youtube(driver, query):
    print(f"Searching for: {query}")
    driver.get("https://www.youtube.com")  # Возвращаемся на главную страницу перед каждым запросом
    search_box = driver.find_element(By.NAME, 'search_query')
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    # Добавляем ожидание, чтобы убедиться, что результаты поиска обновились
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
    )

    print("Page loaded")
    driver.refresh()
    time.sleep(1)

    return driver.page_source

def extract_thumbnails(html):
    soup = BeautifulSoup(html, 'html.parser')
    thumbnails = []

    for video in soup.find_all('a', href=re.compile(r'/watch\?v=')):
        video_id = video['href'].split('v=')[1].split('&')[0]
        thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        print(f"Extracted thumbnail URL: {thumbnail_url}")  # Логирование
        thumbnails.append(thumbnail_url)
        break

    return thumbnails

def show_images(image_urls):
    global is_window_closed
    is_window_closed = False
    root = tk.Tk()
    root.title("YouTube Search Results")

    # Создаем сетку для отображения панелей
    row = 0
    col = 0
    for url in image_urls:
        try:
            response = requests.get(url)
            img_data = Image.open(BytesIO(response.content))            
            # Изменяем размер изображения с сохранением пропорций до 300x200
            img_data.thumbnail((300, 200))#, Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img_data)
            panel = tk.Label(root, image=img)
            panel.image = img
            panel.grid(row=row, column=col)  # Используем grid для размещения в сетке
            col += 1
            if col == 3:  # Переход на следующую строку после 3-х столбцов
                col = 0
                row += 1
        except Exception as e:
            print(f"Error loading image {url}: {e}")

    # Функция для обработки закрытия окна
    def on_close():
        print("Closing application")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)  # Привязываем функцию к событию закрытия окна
    root.mainloop()

def main():
    driver = setup_driver()
    driver.get("https://www.youtube.com")
    
    queries = read_queries("Devastor_YouTube_Query.txt")
    all_thumbnails = []

    for query in queries[:9]:  # Обрабатываем только первые 9 запросов
        html = search_on_youtube(driver, query.strip())
        thumbnails = extract_thumbnails(html)
        if thumbnails:
            all_thumbnails.extend(thumbnails)  # Добавляем все превьюшки

    driver.quit()

    if all_thumbnails:
        show_images(all_thumbnails)

    print("Press any key to finish...")
    #print("Program finished")

if __name__ == "__main__":
    main()

