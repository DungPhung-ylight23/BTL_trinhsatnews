import requests
import sys
from pathlib import Path

from bs4 import BeautifulSoup

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from logger import log
from crawler.spider.base_crawler import BaseCrawler
from utils.bs4_utils import get_text_from_tag


class VietTanCrawler(BaseCrawler):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = log.get_logger(name=__name__)
        self.article_type_dict = {
            0: "thoi-su",
            1: "quan-diem",
            2: "dien-dan",
            3: "hoat-dong-cua-viet-tan",
            4: "thong-bao",
            
        }

    def extract_content(self, url: str) -> tuple:
        """
        Extract title, author and paragraphs from url
        @param url (str): url to crawl
        @return title (str)
        @return author (generator)
        @return paragraphs (generator)
        """
        content = requests.get(url).content
        soup = BeautifulSoup(content, "html.parser")

        title = soup.find("h1", class_="elementor-heading-title elementor-size-default")
        if title == None:
            return None, None, None
        title = title.text

        author = (get_text_from_tag(p) for p in soup.find("span",class_="elementor-icon-list-text elementor-post-info__item elementor-post-info__item--type-author").contents)
        paragraphs = []
        divs = soup.find_all("div", class_="elementor-widget-container")
        for div in divs:
            paragraphs = (get_text_from_tag(p) for p in soup.find_all("p"))
        return title, author, paragraphs
    def write_content(self, url: str, output_fpath: str) -> bool:
        """
        From url, extract title, author and paragraphs then write in output_fpath
        @param url (str): url to crawl
        @param output_fpath (str): file path to save crawled result
        @return (bool): True if crawl successfully and otherwise
        """
        title, author, paragraphs = self.extract_content(url)

        if title == None:
            return False

        with open(output_fpath, "w", encoding="utf-8") as file:
            file.write(title + "\n")
            for p in author:
                file.write(p + "\n")
            for p in paragraphs:
                file.write(p + "\n")

        return True

    def get_urls_of_type_thread(self, article_type, page_number):
        """ " Get urls of articles in a specific type in a page"""
        page_url = f"https://viettan.org/{article_type}/page/{page_number}/"
        content = requests.get(page_url).content
        soup = BeautifulSoup(content, "html.parser")
        titles = soup.find_all(class_="elementor-post__title")

        if len(titles) == 0:
            self.logger.info(
                f"Couldn't find any news in {page_url} \nMaybe you sent too many requests, try using less workers"
            )

        articles_urls = list()

        for title in titles:
            link = title.find_all("a")[0]
            articles_urls.append(link.get("href"))

        return articles_urls
