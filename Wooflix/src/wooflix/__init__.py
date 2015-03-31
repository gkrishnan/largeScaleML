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
Wooflix interface-independent library.

"""
import os
from datetime import date

from sqlalchemy import create_engine, func

from wooflix.indexing import index_dataset, index_dataset_basic
from wooflix.model import (make_session, metadata, User, Movie, Rating,
                           UserFactor, MovieFactor)
from wooflix.parser import parse_manager


class Recommender(object):
    """
    Recommender system.
    
    """
    
    def __init__(self, path_to_netflix_data, db_uri):
        self.path_to_netflix_data = path_to_netflix_data
        self.engine = create_engine(db_uri)
        self.session = make_session(self.engine)
        # Miscellaneous parameters:
        self.learning_rate = 0.001
        self.factors_regulator = 0.015
        self.factors_amount = 2
        self.default_factors_value = 0.00001
        self.maximum_epoch = 3
    
    def full_training(self):
        """
        Train the recommender system from scratch.
        
        """
        # Let's set up the database:
        metadata.create_all(bind=self.engine)
        
        index_dataset(self.path_to_netflix_data, self.session)
        
        self._store_average_rating()
        
        # Initializing the factors matrices:
        for factor_num in range(self.factors_amount):
            for user in self.session.query(User).all():
                factor = UserFactor(factor_num=factor_num,
                                    factor_value=self.default_factors_value)
                user.factors_vector.components.append(factor)
            for movie in self.session.query(Movie).all():
                factor = MovieFactor(factor_num=factor_num,
                                     factor_value=self.default_factors_value)
                movie.factors_vector.components.append(factor)
        
        for rating in self.session.query(Rating).all():
            self._train_rating(rating)
        
        self.session.commit()
    
    def naive_training(self, max_rated_movies=2):
        """
        Train the system using a small subset of the datasets.
        
        Regular training takes many hours to complete on modern hardware, so
        this method ignores most of the records in the dataset so we can have
        something working in a reasonable period of time.
        
        In fact this can hardly be called "training".
        
        """
        # Let's set up the database:
        metadata.create_all(bind=self.engine)
        
        index_dataset_basic(self.path_to_netflix_data, self.session, 1)
        
        self._store_average_rating()
        
        # Initializing the factors matrices:
        for factor_num in range(self.factors_amount):
            for user in self.session.query(User).all():
                factor = UserFactor(factor_num=factor_num,
                                    factor_value=self.default_factors_value)
                user.factors_vector.components.append(factor)
            for movie in self.session.query(Movie).all():
                factor = MovieFactor(factor_num=factor_num,
                                     factor_value=self.default_factors_value)
                movie.factors_vector.components.append(factor)
        
        self.session.commit()
    
    def add_rating(self, user_id, movie_id, rating_value):
        """
        Register raiting from user ``user_id`` to movie ``movie_id``, whose
        score is ``rating_value``.
        
        """
        user = self.session.query(User).get(user_id)
        movie = self.session.query(Movie).get(movie_id)
        rating_value = int(rating_value)
        today = date.today()
        
        rating = Rating(rating_value=rating_value, rating_date=today)
        rating.rater = user
        rating.movie = movie
        self.session.add(rating)
        
        # Let's propagate the rating:
        self._train_rating(rating)
        
        self.session.commit()
    
    def get_random_recommendations(self, user_id, limit=10):
        """
        Return ``limit`` recommendations for ``user_id``.
        
        """
        user = self.session.query(User).get(user_id)
        assert user, "User %s does not exist" % user_id
        movies = []
        for i in range(limit):
            movie = Movie.get_random_movie(self.session)
            movies.append(movie)
        # Now let's sort them:
        comparer = lambda m1, m2: self._compare_movies(user, m1, m2)
        sorted_movies = sorted(movies, comparer)
        return sorted_movies
    
    def filter_random_recommendations(self, user_id, filter, filter_lang="en",
                                      limit=10):
        """
        Return ``limit`` recommendations for ``user``.
        
        All those movies that meet the criteria describe in the boolean
        expression ``filter`` will be taken into account.
        
        """
        user = self.session.query(User).get(user_id)
        assert user, "User %s does not exist" % user_id
        movies = []
        # Retrieve random movies until we find what we're searching for:
        while len(movies) < limit:
            random_movie = Movie.get_random_movie(self.session)
            # Checking if it meets the requirements:
            if parse_manager.evaluate(filter, filter_lang, random_movie):
                movies.append(random_movie)
        # Now let's sort them:
        comparer = lambda m1, m2: self._compare_movies(user, m1, m2)
        sorted_movies = sorted(movies, comparer)
        return sorted_movies
    
    def _predict_rating(self, user, movie):
        """
        Predict the rating ``user`` would give to ``movie`` using the SVD++
        formula.
        
        """
        avg_rating = self._get_average_rating()
        user_bias = user.average_rating - avg_rating
        movie_bias = movie.average_rating - avg_rating
        baseline = avg_rating + user_bias + movie_bias
        
        # Computing the implicit preferences (implicit facts shared among all
        # the movies the user has seen, even if we don't know their rating):
        watched_movies = (len(user.watched_movies_without_rating) +
                          len(user.rated_movies))
        # The next variable, which "normalizes" the watched movies so as to say,
        # is represented as ( |N(u)| ^ -1/2 ) in the SVD++ formula. However,
        # N(u) can be {} (a null set), so we'll use 1 instead:
        wm_regulator = (abs(watched_movies) or 1) ** -0.5
        implicit_factors = [0 for i in range(self.factors_amount)]
        for movie in user.watched_movies_without_rating:
            implicit_factors = movie.sum_vector_list(implicit_factors,
                                                     self.session)
        for rating in user.rated_movies:
            implicit_factors = rating.movie.factors_vector.sum_vector_list(
                                    implicit_factors, self.session)
        implicit_prefences = [factor*wm_regulator for factor in implicit_factors]
        
        # Finally, the prediction:
        preferences = user.factors_vector.multiply_by_list(implicit_prefences,
                                                           self.session)
        factors = movie.factors_vector.multiply_by_list(preferences,
                                                        self.session)
        # Now that the factors have been computed, we can find its average:
        factors_sumation = 0
        for factor in factors:
            factors_sumation += factor
        average_factors = factors_sumation / self.factors_amount
        prediction = baseline + average_factors
        
        return prediction
    
    def _get_average_rating(self):
        """
        Return the global average rating.
        
        If it's not been calculated before, calculate it and store it.
        
        """
        try:
            avg_file_path = os.path.join(self.path_to_netflix_data, "average")
            avg_file = open(avg_file_path)
        except IOError:
            average = self._store_average_rating()
        else:
            average = float(avg_file.readline().strip())
        return average
    
    def _store_average_rating(self):
        """Store the average rating in a file and finally return it."""
        # Computing and storing the average:
        average = Rating.get_average_global_rating(self.session)
        # Storing the average:
        avg_file_path = os.path.join(self.path_to_netflix_data, "average")
        avg_file = open(avg_file_path, "w")
        avg_file.write(str(average))
        avg_file.close()
    
    def _train_rating(self, rating):
        """
        Update the factors vector for the movie and user involved in ``rating``.
        
        """
        user = rating.rater
        movie = rating.movie
        # A couple of short-cuts:
        lrate = self.learning_rate
        k = self.factors_regulator
        
        for factor_num in range(self.factors_amount):
            # For each factor, let's improve its accuracy both on the user
            # and movie sides:
            predicted_rating_value = self._predict_rating(user, movie)
            error = rating.rating_value - predicted_rating_value
            
            # Updating the factors:
            movie_factor = movie.factors_vector.get_factor(factor_num,
                                                           self.session)
            user_factor = user.factors_vector.get_factor(factor_num,
                                                         self.session)
            
            movie_factor.factor_value += (lrate *
                (error*user_factor.factor_value + k*movie_factor.factor_value))
            user_factor.factor_value += (lrate *
                (error*movie_factor.factor_value + k*user_factor.factor_value))
    
    def _compare_movies(self, user, movie1, movie2):
        prediction1 = self._predict_rating(user, movie1)
        prediction2 = self._predict_rating(user, movie2)
        return int(prediction1 - prediction2)

