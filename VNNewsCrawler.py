import argparse

from logger import log
from utils import utils
from crawler.spider.factory import get_crawler
from crawler.spider.connectsql import get_connection, insert_article

def main(config_fpath):
    config = utils.get_config(config_fpath)
    log.setup_logging(log_dir=config["output_dpath"], 
                      config_fpath=config["logger_fpath"])
    crawler = get_crawler(**config)
    crawler.start_crawling()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vietnamese News crawler (with url/type)")
    parser.add_argument("--config", 
                        default="crawler_config.yml", 
                        help="path to config file",
                        dest="config_fpath") 
    args = parser.parse_args()
    main(**vars(args))