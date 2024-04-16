#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import DateTime
from datetime import datetime
import collections
collections.Callable = collections.abc.Callable


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# with app.app_context():
#   now = datetime.now()
#   future_shows = db.session.query(shows).filter(shows.c.start_time > now)
#   past_shows = db.session.query(shows).filter(shows.c.start_time <= now)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

venue_genres = db.Table('VenueGenre',
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('genres_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
)

artist_genres = db.Table('ArtistGenre',
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
    db.Column('genres_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.relationship('Genres', secondary=venue_genres,
                             backref=db.backref('venues', lazy='select'))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)
    
    def past_shows(self):
      return [show for show in self.shows if show.start_time < datetime.now()]
        
    def upcoming_shows(self):
      return [show for show in self.shows if show.start_time > datetime.now()]
    
    def past_shows_count(self):
       return sum(1 for show in self.shows if show.start_time < datetime.now())
        
    def upcoming_shows_count(self):
       return sum(1 for show in self.shows if show.start_time > datetime.now())  
    
    def to_data(self):
      data = {
            "id": self.id,
            "name": self.name,
            "genres": [genre.name for genre in self.genres], 
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": [],
            "upcoming_shows": [],
            "past_shows_count": self.past_shows_count(),
            "upcoming_shows_count": self.upcoming_shows_count()         
        }

      upcoming_show_list = self.upcoming_shows()
      for show in upcoming_show_list:
        artist = Artist.query.get(show.artist_id)
        data['upcoming_shows'].append({
                  "artist_id": artist.id,
                  "artist_name": artist.name,
                  "artist_image_link": artist.image_link,
                  "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
              })
        
      past_show_list = self.past_shows()
      for show in past_show_list:
        artist = Artist.query.get(show.artist_id)
        data['past_shows'].append({
                  "artist_id": artist.id,
                  "artist_name": artist.name,
                  "artist_image_link": artist.image_link,
                  "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
              })
      return data



class Genres(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)




class Show(db.Model):
   __tablename__ = 'Show'
   id = db.Column(db.Integer, primary_key=True)
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
   start_time = db.Column(db.DateTime)
  


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.relationship('Genres', secondary=artist_genres,
      backref=db.backref('Artist', lazy=True))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)
    
    def past_shows(self):
      return [show for show in self.shows if show.start_time < datetime.now()]
        
    def upcoming_shows(self):
      return [show for show in self.shows if show.start_time > datetime.now()]
    
    def past_shows_count(self):
       return sum(1 for show in self.shows if show.start_time < datetime.now())
        
    def upcoming_shows_count(self):
       return sum(1 for show in self.shows if show.start_time > datetime.now())  
    
    def to_data(self):
      data = {
            "id": self.id,
            "name": self.name,
            "genres": [genre.name for genre in self.genres], 
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": [],
            "upcoming_shows": [],
            "past_shows_count": self.past_shows_count(),
            "upcoming_shows_count": self.upcoming_shows_count()         
        }

      upcoming_show_list = self.upcoming_shows()
      for show in upcoming_show_list:
        venue = Venue.query.get(show.venue_id)
        data['upcoming_shows'].append({
                  "venue_id": venue.id,
                  "venue_name": venue.name,
                  "venue_image_link": venue.image_link,
                  "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
              })
        
      past_show_list = self.past_shows()
      for show in past_show_list:
        venue = Venue.query.get(show.venue_id)
        data['past_shows'].append({
                  "venue_id": venue.id,
                  "venue_name": venue.name,
                  "venue_image_link": venue.image_link,
                  "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
              })
      return data

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

