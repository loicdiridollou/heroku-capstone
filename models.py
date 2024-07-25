"""Module with all models for the database."""

import os
from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Date, Integer, String

from config import database_setup

database_path = os.environ.get(
    "DATABASE_URL",
    "postgres://{}:{}@{}/{}".format(
        database_setup["username"],
        database_setup["password"],
        database_setup["port"],
        database_setup["database_name"],
    ),
)

db = SQLAlchemy()


def db_setup(app, database_path=database_path):
    """Set up database."""
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def db_reset():
    """Reset database."""
    db.drop_all()
    db.create_all()
    db_populate()


def db_populate():
    """Populate database."""
    new_actor = Actor(name="Anne", gender="Female", age=23)

    new_movie = Movie(title="Anne first Movie", release_date=date.today())

    new_actor.insert()
    new_movie.insert()
    db.session.commit()


########################################
# Actors model
# id, name, gender, age
########################################


class Actor(db.Model):  # type: ignore
    """Actor class."""

    __tablename__ = "actors"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    age = Column(Integer)

    def __init__(self, name, gender, age):
        self.name = name
        self.gender = gender
        self.age = age

    def insert(self):
        """Insert record in database."""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Update record in database."""
        db.session.commit()

    def delete(self):
        """Delete record from database."""
        db.session.delete(self)
        db.session.commit()

    def format(self):
        """Format method."""
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
        }


########################################
# Movies model
# id, title, release_date, actors
########################################


class Movie(db.Model):  # type: ignore
    """Movie class."""

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    release_date = Column(Date)
    actors = Column(String)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def insert(self):
        """Insert record in database."""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Update record in database."""
        db.session.commit()

    def delete(self):
        """Delete record from database."""
        db.session.delete(self)
        db.session.commit()

    def format(self):
        """Format method."""
        return {"id": self.id, "title": self.title, "release_date": self.release_date}
