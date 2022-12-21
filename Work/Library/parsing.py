import os
import bs4
import requests
import selenium
from time import sleep
from datetime import datetime
from selenium import webdriver

types = {'Сексуальные преступления против несовершеннолетних': 3,
         'Преступления, связанные с алкоголем, наркотиками и другими возбуждающими средствами': 7,
         'Преступления в отношении представителя власти': 8,
         'Преступления совершенные мигрантами': 9,
         'ГИБДД, ДПС, ДТП': 148,
         'Коррупция': 149,
         'Нарушение законов полицией': 150,
         'Убийство': 151 }

class Parser:
    def __init__(self):
        op = webdriver.ChromeOptions()
        #op.add_argument('headless')
        driver_path = os.path.join(os.getcwd(), 'Library', 'chromedriver.exe')
        self.driver = webdriver.Chrome(options=op,
                                 executable_path=driver_path)

    def get_one_news(self, url):
        _id = int(url.split('/')[-1].split('-')[0])
        resp = requests.get(url)
        if resp.ok:
            contents = resp.text
            root = bs4.BeautifulSoup(contents, 'lxml')
                
            theme = root.find('span', {'class': 'theme'})
            
            tags = root.find('span', {'class': 'theme-tags'})
            _type = tags.find('a').text
                    
            title = root.find('span', {'class': 'title'}).text
            
            btn = root.find('div', {'class': 'btn'})
            raw = btn.find('span').text[50:66].replace(':', ' ')
            raw = list(map(int, raw.split()))
            published = datetime(
                year = raw[0],
                month = raw[1],
                day = raw[2],
                hour = raw[3],
                minute = raw[4]
            )
                
            return _id, title, url, _type, published               
        else:
            return None

    def get_all_news(self):
        for i in types.items():
            self.driver.get(f'https://mchsrf.ru/region/tag/{i[1]}')
            sleep(1)
            elem = self.driver.find_element_by_name('date_from')
            elem.clear()
            elem.send_keys("01.01.2000")
            self.driver.find_element_by_class_name('form-submit').click()
            while True:
                try:
                    self.driver.find_element_by_link_text("Показать еще").click()
                except selenium.common.exceptions.NoSuchElementException:
                    break
                except selenium.common.exceptions.StaleElementReferenceException:
                    sleep(0.1)
            root = bs4.BeautifulSoup(self.driver.page_source, 'lxml')
            urls = ['https://mchsrf.ru' + a.get('href') for a in root.find_all('a', {'class': 'news-title'})]
            for url in urls:
                yield self.get_one_news(url)

    def get_news(self, date_from, date_to, s_types=None):
        if not s_types:
            s_types = [i[1] for i in types.items()]
        for i in s_types:
            self.driver.get(f'https://mchsrf.ru/region/tag/{i}')
            sleep(1)
            elem = self.driver.find_element_by_name('date_from')
            elem.clear()
            elem.send_keys(date_from)
            elem = self.driver.find_element_by_name('date_to')
            elem.clear()
            elem.send_keys(date_to)
            self.driver.find_element_by_class_name('form-submit').click()
            while True:
                try:
                    self.driver.find_element_by_link_text("Показать еще").click()
                except selenium.common.exceptions.NoSuchElementException:
                    break
                except selenium.common.exceptions.StaleElementReferenceException:
                    sleep(0.1)
            root = bs4.BeautifulSoup(self.driver.page_source, 'lxml')
            urls = ['https://mchsrf.ru' + a.get('href') for a in root.find_all('a', {'class': 'news-title'})]
            for url in urls:
                yield self.get_one_news(url) 

    def close(self):
        self.driver.close()
