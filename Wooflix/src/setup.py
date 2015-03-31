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

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(name="wooflix",
      version="0.1",
      description="Movie Recommender System",
      author="Gustavo Narea",
      author_email="me@gustavonarea.net",
      packages=find_packages(exclude=["tests"]),
      tests_require = ["coverage >= 3.0", "nose >= 0.11.0"],
      install_requires=["SQLAlchemy >= 0.5.5", "Booleano == 1.0a1"],
      test_suite="nose.collector",
      entry_points={
          'console_scripts': ["wooflix = wooflix.wooflixcli:main"],
      },
)

