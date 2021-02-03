import dateutil.parser
import babel
from config import *
from config import app, db



class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Shows', backref = 'venue', cascade='all, delete', lazy=True)

    def details(self):
        return {

            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "phone": self.phone,
            "genres": self.genres.split(','),
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "seeking_talent": self.seeking_talent,  
            "seeking_description": self.seeking_description
            }
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Shows', backref = 'artist', cascade='all, delete', lazy=True)

    def details(self):
        return {

            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "genres": self.genres.split(','),
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "seeking_venue": self.seeking_venue,  
            "seeking_description": self.seeking_description
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

           
    

class Shows(db.Model):
    __tablename__ = 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()



