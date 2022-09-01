# imdb-org
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is a python script to read and convert imdb lists to [org-mode](https://orgmode.org) lists

## Why
Well, I wanted to have a list of movies, to know which one I've seen and which one has not been seen yet.

But I didn't want to alwys have imdb page open on my computer, and I love org-mode!

So I thought why not scrap it to an org file?!

And so, here we are!

## Installation

Clone this repo, then:

```bash
git clone https://github.com/mmohammadi9812/imdb-org
cd imdb-org
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

```bash
python3 imdb-org.py -l [lsXXXXX]
```

To see all flags:
```bash
python3 imdb-org.py --help
```

## Status
This has come to place where it does what it had intented to do

So, it may not have new features, but it'll receive necessary maintenance, if needed at all

## License
Copyright (C) 2020-2022 Mohammad Mohamamdi

imdb-org is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

imdb-org is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with imdb-org.  If not, see <http://www.gnu.org/licenses/>.
