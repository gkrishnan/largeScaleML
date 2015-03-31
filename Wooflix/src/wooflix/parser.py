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
Parser for the movie filters written by the users in English, Dutch or 
Castilian.

"""

from booleano.parser import Grammar, EvaluableParseManager, SymbolTable, Bind
from booleano.operations import Variable


__all__ = ("parse_manager")


# Defining the grammars:

english_tokens = {
    'not': "not",
    'and': "and",
    'or': "or",
    'eq': "is",
    'ne': "is not",
    'belongs_to': "is contained in",
    'is_subset': "is sub-set of",
}
english_grammar = Grammar(**english_tokens)

dutch_tokens = {
    'not': "niet",
    'and': "en",
    'or': "of",
    'eq': "is",
    'ne': "is geen",
    'belongs_to': "is opgenomen in",
    'is_subset': "is onderdeel van",
}
dutch_grammar = Grammar(**dutch_tokens)

castilian_tokens = {
    'not': "no",
    'and': "y",
    'or': "o",
    'eq': "es",
    'ne': "no es",
    'belongs_to': u"está incluido en",
    'is_subset': u"están incluidos en",
}
castilian_grammar = Grammar(**castilian_tokens)


# Defining the variables:


class MovieId(Variable):
    """Booleano variable that represents the identificator of a movie."""
    operations = set(["equality"])
    
    def to_python(self, context):
        return context.movie_id
    
    def equals(self, value, context):
        return context.movie_id == value


class MovieTitle(Variable):
    """Booleano variable that represents the title of a movie."""
    operations = set(["equality", "membership"])
    
    def to_python(self, context):
        return context.title
    
    def equals(self, value, context):
        return context.title == value
    
    def belongs_to(self, value, context):
        """Check if the word ``value`` appears in the title."""
        return value in context.title
    
    def is_subset(self, value, context):
        """Check if the words in ``value`` appear in the title."""
        words = set(value)
        words_in_title = set(context.title.split(" "))
        return words.issubset(words_in_title)


class MovieYear(Variable):
    """Booleano variable that represents the year of release of a movie."""
    
    operations = set(["equality", "inequality"])
    
    def to_python(self, context):
        return context.year
    
    def equals(self, value, context):
        return context.year == value
    
    def greater_than(self, value, context):
        return context.year > value
    
    def less_than(self, value, context):
        return context.year < value


class MovieAverageRating(Variable):
    """Booleano variable that represents the average rating of a movie."""
    
    operations = set(["equality", "inequality"])
    
    def to_python(self, context):
        return context.average_rating
    
    def equals(self, value, context):
        return context.average_rating == value
    
    def greater_than(self, value, context):
        return context.average_rating > value
    
    def less_than(self, value, context):
        return context.average_rating < value


# Defining the scope:

symbols = SymbolTable("global",
    (
        Bind("movie", MovieId(), nl="film", es=u"película"),
    ),
    SymbolTable("movie",
        (
            Bind("id", MovieId(), nl="id", es="id"),
            Bind("title", MovieTitle(), nl="titel", es=u"título"),
            Bind("year", MovieYear(), nl="jaar", es=u"año"),
            Bind("average_rating", MovieAverageRating(), nl="gemiddelde_rating",
                 es=u"puntuación_promedio")
        ),
        nl="film",
        es=u"película"
    ),
)


# Finally, the parse manager:
parse_manager = EvaluableParseManager(symbols, english_grammar, nl=dutch_grammar,
                                      es=castilian_grammar)
