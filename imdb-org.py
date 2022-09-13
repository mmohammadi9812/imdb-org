# Copyright (C) 2020-2022 Mohammad Mohamamdi
#
# This file is part of imdb-org.
#
# imdb-org is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# imdb-org is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with imdb-org.  If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import os
import re
import shutil
import click
import imdb
import requests
import sys
import typing as t

from bs4 import BeautifulSoup as bs
from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap
from urllib.parse import urlparse

NO_COLOR = os.getenv("NO_COLOR") is not None
WRAP_WIDTH = 80


tqdm = __import__('tqdm', globals(), locals(), ['tqdm']).tqdm if sys.stderr.isatty() else lambda _: _


@dataclass
class Movie:
    title: str
    year: int
    director: imdb.Person.Person
    writer: imdb.Person.Person
    cast: t.List[imdb.Person.Person]
    genres: t.List[str]
    runtime: t.Optional[int]
    rating: float
    votes: int
    plot: str
    url: str
    image: str


def getItem(url: str):
    url = Path(url).name[2:]
    ia = imdb.Cinemagoer()
    m = ia.get_movie(url)
    dt = m.data
    url = f"https://www.imdb.com/title/tt{m.movieID}/"
    title = dt["title"]
    year = dt["year"]
    director, writer, cast = dt["director"], dt["writer"], dt["cast"]
    genres = list(map(str.lower, dt["genres"]))
    runtime = (
        int(dt["runtimes"][0])
        if re.match(r"^\d+$", dt["runtimes"][0])
        else int(dt["runtimes"][0].split(":")[-1])
    )
    image = m.get_fullsizeURL()
    rating = dt["rating"]
    votes = dt["votes"]
    plot = dt["plot outline"] or "\n".join(dt["plot"]) or ""
    return Movie(
        title=title,
        year=year,
        director=director,
        writer=writer,
        cast=cast,
        genres=genres,
        runtime=runtime,
        rating=rating,
        votes=votes,
        plot=plot,
        url=url,
        image=image,
    )


def stylizeMovie(m: Movie) -> str:
    r = click.style(f"title: ", fg="white")
    r += click.style(m.title, fg="cyan")

    return r


def organizeItem(imagePath: str, m: Movie) -> str:
    plot = "\n\t\t".join([el.strip() for el in wrap(m.plot, width=WRAP_WIDTH)])
    r = f"""    - [ ] [[{m.url}][{m.title}]] {m.rating} {f":{':'.join(m.genres)}:"}
    {plot}

    [[file:{imagePath}]]
"""
    return r


def downloadImage(dir: str, m: Movie) -> None:
    path = Path(dir) / f'{m.title}.jpg'
    r = requests.get(m.image, stream=True)
    r.raise_for_status()
    with open(path.__str__(), 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    del r


@click.command()
@click.option(
    "-l",
    "--name",
    "link",
    required=True,
    type=str,
    help="id of the list to be fetched, it must start with ls",
)
@click.option(
    "-f",
    "--file",
    "file",
    type=click.Path(writable=True),
    help="orgfile, to which list will be saved",
)
@click.option("--debug/--no-debug")
def doMain(link: str, file: t.Optional[click.Path], debug: bool):
    if debug:
        logging.basicConfig(filename=Path(__file__).stem + ".log", level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARN)
    logger = logging.getLogger(__name__)

    if link.startswith("ls"):
        link = "https://www.imdb.com/list/" + link
    
    host = urlparse(link).netloc
    if host is None or "imdb.com" not in host:
        raise ValueError(f"[-] invalid link {link}")

    logger.debug(f"getting {link}")
    resp = requests.get(link)
    resp.raise_for_status()
    logger.debug("parsing list elements")
    soup = bs(resp.text, features="lxml")
    jsonel = soup.find(type="application/ld+json").text
    dt = json.loads(jsonel)
    items = dt["about"]["itemListElement"]
    logger.debug(f"#{len(items)} items found on the list")
    if file:
        click.open_file(file, "w").close()

        imagesFolder = Path(Path(file).name).stem
        Path(imagesFolder).mkdir(exist_ok=True)

        with click.open_file(file, "w") as f:
            f.write(
                f"""
#+TITLE: {dt["name"]}
#+AUTHOR: Mohammd Mohammdi
#+STARTUP: inlineimages

* TODO {dt["name"]}
"""
            )
    else:
        click.echo(click.style(dt["name"], fg="yellow"), color=(not NO_COLOR))
    for item in tqdm(items):
        logger.debug(f'fetching {item["url"]}')
        full_item = getItem(item["url"])
        if file:
            imagePath = Path(imagesFolder) / f'{full_item.title}.jpg'
            with click.open_file(file, "a") as f:
                f.write(organizeItem('./' + imagePath.__str__(), full_item))
            downloadImage(imagesFolder, full_item)

        else:
            click.echo(stylizeMovie(full_item), color=(not NO_COLOR))


if __name__ == "__main__":
    doMain()
