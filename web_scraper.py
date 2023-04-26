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

def search(query):
    url = f"https://www.google.com/search?q={query}"
    results = scrape_website(url, max_depth=1)
    return [result['url'] for result in results if result['url'].startswith('http')]

def get_response(ints, intents_json, user_msg):
    tag = ints[0]["intent"]
    probability = float(ints[0]["probability"])
    list_of_intents = intents_json["intents"]
    for i in list_of_intents:
        if i["tag"] == tag and probability > 0.5:
            result = random.choice(i["responses"])
            break
        else:
            result = search(user_msg)
            if result:
                result = f"Here's what I found on the internet: {result[0]}"
            else:
                result = "I'm sorry, I didn't understand that. Could you please rephrase your question?"
    return result
