from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SelectMultipleField,
    DateTimeField,
    BooleanField,
    ValidationError,
)
from wtforms.validators import DataRequired, URL, Regexp
import enum


class GenreEnum(enum.Enum):
    Alternative = "Alternative"
    Blues = "Blues"
    Classical = "Classical"
    Country = "Country"
    Electronic = "Electronic"
    Folk = "Folk"
    Funk = "Funk"
    HipHop = "Hip-Hop"
    HeavyMetal = "Heavy Metal"
    Instrumental = "Instrumental"
    Jazz = "Jazz"
    MusicalTheatre = "Musical Theatre"
    Pop = "Pop"
    Punk = "Punk"
    RnB = "R&B"
    Reggae = "Reggae"
    RocknRoll = "Rock n Roll"
    Soul = "Soul"
    Other = "Other"


def validate_genres(form, field):
    valid_genres = [genre.value for genre in GenreEnum]
    for genre in field.data:
        if genre not in valid_genres:
            raise ValidationError(f"Invalid genre: {genre}")


class SearchForm(FlaskForm):
    search_term = StringField("search_term")


class ShowForm(FlaskForm):
    artist_id = StringField("artist_id")
    venue_id = StringField("venue_id")
    start_time = DateTimeField(
        "start_time", validators=[DataRequired()], default=datetime.today()
    )


class VenueForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField(
        "state",
        validators=[DataRequired()],
        choices=[
            ("AL", "AL"),
            ("AK", "AK"),
            ("AZ", "AZ"),
            ("AR", "AR"),
            ("CA", "CA"),
            ("CO", "CO"),
            ("CT", "CT"),
            ("DE", "DE"),
            ("DC", "DC"),
            ("FL", "FL"),
            ("GA", "GA"),
            ("HI", "HI"),
            ("ID", "ID"),
            ("IL", "IL"),
            ("IN", "IN"),
            ("IA", "IA"),
            ("KS", "KS"),
            ("KY", "KY"),
            ("LA", "LA"),
            ("ME", "ME"),
            ("MT", "MT"),
            ("NE", "NE"),
            ("NV", "NV"),
            ("NH", "NH"),
            ("NJ", "NJ"),
            ("NM", "NM"),
            ("NY", "NY"),
            ("NC", "NC"),
            ("ND", "ND"),
            ("OH", "OH"),
            ("OK", "OK"),
            ("OR", "OR"),
            ("MD", "MD"),
            ("MA", "MA"),
            ("MI", "MI"),
            ("MN", "MN"),
            ("MS", "MS"),
            ("MO", "MO"),
            ("PA", "PA"),
            ("RI", "RI"),
            ("SC", "SC"),
            ("SD", "SD"),
            ("TN", "TN"),
            ("TX", "TX"),
            ("UT", "UT"),
            ("VT", "VT"),
            ("VA", "VA"),
            ("WA", "WA"),
            ("WV", "WV"),
            ("WI", "WI"),
            ("WY", "WY"),
        ],
    )
    address = StringField("address", validators=[DataRequired()])
    phone = StringField(
        "phone",
        validators=[
            Regexp(
                r"^\d{3}-\d{3}-\d{4}$",
                message="Phone number must be in the format xxx-xxx-xxxx",
            )
        ],
    )
    image_link = StringField("image_link")
    genres = SelectMultipleField(
        "genres",
        validators=[DataRequired(), validate_genres],
        choices=[(genre.value, genre.value) for genre in GenreEnum],
    )
    facebook_link = StringField("facebook_link", validators=[URL()])
    website_link = StringField("website_link", validators=[URL()])
    seeking_talent = BooleanField("seeking_talent")
    seeking_description = StringField("seeking_description")


class ArtistForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField(
        "state",
        validators=[DataRequired()],
        choices=[
            ("AL", "AL"),
            ("AK", "AK"),
            ("AZ", "AZ"),
            ("AR", "AR"),
            ("CA", "CA"),
            ("CO", "CO"),
            ("CT", "CT"),
            ("DE", "DE"),
            ("DC", "DC"),
            ("FL", "FL"),
            ("GA", "GA"),
            ("HI", "HI"),
            ("ID", "ID"),
            ("IL", "IL"),
            ("IN", "IN"),
            ("IA", "IA"),
            ("KS", "KS"),
            ("KY", "KY"),
            ("LA", "LA"),
            ("ME", "ME"),
            ("MT", "MT"),
            ("NE", "NE"),
            ("NV", "NV"),
            ("NH", "NH"),
            ("NJ", "NJ"),
            ("NM", "NM"),
            ("NY", "NY"),
            ("NC", "NC"),
            ("ND", "ND"),
            ("OH", "OH"),
            ("OK", "OK"),
            ("OR", "OR"),
            ("MD", "MD"),
            ("MA", "MA"),
            ("MI", "MI"),
            ("MN", "MN"),
            ("MS", "MS"),
            ("MO", "MO"),
            ("PA", "PA"),
            ("RI", "RI"),
            ("SC", "SC"),
            ("SD", "SD"),
            ("TN", "TN"),
            ("TX", "TX"),
            ("UT", "UT"),
            ("VT", "VT"),
            ("VA", "VA"),
            ("WA", "WA"),
            ("WV", "WV"),
            ("WI", "WI"),
            ("WY", "WY"),
        ],
    )
    phone = StringField(
        "phone",
        validators=[
            Regexp(
                r"^\d{3}-\d{3}-\d{4}$",
                message="Phone number must be in the format xxx-xxx-xxxx",
            )
        ],
    )
    image_link = StringField("image_link")
    genres = SelectMultipleField(
        "genres",
        validators=[DataRequired(), validate_genres],
        choices=[(genre.value, genre.value) for genre in GenreEnum],
    )
    facebook_link = StringField("facebook_link", validators=[URL()])
    website_link = StringField("website_link", validators=[URL()])
    seeking_venue = BooleanField("seeking_venue")
    seeking_description = StringField("seeking_description")
