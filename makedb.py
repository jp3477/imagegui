# makedb.py
# Creates an database that stores an image name and corresponding location of clicks
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    type = Column(String, nullable=False)

    image_id = Column(Integer, ForeignKey('image.id'), nullable=False)
    image = relationship(Image)


engine = create_engine("sqlite:///image_location.db")
Base.metadata.create_all(engine)
