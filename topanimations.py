import requests
from bs4 import BeautifulSoup as BS
from textwrap import wrap
from pathlib import Path
import shutil
import helium
import time

UserAgent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-en) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4'

animationURL = 'https://www.imdb.com/list/ls027345371/'

headers = {
    'User-Agent': UserAgent
}

parent = Path(__file__).parent

def download_image(name: str, link: str):
    image_relative_path = "animations/" + name + ".jpg"
    image_path = (parent / image_relative_path).resolve()
    res = requests.get(link, stream=True)
    res.raise_for_status()
    with open(image_path, 'wb') as f:
        res.raw.decode_content = True
        shutil.copyfileobj(res.raw, f)

if __name__ == "__main__":
    # reqres = requests.get(animationURL, headers=headers)
    driver = helium.start_firefox(animationURL, headless=True)
    clen = 0
    height = driver.execute_script("return document.body.scrollHeight")
    while clen < height:
        helium.scroll_down(num_pixels=400)
        clen += 400
        height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(1.)
    res = driver.page_source
    helium.kill_browser()
    soup = BS(res, features='html.parser')
    animations = soup.find_all("div", class_='lister-item')
    lineLength = 80
    with open('animations.org', 'w') as f:
        f.write('#+TITLE: Top Animations\n#+AUTHOR: Mohammd Mohammdi\n#+STARTUP: inlineimages\n')
        for animation in animations:
            image = animation.find('img')
            image_link = image['src']
            content = animation.find(class_='lister-item-content')
            index = animation.find(class_='lister-item-index').text
            title = content.find('a', href=True)
            title_link = title['href']
            title_txt = title.text
            download_image(title_txt, image_link)
            year = content.find('span', class_='lister-item-year').text
            length = content.find(class_='runtime').text
            genre = content.find(class_='genre').text
            rating = content.find(class_='ipl-rating-star__rating').text
            metascore_block = content.find('div', class_='ratings-metascore')
            metascore = metascore_block.find(class_='metascore').text if metascore_block is not None else 'N/A'
            rating_widget = content.find('div', class_='ipl-rating-widget')
            summary_block = metascore_block.findNext('p') if metascore_block is not None else rating_widget.findNext('p')
            summary = '\n\t'.join([el.strip() for el in wrap(summary_block.text, width=lineLength)])
            org_text = f"* [ ] {index} [[{title_link}][{title_txt}]] {rating}\t{ ':' + ':'.join([el.strip() for el in genre.split(',')]) + ':' }\n\t{year}\t{length}\t{metascore}\n\t{summary}\n\t[[file:./animations/{title_txt}.jpg]]\n"
            f.write(org_text)
