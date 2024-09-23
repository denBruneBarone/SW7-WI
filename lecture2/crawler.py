import re
import os
import requests
import pprint
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json

from pip._internal.utils import urls

DEFAULT_DELAY_SECONDS = 2
CRAWL_COUNT = 100

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

seed = [
    "https://www.bt.dk/",
    "https://www.fitshop.dk/",
    "https://cat-bounce.com/",
    "https://moodle.com/",
    "https://www.youtube.com/",
    "https://www.dr.dk/",
    "https://www.nrk.no/",
    "https://ekstrabladet.dk/"

]


def crawl():
    for url in seed:
        add_host(url)

    url_frontier.extend(seed)

    frontier_len = len(url_frontier)
    crawl_counter = 0
    while frontier_len > 0 and crawl_counter < CRAWL_COUNT:
        i = 0
        while i < len(url_frontier):
            if crawl_counter >= CRAWL_COUNT:
                break

            if is_ready(url_frontier[i]):
                current_url = url_frontier[i]

                txt = get_robots_file(current_url)
                robots_obj = robots_parser_from_text(txt)
                if can_visit(current_url, robots_obj):
                    new_urls, html_text = scrape(current_url)
                    url_frontier.remove(current_url)
                    if html_text is not None:
                        url_backlog[current_url] = html_text
                    else:
                        url_backlog[current_url] = None
                    frontier_len = frontier_len - 1

                    host = urlparse(current_url).hostname
                    update_timestamp_on_host(host, DEFAULT_DELAY_SECONDS)

                    if new_urls:
                        url_frontier.extend(new_urls)

                    crawl_counter = crawl_counter + 1
                    print(f"successfully crawled!: crawl count now {crawl_counter}")
                else:
                    print(f"robots.txt says stay the fuck away from url: {current_url}")

            else:
                i = i + 1
                print("not ready yet. trying again...")

    print("backlog")
    pprint.pp(url_backlog)
    with open("url_backlog.json", "w") as outfile:
        json.dump(url_backlog, outfile)
    print("done")


def scrape(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        urls = set()
        text_content = []

        print(f"Scraping {url}")

        # Extract all valid URLs
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)  # Resolve relative URLs

            parsed_url = urlparse(full_url)

            if parsed_url.scheme in ("http", "https") and parsed_url.netloc:
                urls.add(full_url)

        # Extract text from all p, h1, h2, h3, etc. tags
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text_content.append(tag.get_text(strip=True))

        # Example of a function that processes the URL
        for url in urls:
            add_host(url)

        # Return both the URLs and the extracted text
        return urls, text_content

    except requests.RequestException as e:
        # Print the error and return None
        print(f"An error occurred in SCRAPE: {e}")
        return None, None


def is_ready(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    if host not in url_hosts:
        raise Exception(f"host not found. host: {host} from url: {url}")

    now = datetime.now()
    then = url_hosts[host]

    if now > then:
        return True
    else:
        return False


def add_host(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname

    if host not in url_hosts:
        url_hosts[f'{host}'] = datetime.now()


def get_robots_file(url):
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.hostname}/robots.txt"

    try:
        response = requests.get(robots_url)
        response.raise_for_status()

        update_timestamp_on_host(parsed_url.hostname, DEFAULT_DELAY_SECONDS)
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching robots.txt from {robots_url}: {e}")
        return None


def robots_parser_from_text(text):
    if text is None:
        return None
    user_agent_pattern = r"User-agent:\s*(\*)"
    # allow_pattern = r"Allow:\s*(/\S*)"
    disallow_pattern = r"Disallow:\s*(/\S*)"
    # sitemap_pattern = r"Sitemap:\s*(\S*)"

    robots_data = {}
    string = text
    lines = string.splitlines()

    current_agent = None

    for line in lines:
        # Check for User-agent
        user_agent_match = re.search(user_agent_pattern, line, re.IGNORECASE)
        if user_agent_match:
            current_agent = user_agent_match.group(1)
            if current_agent not in robots_data:
                robots_data[current_agent] = {'disallows': []}
            continue  # Move to next line after setting current_agent

        # Check for Disallow directive
        if current_agent:
            disallow_match = re.search(disallow_pattern, line)
            if disallow_match:
                robots_data[current_agent]['disallows'].append(disallow_match.group(1))
                continue

    return robots_data


def can_visit(url, parser_obj):
    if parser_obj is None:
        return True
    if '*' in parser_obj and 'disallows' in parser_obj['*']:
        for disallow in parser_obj['*']['disallows']:
            if disallow in url:
                regex = re.compile(disallow)
                if regex.search(url):
                    return False
    return True


def update_timestamp_on_host(host, timestamp_delay):
    if host not in url_hosts:
        raise Exception(f'could not find host: {host}')
    #Maybe add look for crawl-delay and follow this
    else:
        url_hosts[host] = datetime.now() + timedelta(seconds=timestamp_delay)


if __name__ == "__main__":
    url_frontier = []
    print(url_frontier)
    url_backlog = dict()
    url_hosts = dict()

    crawl()