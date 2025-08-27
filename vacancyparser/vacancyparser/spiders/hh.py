import time
import scrapy
from scrapy.http import HtmlResponse
from fake_useragent import UserAgent
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ua = UserAgent()
        self.search_url = f"https://hh.ru/search/vacancy?text=Analyst"

    def start_requests(self):              
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"user-agent={self.ua.random}")
        self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.get(self.search_url)
        self.scroll_page()
        
        html = self.driver.page_source
        self.driver.quit()
        
        response = HtmlResponse(url=self.search_url, body=html.encode('utf-8'), encoding='utf-8')

        for item in self.parse(response):
            yield item

    def scroll_page(self):
        initial_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[class="vacancy-card--n77Dj8TY8VIUF0yM font-inter"]'))
        scrolls_count = 2

        for i in range(scrolls_count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(2)
            
            current_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div[class="vacancy-card--n77Dj8TY8VIUF0yM font-inter"]'))
            
            if current_count == initial_count and i > 0:
                break
                
            initial_count = current_count

    def parse(self, response):
        vacancies = response.css('div[class="vacancy-card--n77Dj8TY8VIUF0yM font-inter"]')

        for vacancy in vacancies:
            link = vacancy.css('a[data-qa="serp-item__title"]::attr(href)').get()

            vacancy_data = {
                'title': vacancy.css('span[data-qa="serp-item__title-text"]::text').get(),
                'salary': (
                    None
                    if (salary_text := vacancy.css('span[class="magritte-text___pbpft_3-0-32 magritte-text_style-primary___AQ7MW_3-0-32 magritte-text_typography-label-1-regular___pi3R-_3-0-32"]::text').get()) is None 
                    or len(salary_text.strip()) < 4 
                    else salary_text.replace('\u202f', ' ').replace('\xa0', ' ').strip()
                ),
                'company': vacancy.xpath('string(.//span[@data-qa="vacancy-serp__vacancy-employer-text"])').get(),
                'rating': vacancy.css('div[class="magritte-text___pbpft_3-0-32 magritte-text_style-primary___AQ7MW_3-0-32 magritte-text_typography-label-4-regular___E5l2b_3-0-32"]::text').get(),
                'city': vacancy.css('span[data-qa="vacancy-serp__vacancy-address"]::text').get() or None,
                'experience': vacancy.css('span[data-qa*="experience"]::text').get('').strip(),
                'remote': 'Да' if vacancy.css('span[data-qa*="remote"]') else None,
                'link': link
            }

            yield vacancy_data

        for page_url in self.get_pagination_links(response):
            yield scrapy.Request(
                url=page_url,
                callback=self.parse,
                headers={'User-Agent': self.ua.random}
            )


    def get_pagination_links(self, response):
        pagination_links = response.css('[data-qa="pager-page"]::attr(href)').getall()
        next_page = response.css('[data-qa="pager-next"]::attr(href)').get()
        
        if next_page:
            pagination_links.append(next_page)
        
        return [urljoin(response.url, link) for link in pagination_links]