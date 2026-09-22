from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


def fetch_tvbs_news():
    url = 'https://news.tvbs.com.tw/'
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        with urlopen(request, timeout=10) as response:
            if response.status != 200:
                print(f'Failed to retrieve the news (HTTP {response.status})')
                return
            html = response.read()
    except Exception as error:
        print(f'Failed to retrieve the news: {error}')
        return

    soup = BeautifulSoup(html, 'html.parser')
    news_items = soup.find_all('h2')
    found_news = 0

    for item in news_items:
        link_tag = item.find_parent('a', href=True)
        title = item.get_text(strip=True)
        if link_tag is None or not title or '快訊' not in title:
            continue

        link = urljoin(url, link_tag['href'])
        print(f'Title: {title}')
        print(f'Link: {link}')
        print('---')
        found_news += 1

    if found_news == 0:
        print('No news items found')

if __name__ == '__main__':
    fetch_tvbs_news()