#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (Flask, render_template, request, 
                    Response, flash, redirect, url_for,
                    jsonify)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from config import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
# Use the Venue model to generate venue object obtained from
# the Venue model
      

def create_venue_submission():
      form= VenueForm()
      if not form.validate():
            flash(f'Venue could not be registered! \
                   Phone field must be numbers in format xxx-xxx-xxxx')
            return redirect(url_for('create_venue_submission'))
      try:
        venue = Venue(
                      name= request.form.get('name'),
                      city= request.form.get('city'),
                      state= request.form.get('state'),
                      address= request.form.get('address'),
                      phone= request.form.get('phone'),
                      genres= ','.join(request.form.getlist('genres')),
                      image_link= request.form.get('image_link'),
                      facebook_link= request.form.get('facebook_link'),
                      website= request.form.get('website'),
                      seeking_talent = bool(request.form.get('seeking_talent')),
                      seeking_description = request.form.get('seeking_description')
                    )
        venue.insert()
        # message after successful entry
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

      except:
        # message after failed attempt and rollback so that the record is not
        # listed
        db.session.rollback()
        error = True
        flash('An error occurred. Venue ' + request.form['name']  + ' could not be listed.')
        abort(500)
  
      finally:
        #close session
        db.session.close()
      return render_template('pages/home.html')

#  Show Venues
#  ----------------------------------------------------------------------  
@app.route('/venues')
def venues():
  # this function list all the values
  places = set()
  venues = Venue.query.all()
  for venue in venues:
        # lists unique city and state combination as a tuple
        places.add((venue.city, venue.state))
  data =[]
  for place in places:
        # append all the unique city and state combinations
            data.append({'city': place[0],
                          'state': place[1],
                          'venues': []})
  
  for venue in venues:
        num_upcoming_shows = 0
        current_time = datetime.now()

        # find all the shows for a venue
        shows = Shows.query.filter(Shows.venue_id == venue.id and Shows.start_time > current_time).all()

        if shows is None:
              abort(404)

                      
        for item in data:
              if item['city'] == venue.city and item['state'] == venue.state:
                    item['venues'].append({ 'id': venue.id,
                                            'name': venue.name,
                                          })

  return render_template('pages/venues.html', areas=data)

# Show the venue page
# -------------------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first_or_404()

  if venue is None:
        abort(404)

  # get all the shows in the venue with the venue_id
  # by joining the Shows table with the Artist table
  # and filter the artist by venue id
  venue_shows = db.session.query(Shows).order_by(Shows.start_time).\
                join(Artist).filter(Shows.venue_id == venue_id).all()
  upcoming_shows=[]
  past_shows=[]
  

  for show in venue_shows:
        print(show.start_time)
        artist = db.session.query(Artist).filter(show.artist_id == Artist.id).first()

        # get all the needed show data
        show_add = {"artist_id": show.artist_id,
                    "artist_name": artist.name,
                    "artist_image_link":artist.image_link,
                    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")}
        
        # decide if it is a past show or an upcoming show
        if show.start_time < datetime.now():
              past_shows.append(show_add)
        else:
              upcoming_shows.append(show_add)
  
  
  data = venue.details()
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

# Search a Venue
# ------------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  data = []
  # lower the search term to make it case insensitive
  search_term = request.form.get('search_term').lower()

  # seach the venues with the search term and limit it to 10
  # using ilike make it case insensetive
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).limit(10).all()

  for venue in venues:
        upcomng_shows =  Shows.query.filter(Shows.venue_id == venue.id).filter(Shows.start_time > datetime.now()).all()
        data.append({'id':venue.id,
                      'name': venue.name,
                      'num_upcoming_shows': len(upcomng_shows) })
        
  response = { "count": len(venues),
               "data": data}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term'))
