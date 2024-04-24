import argparse

from logger import log
from utils import utils
from crawler.spider.factory import get_crawler
from crawler.spider.connectsql import connect_to_sqlite, insert_article


def main(config_fpath):
    config = utils.get_config(config_fpath)
    log.setup_logging(log_dir=config["output_dpath"],
                      config_fpath=config["logger_fpath"])
    crawler = get_crawler(**config)
    crawler.start_crawling()


if __name__ == "__main__":
    database_file = "osintnews.db"
    connection = connect_to_sqlite(database_file)
    # if connection:
    #     # Định nghĩa một lớp Article hoặc sử dụng namedtuple hoặc bất kỳ cấu trúc dữ liệu nào bạn muốn để biểu diễn một bài báo
    #     class Article:
    #         def __init__(self, id, title, url, image_url, author, content, created_at, sentiment, is_fake):
    #             self.id = id
    #             self.title = title
    #             self.url = url
    #             self.image_url = image_url
    #             self.author = author
    #             self.content = content
    #             self.created_at = created_at
    #             self.sentiment = sentiment
    #             self.is_fake = is_fake
    parser = argparse.ArgumentParser(
        description="Vietnamese News crawler (with url/type)")
    parser.add_argument("--config",
                        default="crawler_config.yml",
                        help="path to config file",
                        dest="config_fpath")
    args = parser.parse_args()
    main(**vars(args))
