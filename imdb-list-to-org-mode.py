# Copyright (C) 2020 Mohammad Mohamamdi
# 
# ScrapIMDBList is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ScrapIMDBList is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with ScrapIMDBList. If not, see <http://www.gnu.org/licenses/>.

import requests
from bs4 import BeautifulSoup as BS
from textwrap import wrap
from pathlib import Path
import shutil
import helium
import time
import yaml
import re

URLs = dict()

with open('lists.yaml', 'r') as orig, open('.generated.yaml', 'r') as dups:
    config_genres = yaml.safe_load(orig)
    generated_genres = yaml.safe_load(dups)
    if generated_genres is None:
        generated_genres = list()
    for genre in config_genres:
        if genre not in generated_genres:
            URLs[genre] = config_genres[genre]

if URLs == {}:
    exit(0)

parent = Path(__file__).parent


def download_image(list_name: str, name: str, link: str):
    dir_relative = list_name + "/"
    dir_abs_path = (parent / list_name).resolve()
    if not Path(dir_abs_path).exists():
        Path(dir_abs_path).mkdir()
    image_relative_path = list_name + "/" + name + ".jpg"
    image_path = (parent / image_relative_path).resolve()
    res = requests.get(link, stream=True)
    res.raise_for_status()
    with open(image_path, 'wb') as f:
        res.raw.decode_content = True
        shutil.copyfileobj(res.raw, f)

def imdb_list_org(list_name: str, src: str, wrap_width: int = 80, save_images: bool = False):
    soup = BS(src, features='html.parser')
    animations = soup.find_all("div", class_='lister-item')
    with open(str.lower(str(list_name)) + '.org', 'w') as f:
        f.write(f'#+TITLE: Top {str.capitalize(str(list_name))}s\n#+AUTHOR: Mohammd Mohammdi\n#+STARTUP: inlineimages\n')
        for animation in animations:
            image = animation.find('img')
            image_link = image['src']
            content = animation.find(class_='lister-item-content')
            index = animation.find(class_='lister-item-index').text
            title = content.find('a', href=True)
            title_link = title['href']
            title_txt = title.text
            if save_images:
                if '?' in title_txt or '*' in title_txt or '"' in title_txt:
                    title_txt = title_txt.replace('?', '').replace('*','').replace('"','')
                download_image(str.lower(str(list_name)), title_txt, image_link)
            year = content.find('span', class_='lister-item-year').text
            length = content.find(class_='runtime').text if content.find(class_='runtime') is not None else 'N/A'
            genre = content.find(class_='genre').text
            rating = content.find(class_='ipl-rating-star__rating').text
            metascore_block = content.find('div', class_='ratings-metascore')
            metascore = metascore_block.find(class_='metascore').text if metascore_block is not None else 'N/A'
            rating_widget = content.find('div', class_='ipl-rating-widget')
            summary_block = metascore_block.findNext('p') if metascore_block is not None else rating_widget.findNext('p')
            summary = '\n\t'.join([el.strip() for el in wrap(summary_block.text, width=wrap_width)])
            org_text = f"* [ ] {index} [[{title_link}][{title_txt}]] {rating}\t{ ':' + ':'.join([el.strip() for el in genre.split(',')]) + ':' }\n\t{year}\t{length}\t{metascore}\n\t{summary}\n" + f"\t[[file:./{str.lower(str(list_name))}/{title_txt}.jpg]]\n" if save_images else ""
            f.write(org_text)


if __name__ == "__main__":
    driver = helium.start_firefox(headless=True)
    generated = list()
    for genre in URLs:
        helium.go_to(URLs[genre])
        clen = 0
        height = driver.execute_script("return document.body.scrollHeight")
        while clen < height:
            helium.scroll_down(num_pixels=400)
            clen += 400
            height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(1.)
        res = driver.page_source
        imdb_list_org(genre, res, save_images=True)
        generated.append(genre)

    with open('.generated.yaml', 'a') as f:
        yaml.safe_dump(generated, f)

    helium.kill_browser()
