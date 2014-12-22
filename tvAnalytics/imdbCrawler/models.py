from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings
 
DeclarativeBase = declarative_base()
 
def db_connect():
	return create_engine(URL(**settings.DATABASE),echo=True)
 
def create_imdbItem_table(engine):
    DeclarativeBase.metadata.create_all(engine)
 
class imdbItem(DeclarativeBase):
    __tablename__ = "imdbCrawler"
 
    id = Column(Integer, primary_key=True)
    showName = Column('showName', String(400))
    link = Column('link', String(200))
    seriesRating = Column('seriesRating',Float)
    episode = Column('episode',String(100))
    episodeRating = Column('episodeRating',Float)
    votes = Column('votes',Integer)
    genre = Column('genre',String(100))
    director = Column('director',String(100))
    airDate = Column('airDate',String(100))
    videoLink = Column('videoLink',String(100))