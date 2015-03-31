# -*- coding: utf-8 -*-
#
# Copyright (C) 2009, Gustavo Narea <http://gustavonarea.net/>.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
"""
Indexed data from the Netflix data sets.

"""
from random import randrange

from sqlalchemy.orm import sessionmaker, scoped_session, relation, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, ForeignKey, Column, func
from sqlalchemy.types import Unicode, Integer, Date, Float


__all__ = ("metadata", "make_session", "User", "Movie", "Rating",
           "WatchedMovieWithoutRating", "UserFactorsVector",
           "MovieFactorsVector", "UserFactor", "MovieFactor")


BaseModel = declarative_base()
metadata = BaseModel.metadata


# Association table for the many-to-many relationship between users and
# movies (i.e., the movies watched and rated, but whose rating value is
# unknown):
unknown_ratings = Table("unknown_ratings", metadata,
    Column("user_id", Integer, ForeignKey("users.user_id")),
    Column("movie_id", Integer, ForeignKey("movies.movie_id"))
)


def make_session(engine):
    """
    Return an SQLAlchemy session for ``engine``.
    
    :param engine: A database URI.
    :param engine: basestring
    :return: The SA session.
    
    """
    maker = sessionmaker(autoflush=True, autocommit=False, bind=engine)
    session = scoped_session(maker)
    return session


#{ Models


class User(BaseModel):
    """
    User table.
    
    """
    
    __tablename__ = "users"
    
    #{ Columns
    
    user_id = Column(Integer(6), primary_key=True)
    
    average_rating = Column(Float(), default=0)
    
    #{ Relationships
    
    unknown_rated_movies = relation("Movie", secondary=unknown_ratings)
    
    #}
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.factors_vector = self.factors_vector or UserFactorsVector()
    
    @classmethod
    def create_user(cls, db_session, user_id):
        """
        Create a user account for ``user_id`` if it doesn't exist yet.
        
        """
        user = db_session.query(cls).get(user_id)
        if user is None:
            user = cls(user_id=user_id)
            db_session.add(user)
    
    def recalculate_average_rating(self, db_session):
        """
        Recalculate the user's global rating.
        
        """
        avg_func = func.avg(Rating.rating_value)
        average = db_session.query(avg_func).filter(User.user_id==self.user_id)
        self.average_rating = average.one()[0]


class Movie(BaseModel):
    """
    Movie table.
    
    """
    
    __tablename__ = "movies"
    
    #{ Columns
    
    movie_id = Column(Integer(5), primary_key=True)
    
    year = Column(Integer(4))
    
    title = Column(Unicode())
    
    average_rating = Column(Float(), default=0)
    
    #}
    
    def __init__(self, id_, title, year):
        self.movie_id = id_
        self.title = title
        self.year = year
        self.factors_vector = self.factors_vector or MovieFactorsVector()
    
    def recalculate_average_rating(self):
        """
        Recalculate the movie's global rating.
        
        """
        avg_func = func.avg(Rating.rating_value)
        average = db_session.query(avg_func).filter(Movie.movie_id==self.movie_id)
        self.average_rating = average.one()[0]
    
    @classmethod
    def get_movie_title(cls, db_session, movie_id):
        """Return the title of the movie whose Id. is ``movie_id``."""
        movie = db_session.query(cls).get(movie_id)
        return movie.title
    
    @classmethod
    def get_random_movie(cls, db_session):
        random_movie_id = randrange(1, 17770)
        movie = db_session.query(cls).get(random_movie_id)
        return movie


class Rating(BaseModel):
    """
    Rating table.
    
    """
    
    __tablename__ = "ratings"
    
    #{ Columns
    
    rating_id = Column(Integer(), autoincrement=True, primary_key=True)
    
    rater_id = Column(Integer(6), ForeignKey("users.user_id"))
    
    movie_id = Column(Integer(5), ForeignKey("movies.movie_id"))
    
    rating_date = Column(Date(), nullable=True)
    
    rating_value = Column(Integer(length=1))
    
    #{ Relationships
    
    rater = relation(User, backref="rated_movies")
    
    movie = relation(Movie, backref="ratings")
    
    #}
    
    @classmethod
    def get_average_global_rating(cls, db_session):
        """Return the average global rating."""
        query = db_session.query(func.avg(cls.rating_value)).one()
        return query[0]


class WatchedMovieWithoutRating(BaseModel):
    """
    Table for the movies that were watched by a user, but whose rating is
    not available.
    
    """
    
    __tablename__ = "watched_movies"
    
    #{ Columns
    
    id = Column(Integer(), autoincrement=True, primary_key=True)
    
    user_id = Column(Integer(6), ForeignKey("users.user_id"))
    
    movie_id = Column(Integer(5), ForeignKey("movies.movie_id"))
    
    rating_date = Column(Date(), nullable=True)
    
    #{ Relationships
    
    user = relation(User, backref="watched_movies_without_rating")
    
    #}


