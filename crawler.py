import json
import hashlib
import mysql.connector
import requests
import validators
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
from datetime import datetime
from bot import TelegramBot

image_path = './'

def slug(string):
    word_list = string.split()
    return "-".join(word_list)

import os
import time
import requests
import hashlib
from datetime import datetime

def download_image(url, save_path):
    now = datetime.now()
    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)
    folder_path = os.path.join(save_path, year, month, day)
    os.makedirs(folder_path, exist_ok=True)

    max_retries = 3
    timeout = 60
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200: 
                print("Request successful")
                break
            else:
                print(f"Request attempt {attempt + 1} failed with status code {response.status_code}")
        except requests.Timeout:
            print(f"Request attempt {attempt + 1} timed out.")
        except requests.RequestException as e:
            print(f"An error occurred on attempt {attempt + 1}: {e}")

        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    content = response.content

    md5_hash = hashlib.md5(content).hexdigest()
    ext = url.split(".")
    image_format = ext[-1].split("?")[0]
    file_path = os.path.join(folder_path, md5_hash + '.' + image_format)
    
    with open(file_path, 'wb') as f:
        f.write(content)

    return md5_hash + "." + image_format


with open('website_config.json', 'r') as f:
    website_configs = json.load(f)
    
with open('bot_config.json', 'r') as f:
    bot_config = json.load(f)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="mydatabase"
)
cursor = db.cursor()

def crawl_website(website_config):

    print(f"Crawling website: {website_config['name']}")

    categories = website_config['categories']

    try:
        for category in categories:
            max_retries = 5
            timeout = 60
            for attempt in range(max_retries):
                try:
                    response = requests.get(category["url"], timeout=timeout)
                    response.raise_for_status()
                    print("Request successful:")
                    break
                except requests.Timeout:
                    print(f"Request attempt {attempt + 1} timed out.")
                except requests.RequestException as e:
                    print(f"An error occurred on attempt {attempt + 1}:", e)

                if attempt < max_retries - 1:
                    print("Retrying...")    

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

            print(f"Page loaded successfully: {category['url']}")  

            html_schema = website_config["html_schema"]  
            
            for post in soup.find(html_schema["top_base_class"]["tag"],class_=html_schema["top_base_class"]["class"]).find_all(html_schema["items_base_class"]["tag"], class_=html_schema["items_base_class"]["class"]):
                title = post.find(html_schema["title"]).text.strip()
                description = post.find(html_schema["description"]).text.strip()
                image_url = post.find(html_schema["image"])['src']
                post_url = post.find(html_schema["url"])['href']

                if not validators.url(post_url):
                    print(f"{website_config['base_url']}{post_url}")
                    post_url = f"{website_config['base_url']}{post_url}"
                    
                post_hash = hashlib.sha256((title + description + image_url).encode()).hexdigest()

                print(f"Saving Post : {post_hash}")

                cursor.execute("SELECT COUNT(*) FROM news WHERE hash=%s", (post_hash,))
                if cursor.fetchone()[0] == 0:
                    if validators.url(image_url):
                        image_name = download_image(image_url,image_path)
                        cursor.execute("INSERT INTO news (category_id,title, description, media, hash,url,slug) VALUES (%s, %s, %s, %s, %s,%s,%s)",
                                    (category["category_id"],title, description, image_name, post_hash,post_url,slug(title)))
                        db.commit()
                        last_inserted_id = cursor.lastrowid
                        telegrabBot = TelegramBot()
                        telegrabBot.send_photo(url=f"{bot_config['base_url']}{last_inserted_id}",image_url=image_url,title=title,description=description)
                        time.sleep(1)
                else :
                    print(f"Skipping Post : {post_hash} already exist !")        
            
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Retrying ...")
        print(f"Start Again crawling proccess")
        crawl_website(website_config)

def main():
    sleep_time = 30
    for website_config in website_configs:
        print(f"Start crawling proccess")
        crawl_website(website_config)
        print(f"Stop For {sleep_time} seconds until next crawl")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()