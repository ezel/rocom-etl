from etl import ETLer
from crawl import BiliCrawler

#FILE_PATH = 'rat/public/data/tables/'
FILE_PATH = 'rat/public/data/BinData/'

e = ETLer(root=FILE_PATH)
#e.export_color_html()
e.load_sqlite()

#c = BiliCrawler('data/tmp.pkl')
#c.test()
