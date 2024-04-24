from abc import ABC, abstractmethod
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

import concurrent.futures

from tqdm import tqdm

from utils.utils import init_output_dirs, create_dir, read_file


Base = declarative_base()


class BaseEntity:
    
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    title = Column(String)
    image_url = Column(String)
    content = Column(String)
    url = Column(String)
    category = Column(String)
    author = Column(String)
    sentiment = Column(String)
    is_fake = Column(String)

    def __init__(self, id, title, url, image_url, author, content, created_at, sentiment, is_fake):
        self.id = id
        self.title = title
        self.url = url
        self.image_url = image_url
        self.content = content
        self.author = author
        self.created_at = created_at
        self.sentiment = sentiment
        self.is_fake = is_fake

    def __repr__(self):
        return "<id {}>".format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'image_url': self.image_url,
            'author': self.author,
            'content': self.content,
            'created_at': self.created_at,
            'sentiment': self.sentiment,
            'is_fake': self.is_fake
        }


class Article(BaseEntity):
    def __init__(self, id, title, url, image_url, author, content, created_at, sentiment, is_fake):
        super().__init__(id=id, title=title, image_url=image_url, content=content, url=url, created_at=created_at,
                         author=author, sentiment=sentiment, is_fake=is_fake)


class BaseCrawler(ABC):
    
    
    @abstractmethod
    def extract_content(self, url):
        """
        Extract title, image_url and paragraphs from url
        @param url (str): url to crawl
        @return title (str)
        @return description (generator)
        @return paragraphs (generator)
        """

        title = str()
        description = list()
        content = list()

        return title, content, description

    @abstractmethod
    def write_content(self, url, output_fpath):
        """
        From url, extract title, content and paragraphs then write in output_fpath
        @param url (str): url to crawl
        @param output_fpath (str): file path to save crawled result
        @return (bool): True if crawl successfully and otherwise
        """

        return True

    @abstractmethod
    def get_urls_of_type_thread(self, article_type, page_number, article_child):
        """ " Get urls of articles in a specific type in a page"""

        articles_urls = list()

        return articles_urls

    def start_crawling(self):
        error_urls = list()
        if self.task == "url":
            error_urls = self.crawl_urls(self.urls_fpath, self.output_dpath)
        elif self.task == "type":
            error_urls = self.crawl_types()

        self.logger.info(f"The number of failed URL: {len(error_urls)}")

    def crawl_urls(self, urls_fpath, output_dpath):
        """
        Crawling contents from a list of urls
        Returns:
            list of failed urls
        """
        self.logger.info(f"Start crawling urls from {urls_fpath} file...")
        create_dir(output_dpath)
        urls = list(read_file(urls_fpath))
        num_urls = len(urls)
        # number of digits in an integer
        self.index_len = len(str(num_urls))

        args = ([output_dpath] * num_urls, urls, range(num_urls))
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            results = list(
                tqdm(executor.map(self.crawl_url_thread, *args), total=num_urls, desc="URLs"))

        self.logger.info(
            f"Saving crawling result into {output_dpath} directory...")
        return [result for result in results if result is not None]

    def crawl_url_thread(self, output_dpath, url, index):
        """Crawling content of the specific url"""
        file_index = str(index + 1).zfill(self.index_len)
        output_fpath = "".join([output_dpath, "/url_", file_index, ".txt"])
        is_success = self.write_content(url, output_fpath)
        if not is_success:
            self.logger.debug(f"Crawling unsuccessfully: {url}")
            return url
        else:
            return None

    def crawl_types(self):
        """Crawling contents of a specific type or all types"""
        urls_dpath, results_dpath = init_output_dirs(self.output_dpath)

        if self.article_type == "all":
            error_urls = self.crawl_all_types(urls_dpath, results_dpath)

        else:
            if self.article_child:
                error_urls = self.crawl_type(
                    self.article_type, urls_dpath, results_dpath, self.article_child)
            if not self.article_child:
                error_urls = self.crawl_type(
                    self.article_type, urls_dpath, results_dpath, None)
        return error_urls

    def crawl_type(self, article_type, urls_dpath, results_dpath, article_child):
        if article_child:
            self.logger.info(
                f"Crawl articles child type {article_child} of {article_type}")
            """ " Crawl total_pages of articles in specific type"""
            error_urls = list()

            self.logger.info(f"Getting urls of {article_child}...")
            articles_urls = self.get_urls_of_type(article_type, article_child)
            articles_urls_fpath = "/".join([urls_dpath,
                                           f"{article_child}.txt"])
            with open(articles_urls_fpath, "w") as urls_file:
                urls_file.write("\n".join(articles_urls))
            # crawling urls
            self.logger.info(
                f"Crawling from urls of {article_child} of {article_type}...")
            results_type_dpath = "/".join([results_dpath,
                                          article_type, article_child])
            error_urls = self.crawl_urls(
                articles_urls_fpath, results_type_dpath)

        else:
            self.logger.info(f"Crawl articles type {article_type}")
            error_urls = list()
            # getting urls
            self.logger.info(f"Getting urls of {article_type}...")
            articles_urls = self.get_urls_of_type(article_type, None)
            articles_urls_fpath = "/".join([urls_dpath, f"{article_type}.txt"])
            with open(articles_urls_fpath, "w") as urls_file:
                urls_file.write("\n".join(articles_urls))

            # crawling urls
            self.logger.info(f"Crawling from urls of {article_type}...")
            results_type_dpath = "/".join([results_dpath, article_type])
            error_urls = self.crawl_urls(
                articles_urls_fpath, results_type_dpath)

        return error_urls

    def crawl_all_types(self, urls_dpath, results_dpath):
        """ " Crawl articles from all categories with total_pages per category"""
        total_error_urls = list()

        num_types = len(self.article_type_dict)
        for i in range(num_types):
            article_type = self.article_type_dict[i]
            error_urls = self.crawl_type(
                article_type, urls_dpath, results_dpath)
            self.logger.info(
                f"The number of failed {article_type} URL: {len(error_urls)}")
            self.logger.info("-" * 79)
            total_error_urls.extend(error_urls)

        return total_error_urls

    def get_urls_of_type(self, article_type, article_child):
        """ " Get urls of articles in a specific type"""
        articles_urls = list()
        if article_child:

            args = ([article_type] * self.total_pages, range(1,
                    self.total_pages + 1), [article_child] * self.total_pages)

        else:
            args = ([article_type] * self.total_pages,
                    range(1, self.total_pages + 1), [None] * self.total_pages)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            results = list(tqdm(executor.map(
                self.get_urls_of_type_thread, *args), total=self.total_pages, desc="Pages"))

        articles_urls = sum(results, [])
        articles_urls = list(set(articles_urls))

        return articles_urls
