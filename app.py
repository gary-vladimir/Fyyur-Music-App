# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from models import db, Venue, Artist, Show

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
csrf = CSRFProtect(app)
moment = Moment(app)
app.config.from_object("config")
db.init_app(app)
migrate = Migrate(app, db)


@app.context_processor
def inject_search_form():
    return dict(search_form=SearchForm())


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # Getting all of the individual venues sorted
    venues = Venue.query.order_by(Venue.city, Venue.state, Venue.id.desc()).all()

    # Separating venues into their respective city and state.
    city_state_dict = {}
    for venue in venues:
        city_state = (venue.city, venue.state)
        if city_state not in city_state_dict:
            city_state_dict[city_state] = []

        city_state_dict[city_state].append(
            {
                "id": venue.id,
                "name": venue.name,
            }
        )

    # Added data with correct format.
    data = []
    for city_state, venues in city_state_dict.items():
        data.append(
            {
                "city": city_state[0],
                "state": city_state[1],
                "venues": venues,
            }
        )

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "")
    search = f"%{search_term}%"  # formatting
    venues = Venue.query.filter(
        Venue.name.ilike(search)
    ).all()  # getting venues that match

    response = {"count": len(venues), "data": []}
    # formatting response to include the number of upcoming shows.
    for venue in venues:
        num_upcoming_shows = len(
            Show.query.filter(
                Show.venue_id == venue.id, Show.start_time > datetime.now()
            ).all()
        )
        response["data"].append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_upcoming_shows,
            }
        )

    return render_template(
        "pages/search_venues.html", results=response, search_term=search_term
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        return render_template("errors/404.html"), 404
    now = datetime.now()
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
        helper = {
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if show.start_time < now:
            past_shows.append(helper)
        else:
            upcoming_shows.append(helper)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    form = VenueForm(request.form)
    if form.validate_on_submit():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                website=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
            )
            db.session.add(venue)
            db.session.commit()
            flash(f"Venue {form.name.data} was successfully listed!")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            flash(
                f"An error occurred. Venue {form.name.data} could not be listed. Error: {str(e)}"
            )
        finally:
            db.session.close()
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f"Error in {fieldName}: {err}")
        flash("an error occurred. Please check the form for errors.")
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        if venue:
            db.session.delete(venue)
            db.session.commit()
            flash(f"Venue {venue.name} was successfully deleted.")
            return jsonify({"success": True}), 200
        else:
            flash(f"Venue with id {venue_id} does not exist.")
            return jsonify({"success": False, "error": "Venue not found"}), 404
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while trying to delete the venue. Error: {str(e)}")
        jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.session.close()
    return redirect(url_for("venues"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    artists = Artist.query.order_by(Artist.id.desc()).all()
    data = []
    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term", "")
    search = f"%{search_term}%"
    artists = Artist.query.filter(Artist.name.ilike(search)).all()

    response = {
        "count": len(artists),
        "data": [],
    }

    for artist in artists:
        num_upcoming_shows = len(
            Show.query.filter(
                Show.artist_id == artist.id, Show.start_time > datetime.now()
            ).all()
        )
        response["data"].append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": num_upcoming_shows,
            }
        )

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=search_term,
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        return render_template("errors/404.html"), 404
    now = datetime.now()
    upcoming_shows = []
    past_shows = []
    for show in artist.shows:
        helper = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if show.start_time < now:
            past_shows.append(helper)
        else:
            upcoming_shows.append(helper)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} does not exist.")
        return redirect(url_for(artists))

    # Populate the form with the artist data
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link

    # Prepare the artist data in the correct format for rendering
    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
    }
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    if not artist:
        flash(f"Artist with ID {artist_id} does not exist.")
        return redirect(url_for("artists"))

    try:
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website = form.website_link.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data

        db.session.commit()
        flash(f"Artist {artist.name} was successfully updated!")
    except Exception as e:
        db.session.rollback()
        flash(
            f"An error occurred. Artist {artist.name} could not be updated. Error: {str(e)}"
        )
    finally:
        db.session.close()

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if not venue:
        flash(f"Venue with ID {venue_id} does not exist.")
        return redirect(url_for("venues"))

    # Populate the form with the venue data
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link

    # Prepare the venue data in the correct format for rendering
    venue_data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
    }

    return render_template("forms/edit_venue.html", form=form, venue=venue_data)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if not venue:
        flash(f"Venue with ID {venue_id} does not exist.")
        return redirect(url_for("venues"))

    # Update venue attributes with form data
    try:
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.address = form.address.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website = form.website_link.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data

        db.session.commit()
        flash(f"Venue {venue.name} was successfully updated!")
    except Exception as e:
        db.session.rollback()
        flash(
            f"An error occurred. Venue {venue.name} could not be updated. Error: {str(e)}"
        )
    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    form = ArtistForm(request.form)
    if form.validate_on_submit():
        try:
            artist = Artist(
                name=form.name.data,
                genres=form.genres.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                website=form.website_link.data,
                facebook_link=form.facebook_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
                image_link=form.image_link.data,
            )
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash("Artist " + request.form["name"] + " was successfully listed!")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            # on unsuccessful db insert, flash an error instead
            flash(
                "An error occurred. Artist "
                + request.form["name"]
                + " could not be listed. Error: "
                + str(e)
            )
        finally:
            db.session.close()
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f"Error in {fieldName}: {err}")
        flash("An error occurred. Please check the form for errors.")
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    shows = Show.query.order_by(Show.id.desc()).all()
    data = []
    for show in shows:
        data.append(
            {
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    form = ShowForm(request.form)
    if form.validate_on_submit():
        try:
            show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data,
            )
            db.session.add(show)
            db.session.commit()
            flash("Show was successfully listed!")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred. Show could not be listed. Error: {str(e)}")
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f"Error in {fieldName}: {err}")
        flash("An error occurred. Please check the form for errors.")

    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
