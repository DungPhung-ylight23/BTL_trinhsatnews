from .vnexpress import VNExpressCrawler
from .dantri import DanTriCrawler
from .vietnamnet import VietNamNetCrawler
from .viettan import VietTanCrawler
WEBNAMES = {"vnexpress": VNExpressCrawler,
            "dantri": DanTriCrawler,
            "vietnamnet": VietNamNetCrawler,
            "viettan": VietTanCrawler}

def get_crawler(webname, **kwargs):
    crawler = WEBNAMES[webname](**kwargs)
    return crawler