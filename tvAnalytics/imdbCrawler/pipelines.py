from sqlalchemy.orm import sessionmaker
from models import imdbItem,db_connect,create_imdbItem_table

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class imdbItemPipeline(object):
	def __init__(self):
		engine = db_connect()
		create_imdbItem_table(engine)
		self.Session = sessionmaker(bind=engine)

	def process_item(self, item, spider):
		session = self.Session()
		imdbCrawler = imdbItem(**item)
		session.add(imdbCrawler)
		session.commit()
		return item