class UserFactor(BaseModel):
    """Individual user factor component."""
    
    __tablename__ = "user_factors"
    
    #{ Columns
    
    factor_id = Column(Integer(), autoincrement=True, primary_key=True)
    
    factor_num = Column(Integer(3))
    
    factor_value = Column(Float())
    
    vector_id = Column(Integer(), ForeignKey("user_factors_matrix.vector_id"))
    
    #{ Relationships
    
    vector = relation("UserFactorsVector", backref="components")
    
    #}


class MovieFactor(BaseModel):
    """Individual movie factor component."""
    
    __tablename__ = "movie_factors"
    
    #{ Columns
    
    factor_id = Column(Integer(), autoincrement=True, primary_key=True)
    
    factor_num = Column(Integer(3))
    
    factor_value = Column(Float())
    
    vector_id = Column(Integer(), ForeignKey("movie_factors_matrix.vector_id"))
    
    #{ Relationships
    
    vector = relation("MovieFactorsVector", backref="components")
    
    #}


class BaseFactorsVector(object):
    """Base class for factors vectors."""
    
    def sum_vector(self, vector, db_session):
        """
        Add this vector and ``vector`` together.
        
        This is, sum the each factor's values.
        
        """
        pseudo_vector = []
        for this_factor in self.components:
            other_factor = vector.get_factor(this_factor.factor_num,
                                             db_session)
            sum = this_factor.factor_value + other_factor.value
            pseudo_vector.append(sum)
        return pseudo_vector
    
    def sum_vector_list(self, vector, db_session):
        """
        Add this vector and ``vector`` together.
        
        This is, sum the each factor's values.
        
        **This time, the ``vector`` is a Python list that represents the
        factor values of the actual vector.**
        
        """
        pseudo_vector = []
        counter = 0
        for factor in self.components:
            sum = factor.factor_value + vector[counter]
            pseudo_vector.append(sum)
            counter += counter
        return pseudo_vector
    
    def multiply_vector(self, vector, db_session):
        """
        Multiply this vector and ``vector``.
        
        This is, multiply the each factor's values.
        
        """
        pseudo_vector = []
        for this_factor in self.components:
            other_factor = vector.get_factor(this_factor.factor_num,
                                             db_session)
            product = this_factor.factor_value * other_factor.value
            pseudo_vector.append(product)
        return pseudo_vector
    
    def multiply_by_list(self, vector, db_session):
        """
        Multiply this vector and ``vector``.
        
        This is, multiply the each factor's values.
        
        **This time, the ``vector`` is a Python list that represents the
        factor values of the actual vector.**
        
        """
        pseudo_vector = []
        counter = 0
        for this_factor in self.components:
            product = this_factor.factor_value * vector[counter]
            pseudo_vector.append(product)
            counter += counter
        return pseudo_vector
    
    def multiply_by_number(self, number, db_session):
        """
        Multiply this vector by ``number``.
        
        This is, multiply the each factor's values by ``number``.
        
        """
        pseudo_vector = []
        for this_factor in self.components:
            product = this_factor.factor_value * number
            pseudo_vector.append(product)
        return pseudo_vector
    
    def get_factor(self, factor_num, db_session):
        """
        Return factor #factor_num.
        
        """
        factor = (db_session.query(self.factor_class)
                  .filter(self.factor_class.factor_num==factor_num)
                  .filter(self.factor_class.vector_id==self.vector_id)
                  )
        return factor.one()
    
    def get_average_factor_value(self, db_session):
        """
        Return the average values for the factors in this vector.
        
        """
        all_values = 0
        for factor in self.factors:
            all_values += factor.factor_value
        average = all_values / len(self.factors)
        return average


class UserFactorsVector(BaseFactorsVector, BaseModel):
    """User-factors vectors."""
    
    __tablename__ = "user_factors_matrix"
    
    #{ Columns
    
    vector_id = Column(Integer(), autoincrement=True, primary_key=True)
    
    user_id = Column(Integer(6), ForeignKey("users.user_id"))
    
    #{ Relationships
    
    user = relation(User, uselist=False, backref=backref("factors_vector",
                                                         uselist=False))
    
    #}
    
    factor_class = UserFactor


class MovieFactorsVector(BaseFactorsVector, BaseModel):
    """Movie-factors vectors."""
    
    __tablename__ = "movie_factors_matrix"
    
    #{ Columns
    
    vector_id = Column(Integer(), autoincrement=True, primary_key=True)
    
    movie_id = Column(Integer(6), ForeignKey("movies.movie_id"))
    
    #{ Relationships
    
    movie = relation(Movie, uselist=False, backref=backref("factors_vector",
                                                           uselist=False))
    
    #}
    
    factor_class = MovieFactor


#}
