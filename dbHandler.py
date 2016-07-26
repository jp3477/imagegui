# dbHandler.py
# Contains functions to interact with image database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from makedb import Base, Location, Image
from imagegui import DBSESSION

def start_session(db_name):

    
    DBSESSION.configure(bind=create_engine('sqlite:///' + db_name))
    session = DBSESSION()
    
    return session

def addImage(name, session):
    image = Image(name=name)
    session.add(image)
    session.commit()

def addLocation(x, y, type, image, session):
    location = Location(x=x, y=y, type=type, image=image)
    session.add(location)
    session.commit()

def getAllImages(session):
    return session.query(Image).all()

def getAllLocations(session):
    return session.query(Location).all()

def getImageByName(name, session):
    return session.query(Image).filter(Image.name == name).one_or_none()

def getLocationsByImage(image, session):
    return session.query(Location).filter(Location.image == image).all()

def getImageLocationByType(image, type, session):
    return session.query(Location).filter(Location.image == image, Location.type == type).one_or_none()





    
