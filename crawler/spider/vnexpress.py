from datetime import datetime
import requests
import sys
from pathlib import Path
from crawler.spider.connectsql import connect_to_sqlite, is_url_exists, insert_article
from bs4 import BeautifulSoup
import sqlite3
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
from logger import log
from crawler.spider.base_crawler import Article, BaseCrawler
from utils.bs4_utils import get_text_from_tag


class VNExpressCrawler(BaseCrawler):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = log.get_logger(name=__name__)
        self.article_type_dict = {
            0: "thoi-su",
            1: "du-lich",
            2: "the-gioi",
            3: "kinh-doanh",
            4: "khoa-hoc",
            5: "giai-tri",
            6: "the-thao",
            7: "phap-luat",
            8: "giao-duc",
            9: "suc-khoe",
            10: "doi-song"
        }
        self.article_child_dict ={
            0: "chinh-tri",
            1: "dan-sinh",
            2: "lao-dong-viec-lam",
            3: "giao-thong"
        }  

    def extract_content(self, url: str) -> tuple:
        """
        Extract title, author and content from url
        @param url (str): url to crawl
        @return title (str)
        @return author (generator)
        @return content (generator)
        """
        content = requests.get(url).content
        soup = BeautifulSoup(content, "html.parser")

        title = soup.find("h1", class_="title-detail") 
        if title == None:
            return None, None, None
        
        title = title.text

        # some sport news have location-stamp child tag inside author tag
        author = (get_text_from_tag(p) for p in soup.find("p", class_="description").contents)
        content = (get_text_from_tag(p) for p in soup.find_all("p", class_="Normal"))

        return title, author, content

    def write_content(self, url: str, output_fpath: str) -> bool:
        """
        From url, extract title, author and content then write in output_fpath
        @param url (str): url to crawl
        @param output_fpath (str): file path to save crawled result
        @return (bool): True if crawl successfully and otherwise
        """
        title, author, content = self.extract_content(url)

        
        
        article = Article(id=None,title='\n'.join(title), url=url, image_url="", author='\n'.join(
            author), content='\n'.join(content), created_at=datetime.now(), sentiment="", is_fake=False)
        connect_sql = connect_to_sqlite(database_file="osintnews.db")
        
        
        if not is_url_exists(connect_sql, article.url):
            if title == None:
                return False
            with open(output_fpath, "w", encoding="utf-8") as file:
                file.write(title + "\n")
                for p in author:
                    file.write(p + "\n")
                for p in content:                     
                    file.write(p + "\n")
        # Insert the article into the database
            insert_article(connect_sql, article)
        
        return True

    def get_urls_of_type_thread(self, article_type, page_number, article_child):
        """" Get urls of articles in a specific type in a page"""
        if article_child:
            page_url = f"https://vnexpress.net/{article_type}/{article_child}-p{page_number}"
        else:
            page_url = f"https://vnexpress.net/{article_type}-p{page_number}"
        content = requests.get(page_url).content
        soup = BeautifulSoup(content, "html.parser")
        titles = soup.find_all(class_="title-news")

        # if (len(titles) == 0):
        #     self.logger.info(f"Couldn't find any news in {page_url} \nMaybe you sent too many requests, try using less workers")
            
        # articles_urls = list()
        
        # for title in titles:
        #     link = title.find_all("a")[0]
        #     articles_urls.append(link.get("href"))

        if (len(titles) == 0):
            self.logger.info(f"Couldn't find any news in {page_url} \nMaybe you sent too many requests, try using less workers")
            return []
        articles_urls = []

        for title in titles:
            links = title.find_all("a")
            if links:
                link = links[0]
                articles_urls.append(link.get("href"))
        return articles_urls
    