# Edit venues
# --------------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
      # pre-populate the data in the edit form
      # so that the user does not need to re-enter all the data
      # and can modify just the necessary field from the existing data
      venue = Venue.query.get_or_404(venue_id)
      form = VenueForm()
      form.name.data = venue.name
      form.city.data = venue.city 
      form.state.data = venue.state  
      form.address.data = venue.address 
      form.phone.data = venue.phone 
      form.genres.data = venue.genres
      form.facebook_link.data = venue.facebook_link
      form.website.data = venue.website
      form.image_link.data = venue.image_link
      form.seeking_talent.data = venue.seeking_talent 
      form.seeking_description.data = venue.seeking_description
      return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    if venue is none:
          abort(404)
    form = VenueForm()


    if not form.validate():
        flash(f'Venue could not be updated! \
                   Phone field must be numbers in format xxx-xxx-xxxx')
        return redirect(url_for('edit_venue_submission', venue_id=venue_id))

    else:
        error=False
        try:
          venue.name = form.name.data 
          venue.city = form.city.data 
          venue.address = form.address.data
          venue.phone = form.phone.data 
          venue.genres = ','.join(form.genres.data)
          venue.facebook_link = form.facebook_link.data 
          venue.website= form.website.data 
          venue.image_link= form.image_link.data
          venue.seeking_talent = form.seeking_talent.data 
          venue.seeking_description = form.seeking_description.data 
          venue.update()
          
        except: 
          error=True
          db.session.rollback()
          print(sys.exc_info())
          

        finally:
          db.session.close()

        if error:
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
            abort(500)
            
        if not error:
            # on successful db update, flash success
            flash('Venue ' + request.form['name'] + ' was successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue_id))
          
   

# Delete Venues
# -------------------------------------------------------------------------------
@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):
    error = False
    venue = Venue.query.get_or_404(venue_id)
    try: 
      venue.delete()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()

    if error:
        flash('An error occurred. Venue' +  ' could not be deleted.')
    if not error:
        flash('Venue' +' was successfully deleted!')

    return redirect(url_for('venues'))



#  Artists
#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
      form= ArtistForm()
      if not form.validate():
            flash(f'Artist could not be registered! \
                   Phone field must be numbers in format xxx-xxx-xxxx')
            return redirect(url_for('create_artist_submission'))
      
      try:
        artist = Artist(name=request.form.get('name'),
                        city=request.form.get('city'),
                        state=request.form.get('state'),
                        phone=request.form.get('phone'),
                        genres=','.join(request.form.getlist('genres')),
                        image_link=request.form.get('image_link'),
                        facebook_link=request.form.get('facebook_link'),
                        website=request.form.get('website'),
                        seeking_venue = bool(request.form.get('seeking_venue')),
                        seeking_description = request.form.get('seeking_description')
                      
                      )
             

        artist.insert()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        
      except:
        db.session.rollback()
        error = True
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())

      finally:
        db.session.close()

      return render_template('pages/home.html')

# Show all Artists
@app.route('/artists')
def artists():
  data = []
  artists = db.session.query(Artist).distinct(Artist.name).all()
  if artists is None:
        abort(404)

  for artist in artists: 
      artist_data = {
                    'id': artist.id,
                    'name': artist.name
                    }
      data.append(artist_data)

  return render_template('pages/artists.html', artists=data)

  #  Show an individual Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first_or_404()
  # Join the Shows and Artist table and filter by the artist_it to get 
  # all the shows for the specific artist with the artist id
  artist_shows = db.session.query(Shows).order_by(Shows.start_time).\
                join(Artist).filter(Shows.artist_id == artist_id).all()
  
  upcoming_shows = []
  past_shows=[]
  
  for show in artist_shows:
        # get all the venues for the artist with the artist_id
        venue = db.session.query(Venue).filter(show.venue_id == Venue.id).first_or_404()

        # all the venue data
        venue_data = {"venue_id": show.venue_id,
                        "venue_name":venue.name,
                        "venue_image_link":venue.image_link,
                        "start_time":show.start_time.strftime("%m/%d/%Y, %H:%M")
                        }

        # decide whether to add the data in the past or upcoming shows
        if show.start_time < datetime.now():
            past_shows.append(venue_data)

        else:
            upcoming_shows.append(venue_data)


  data = artist.details() 
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows) 
  return render_template('pages/show_artist.html', artist=data)

