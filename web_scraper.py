import requests
from bs4 import BeautifulSoup
from robotexclusionrulesparser import RobotFileParserLookalike as RobotParser

def get_robots_txt(url):
    try:
        rp = RobotParser()
        rp.set_url(url)
        rp.read()
        return rp
    except Exception as e:
        print(f"Error reading robots.txt: {e}")
        return None

def search(query, num_results=5):
    search_url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.3"}

    robots_txt_url = "https://www.google.com/robots.txt"
    robots_parser = get_robots_txt(robots_txt_url)

    if robots_parser and not robots_parser.can_fetch("*", search_url):
        print("Blocked by robots.txt")
        return []

    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        search_results = []

        for g in soup.find_all("div", class_="g"):
            anchors = g.find_all("a")
            if anchors:
                link = anchors[0]["href"]
                title = g.find("h3").text
                if link.startswith("http") and not link.startswith("https://webcache.googleusercontent.com"):

                    # Check if the link is allowed by the website's robots.txt
                    robots_txt_url = f"{link.split('/')[0]}//{link.split('/')[2]}/robots.txt"
                    robots_parser = get_robots_txt(robots_txt_url)

                    if robots_parser and not robots_parser.can_fetch("*", link):
                        continue

                    search_results.append({"title": title, "link": link})
                    if len(search_results) >= num_results:
                        break

        return search_results

    return []
