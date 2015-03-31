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
Wooflix command-line interface.

"""

from optparse import OptionParser
import os
import sys

from wooflix import Recommender

usage = "usage: wooflix COMMAND [argument ..]"
description = "You must `cd` into a Netflix data set directory to run this."
parser = OptionParser(usage=usage, description=description)
parser.add_option("-f", "--filter", dest="filter", type="string",
                  help="The expression to filter the recommendations to get")
parser.add_option("-l", "--filter-lang", dest="filter_lang", type="string",
                  help="The language of the filter")
parser.add_option("-n", "--naive", dest="naive_training", action="store_true",
                  help="Whether training should be 'naive'", default=False)
parser.add_option("-m", "--max", dest="recommendations_limit", type="int",
                  help="The max amount of recommendations to get", default=10)
parser.add_option("-d", "--database", dest="database_uri", type="string",
                  help="The URI for the database to be used",
                  default="sqlite:///indexed-dataset.db")


def main():
    (options, arguments) = parser.parse_args()
    
    if len(arguments) == 0:
        parser.error("The COMMAND is not specified")
    
    current_dir = os.getcwd()
    recommender = Recommender(current_dir, options.database_uri)
    
    if arguments[0] == "train":
        if not options.naive_training:
            print "The recommender system will be trained with all the dataset."
            print "This will take HOURS!"
            recommender.full_training()
        else:
            print "Naive training will start now"
            recommender.naive_training()
        print "Training finished!"
        sys.exit()
    elif arguments[0] == "rate":
        if len(arguments) < 4:
            parser.error("To rate a movie, the USER_ID, MOVIE_ID and "
                         "RATING_VALUE must be passed!")
        
        user_id = int(arguments[1])
        movie_id = int(arguments[2])
        rating_value = int(arguments[3])
        print "User #%s is rating movie #%s with %s stars" % (user_id, movie_id,
                                                              rating_value)
        print ("After registering the rating, the system will be partially "
               "trained again")
        recommender.add_rating(user_id, movie_id, rating_value)
        print "Rating has been registered and propagated"
        sys.exit()
    elif arguments[0] == "recommendations":
        if len(arguments) < 2:
            parser.error("To get movie recommendations, the target USER_ID "
                         "must be passed!")
        
        user_id = int(arguments[1])
        limit = options.recommendations_limit
        print "Recommendations for user #%s are going to be calculated" % user_id
        
        if not options.filter:
            movies = recommender.get_random_recommendations(user_id, limit)
        else:
            print "The following filter is being use: %s" % options.filter
            movies = recommender.filter_random_recommendations(user_id,
                options.filter, options.filter_lang, limit)
        
        counter = 1
        for movie in movies:
            print counter, ".-", movie.title, "(%s)" % movie.year
            counter += 1
    else:
        parser.error("Unknown command: %s" % arguments[0])


if __name__ == "__main__":
    main()