# Search Artists
@app.route('/artists/search', methods=['POST'])
def search_artists():

  data = []
  # get the search term and make it lower case 
  # 
  search_term = request.form.get('search_term').lower()
  # searh all the artist to get the artist(s) with the search term
  # using ilike to make it case insensitive and limit the result to 10 
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).distinct(Artist.name).limit(10).all()

  for artist in artists:
        data.append({
          'id': artist.id,
          'name': artist.name})
      
  response = {
          "count": len(artists),
          "data": data}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term'))


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
      # pre-populate the data in the edit form
      # so that the user does not need to re-enter the data
      # and can modify the existing data
      artist = Artist.query.get_or_404(artist_id)
      form = ArtistForm()
      form.name.data = artist.name
      form.city.data = artist.city 
      form.state.data = artist.state  
      form.phone.data = artist.phone 
      form.genres.data = artist.genres
      form.facebook_link.data = artist.facebook_link
      form.website.data = artist.website
      form.image_link.data = artist.image_link
      form.seeking_venue.data = artist.seeking_venue
      form.seeking_description.data = artist.seeking_description 
      return render_template('forms/edit_artist.html', form=form, artist=artist)
      
      
      
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm()
    error = False
    
    if not form.validate():
          flash(f'Artist information could not be updated! \
                   Phone field must be numbers in format xxx-xxx-xxxx')

          return redirect(url_for('edit_artist_submission', artist_id=artist_id))

    else:
        
        try:
          # get the user input from the edit form
          artist.name = form.name.data 
          artist.city = form.city.data 
          artist.state = form.state.data
          artist.phone = form.phone.data 
          artist.genres = ','.join(form.genres.data)
          artist.facebook_link = form.facebook_link.data 
          artist.website= form.website.data 
          artist.image_link= form.image_link.data
          artist.seeking_venue = form.seeking_venue.data 
          artist.seeking_description = form.seeking_description.data 
          artist.update()
        
        except:
          error=True
          db.session.rollback()
          print(sys.exc_info())

        finally:
          db.session.close()

        
        if error:
          flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
          abort(500)
          
        if not error:
          # on successful db update, flash success
          flash('Artist ' + request.form['name'] + ' was successfully updated!')
          return redirect(url_for('show_artist', artist_id=artist_id))



#  Shows
#  ----------------------------------------------------------------

# Create a Show
# --------------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
      if request.method == "POST":
        try:
    
          shows = Shows( artist_id = request.form['artist_id'],
                        venue_id = request.form['venue_id'],
                        start_time = request.form['start_time'])

          shows.insert()
          # on successful db insert, flash success
          flash('Show was successfully listed!')

        except:
          db.session.rollback()
          error = True
          flash('An error occurred. Show could not be listed.')
          print(sys.exc_info())

  
        finally:
          db.session.close()
      return render_template('pages/home.html')

# Show all record of shows
# ----------------------------------------------------------------
@app.route('/shows')
def shows():
  
    shows = Shows.query.order_by(Shows.start_time).all()

    data=[]
    
    for show in shows:
        # all the venues for shows
        venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
        # all the artist for shows
        artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
        data.append(
                    {"venue_id": show.venue_id,
                      "venue_name": venue.name,
                      "artist_id": show.artist_id,
                      "artist_name": artist.name,
                      "artist_image_link":artist.image_link,
                      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
                      }
                    )
    return render_template('pages/shows.html', shows=data)


# error handlers

@app.errorhandler(404)
def not_found_error(error):
      return jsonify({
            "success":False,
            "error": 404,
            "message": "resource not found"
        }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
            "success":False,
            "error": 500,
            "message": "internal server error"
        }), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()


