import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = [urljoin(url, link.get("href")) for link in soup.find_all("a")]
    return links

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title").text
    content = soup.get_text()
    return {"url": url, "title": title, "content": content}

def scrape_website(url, max_depth=1, current_depth=0):
    if current_depth > max_depth:
        return []

    links = get_links(url)
    pages = [scrape_page(url)]

    for link in links:
        pages.extend(scrape_website(link, max_depth=max_depth, current_depth=current_depth+1))

    return pages
