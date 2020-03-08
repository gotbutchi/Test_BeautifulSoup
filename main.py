import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template
from loguru import logger
from pprint import PrettyPrinter as pp

HOME_URL = 'https://www.globalgiving.org'
BASE_URL = 'https://www.globalgiving.org/search/?size=25&nextPage=1&sortField=sortorder&loadAllResults=true'
PORT = 8000


def url_builder(base_url: str = BASE_URL, param: str = "gift an education") -> str:
    return f"{base_url}&keywords={param.replace(' ','%20')}"


def fetch_html_then_return_soup(url: str, file_path: str = './templates/input.html') -> str:
    r = requests.get(url)
    with open(file_path, 'wb') as f:
        logger.debug(f"Writing content from {url} to {file_path}.")
        f.write(r.content)
    logger.debug(f"Returning BeautifulSoup html.parser from {file_path}")
    return BeautifulSoup(open(file_path), 'html.parser')


if __name__ == '__main__':
    pp(indent=2)
    soup = fetch_html_then_return_soup(url_builder())

    articles = soup.find_all('div', class_="flex_growChildren")
    data = []
    for article in articles:
        d = {'topic': '', 'title': '', 'author': '',
             'link': '', 'image': '', 'description': ''}
        d['topic'] = article.span.text.replace(
            '\n', '').replace("               ", ' ').strip()
        d['title'] = article.h4.text.strip()
        d['author'] = article.find(
            'div', class_="grid-12 box_verticalPaddedHalf").text.strip()
        d['description'] = article.find(
            'div', class_="col_ggSecondary1Text").text.split('…')[0].strip() + '..'
        d['link'] = HOME_URL + article.a["href"]
        d['image'] = HOME_URL + \
            article.a["style"][article.a["style"].find(
                "(")+1:article.a["style"].rfind(");")]
        data.append(d)
    logger.debug(data)

    app = Flask(__name__)
    app.config['TESTING'] = True

    @app.route('/')
    def index():
        return render_template('home1.html', data=data)

    logger.info(f"Running Flask server on port: {PORT}")
    app.run(host='127.0.0.1', port=PORT, debug=True)
