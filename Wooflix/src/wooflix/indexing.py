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
Utilities to index Netflix data sets into databases.

"""
import os
from tarfile import open as open_tar, TarError
from datetime import date

from wooflix.model import User, Movie, Rating, WatchedMovieWithoutRating

__all__ = ("index_dataset", "index_dataset_basic", "IndexingError")


def index_dataset(path_to_dataset, db_session):
    """
    Load the Netflix data set in ``path_to_dataset`` into the database.
    
    :param path_to_dataset: The path to the Netflix data set.
    :type param_to_dataset: basestring
    :param db_session: The SQLAlchemy DB session to use to store the data set.
    :raises IndexingError: If something goes wrong.
    
    """
    # Index all the basic data set:
    index_dataset_basic(path_to_dataset, db_session, None)
    
    # Loading the unknown ratings (i.e., those in the qualifying set):
    qualifying_set = os.path.join(path_to_dataset, "qualifying.txt")
    for (movie_id, user_id, rating_date) in get_unknown_ratings(qualifying_set):
        User.create_user(db_session, user_id)
        watched_movie = WatchedMovieWithoutRating(movie_id=movie_id,
                                                  user_id=user_id,
                                                  rating_date=rating_date)
        db_session.add(watched_movie)


def index_dataset_basic(path_to_dataset, db_session, max_movies_rated):
    """
    Load a small sub-set of the Netflix data into the database.
    
    """
    # Loading the movies:
    movies_path = os.path.join(path_to_dataset, "movie_titles.txt")
    for movie in get_movies(movies_path):
        db_session.add(movie)
    
    # Loading the ratings:
    training_set = os.path.join(path_to_dataset, "training_set")
    if not os.path.isdir(training_set):
        # The ratings haven't been extracted. Let's do it!
        try:
            tar_file = open_tar(training_set + ".tar")
            tar_file.extractall(path_to_dataset)
        except TarError, exc:
            raise IndexingError("Could not open training file: %s" % exc)
        finally:
            tar_file.close()
    known_ratings = get_known_ratings_from_training_dir(training_set,
                                                        max_movies_rated)
    for (movie_id, user_id, r_value, r_date) in known_ratings:
        User.create_user(db_session, user_id)
        rating = Rating(movie_id=movie_id, rater_id=user_id,
                        rating_value=r_value, rating_date=r_date)
        db_session.add(rating)


def get_movies(path_to_movies):
    """
    Return the movies, converted into the valid data model.
    
    :param path_to_movies: The path to the movies file.
    
    """
    try:
        movies_file = open(path_to_movies)
    except IOError, exc:
        raise IndexingError("Could not open movies file: %s" % exc)
    
    for movie_line in movies_file:
        # Removing the trailing line newline character:
        movie_line = movie_line.rstrip()
        (movie_id, movie_year, movie_title) = movie_line.split(",", 2)
        
        # Correcting some non-ASCII characters in the titles (e.g.,
        # movie 6483):
        movie_title = movie_title.decode("iso-8859-1")
        movie_title = unicode(movie_title)
        
        movie = Movie(movie_id, movie_title, movie_year)
        yield movie
    
    movies_file.close()


def get_known_ratings_from_training_dir(path_to_training_data_dir,
                                        max_movies_rated):
    """
    Return all the ratings in the training data set.
    
    It will iterate over all the files in the training data set. Note: The
    training data set must have been extracted because we're going to use
    a directory.
    
    """
    counter = 1
    for file_name in os.listdir(path_to_training_data_dir):
        path = os.path.join(path_to_training_data_dir, file_name)
        movie_rating_file = open(path)
        # In these files, the first line is the movie id followed by a colon:
        movie_id = movie_rating_file.readline().strip().rstrip(":")
        
        for rating in movie_rating_file:
            # Removing any trailing spaces:
            rating = rating.strip()
            (user_id, rating_value, rating_date) = rating.split(",", 2)
            # Converting these components into the right types:
            user_id = int(user_id)
            rating_value = int(rating_value)
            rating_date = qualify_date(rating_date)
            
            yield (movie_id, user_id, rating_value, rating_date)
        
        movie_rating_file.close()
        
        if max_movies_rated and counter > max_movies_rated:
            break
        counter += counter


def get_unknown_ratings(path_to_qualifying_set):
    """
    Return all the movies watched by every user, but whose rating value is
    not available.
    
    This is extracted from the qualifying data set.
    
    """
    try:
        qualifying_set = open(path_to_qualifying_set)
    except IOError, exc:
        raise IndecingError("Could not open qualifying set: %s" % exc)
    
    current_movie = None
    
    for line in qualifying_set:
        # Removing the trailing newline character:
        line = line.rstrip()
        
        if line[-1] == ":":
            # It's a movie section!
            current_movie = int(line[:-1])
        else:
            # It's a rating record.
            (user_id, rating_date) = line.split(",")
            # Converting to the right types:
            user_id = int(user_id)
            rating_date = qualify_date(rating_date)
            
            yield (current_movie, user_id, rating_date)
    
    qualifying_set.close()


def qualify_date(date_string):
    """Turn ``date_string`` into a valid Python date object."""
    date_parts = [int(part) for part in date_string.split("-")]
    qualified_date = date(*date_parts)
    return qualified_date


#{ Exceptions


class IndexingError(Exception):
    """
    Exception raised when there was a problem while loading the Netflix data
    set into a database.
    
    """
    pass


#}
