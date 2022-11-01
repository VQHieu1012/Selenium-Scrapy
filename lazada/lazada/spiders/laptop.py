from requests import request
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from shutil import which



def get_headers(s, sep=': ', strip_cookie=True, strip_cl=True, strip_headers: list = []) -> dict():
    d = dict()
    for kv in s.split('\n'):
        kv = kv.strip()
        if kv and sep in kv:
            v = ''
            k = kv.split(sep)[0]
            if len(kv.split(sep)) == 1:
                v = ''
            else:
                v = kv.split(sep)[1]
            if v == '\'\'':
                v = ''
            # v = kv.split(sep)[1]
            if strip_cookie and k.lower() == 'cookie':
                continue
            if strip_cl and k.lower() == 'content-length':
                continue
            if k in strip_headers:
                continue
            d[k] = v
    return d


class LaptopSpider(scrapy.Spider):
    name = 'laptop'

    def start_requests(self):
        # copy link --> private window --> network --> click --> get_header--> copy except :
        h = get_headers('''
        accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        accept-encoding: gzip, deflate, br
        accept-language: en-US,en;q=0.9
        sec-ch-ua: "Not-A.Brand";v="99", "Opera";v="91", "Chromium";v="105"
        sec-ch-ua-mobile: ?0
        sec-ch-ua-platform: "Windows"
        sec-fetch-dest: document
        sec-fetch-mode: navigate
        sec-fetch-site: none
        sec-fetch-user: ?1
        upgrade-insecure-requests: 1
        user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.77''')
       
        chrome_path = which("chromedriver")
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(executable_path=chrome_path, options=options)

        for i in range(1, 100):
            driver.get(f'https://www.lazada.com.ph/shop-laptops/?page={i}')
            
            products = driver.find_elements(By.XPATH, "//div[@class='ant-col ant-col-20 ant-col-push-4 Jv5R8']//div[@data-qa-locator='general-products']/div/div/div/div[2]/div[2]/a")
            for product in products:
                #link_elements = driver.find_elements(By.XPATH, '//*[@data-qa-locator="product-item"]//a/@href')
                yield scrapy.Request(product.get_attribute('href'), callback=self.parse, headers=h)
                
        driver.quit()  

    def parse(self, response):
        yield {
            'name': response.xpath("//h1/text()").get(),
            'price': response.xpath("//span[@class='pdp-price pdp-price_type_normal pdp-price_color_orange pdp-price_size_xl']/text()").get()
        }