@app.route('/venues')
def venues():

   # Query all venues and their shows, grouped by city and state
  venue_list = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
  data = []


  for venue in venue_list:
      area_exists = False
      for area in data:
          if area['city'] == venue.city and area['state'] == venue.state:
              area_exists = True
              break
      
      if not area_exists:
          data.append({
              "city": venue.city,
              "state": venue.state,
              "venues": []
          })
      
      for area in data:
          if area['city'] == venue.city and area['state'] == venue.state:
              area['venues'].append({
                  "id": venue.id,
                  "name": venue.name,
                  "num_upcoming_shows": venue.upcoming_shows_count()
              })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')

  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  count = len(venues)
  response={
    "count": count,
    "data": []
  }
  data = []
  for venue in venues:
     response['data'].append({
                  "id": venue.id,
                  "name": venue.name,
                  "num_upcoming_shows": venue.upcoming_shows_count()
              })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  if not venue:
            flash('Venue not found.', 'error')
            return redirect('/') 
  data = venue.to_data()
 
  return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  venue = Venue.query.get(venue_id)
  try:
    # Update venue
    venue.name = request.form.get('name', '')
    venue.address = request.form.get('address', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.phone = request.form.get('phone', '')
    venue.website = request.form.get('website', '')
    venue.facebook_link = request.form.get('facebook_link', '')
    venue.seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
    venue.seeking_description = request.form.get('seeking_description', '')
    venue.image_link = request.form.get('image_link', '')

    # Remove the exixting genres
    venue.genres.clear()

    # Update the genres for the venue
    genres_list =  request.form.getlist('genres')
    for genre_item in genres_list:
       genre = Genres.query.get(genre_item)
       venue.genres.append(genre)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' +  request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
    venue = Venue(name = request.form.get('name', ''))
    venue.address = request.form.get('address', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.phone = request.form.get('phone', '')
    venue.website = request.form.get('website', '')
    venue.facebook_link = request.form.get('facebook_link', '')
    venue.seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
    venue.seeking_description = request.form.get('seeking_description', '')
    venue.image_link = request.form.get('image_link ', '')

    # Insert the genres for the venue
    genres_list =  request.form.getlist('genres')
    for genre_item in genres_list:
       genre = Genres.query.get(genre_item)
       venue.genres.append(genre)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' +  request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    # Delete a venue
    venue = Venue.query.get(venue_id)
    if not venue:
            flash('Venue not found.', 'error')
            return redirect('/') 

   
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' +  venue.name + ' could not be deleted.')
  finally:
    db.session.close()

  return 200

@app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def deleted_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if not venue:
    flash('Venue was successfully deleted!')
    return redirect('/') 
  else:
    return redirect(f'/venues/{venue_id}')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = []
  artists = Artist.query.all()
  for artist in artists: 
     data.append({
              "id": artist.id,
              "name": artist.name
          })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])

def search_artists():
 
  search_term = request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  count = len(artists)
  response={
    "count": count,
    "data": []
  }
  for artist in artists:
     response['data'].append({
                  "id": artist.id,
                  "name": artist.name,
                  "num_upcoming_shows": artist.upcoming_shows_count()
              })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 
  artist = Artist.query.get(artist_id)
  data = artist.to_data()

  return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.website = request.form.get('website', '')
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
    artist.seeking_description = request.form.get('seeking_description', '')
    artist.image_link = request.form.get('image_link', '')

    # Remove the exixting genres
    artist.genres.clear()

    # Update the genres for the artist
    genres_list =  request.form.getlist('genres')
    for genre_item in genres_list:
       genre = Genres.query.get(genre_item)
       artist.genres.append(genre)
    db.session.commit()
    flash('Arist ' + artist.name + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' +  request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  try:
    artist = Artist(name = request.form.get('name', ''))
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.website = request.form.get('website', '')
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
    artist.seeking_description = request.form.get('seeking_description', '')
    artist.image_link = request.form.get('image_link ', '')

    # Insert the genres for the venue
    genres_list =  request.form.getlist('genres')
    for genre_item in genres_list:
       genre = Genres.query.get(genre_item)
       artist.genres.append(genre)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' +  request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []
  shows = Show.query.all()
  for show in shows:
     venue = Venue.query.get(show.venue_id) 
     artist = Artist.query.get(show.artist_id)
     data.append({
              "venue_id": venue.id,
              "venue_name": venue.name,
              "artist_id": artist.id,
              "artist_name": artist.name,
              "artist_image_link": artist.image_link,
              "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
          })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    show = Show()
    show.artist_id = request.form.get('artist_id')
    show.venue_id = request.form.get('venue_id')
    show.start_time = request.form.get("start_time")

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


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

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
