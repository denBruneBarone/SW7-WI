import os
import re
import requests
from urllib.parse import urlparse

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))


def get_robots_file(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    robots_url = f"{host.rstrip('/')}/robots.txt"

    try:
        # Send an HTTP GET request to fetch the robots.txt file
        response = requests.get(robots_url)
        response.raise_for_status()  # Raise an error for HTTP requests with error responses

        # Return the content of the robots.txt file
        return response.text
    except requests.RequestException as e:
        # Handle exceptions (network problems, invalid URL, etc.)
        print(f"Error fetching robots.txt from {robots_url}: {e}")
        return None


def robots_parser_from_file(filepath):
    input_file = os.path.join(PROJECT_ROOT, filepath)

    user_agent_pattern = r"User-agent:\s*(\*)"
    allow_pattern = r"Allow:\s*(/\S*)"
    disallow_pattern = r"Disallow:\s*(/\S*)"
    sitemap_pattern = r"Sitemap:\s*(\S*)"

    robots_data = {}

    with open(input_file, 'r') as f:
        string = f.read()
        lines = string.splitlines()

        current_agent = None

        for line in lines:
            # Check for User-agent
            user_agent_match = re.search(user_agent_pattern, line, re.IGNORECASE)
            if user_agent_match:
                current_agent = user_agent_match.group(1)
                if current_agent not in robots_data:
                    robots_data[current_agent] = {'allows': [], 'disallows': [], 'sitemaps': []}
                continue  # Move to next line after setting current_agent

            # Check for Allow directive
            if current_agent:
                allow_match = re.search(allow_pattern, line)
                if allow_match:
                    robots_data[current_agent]['allows'].append(allow_match.group(1))
                    continue

            # Check for Disallow directive
            if current_agent:
                disallow_match = re.search(disallow_pattern, line)
                if disallow_match:
                    robots_data[current_agent]['disallows'].append(disallow_match.group(1))
                    continue


            sitemap_match = re.search(sitemap_pattern, line)
            if sitemap_match:
                robots_data[current_agent]['sitemaps'].append(sitemap_match.group(1))
                continue

    return robots_data


def robots_parser_from_text(text):
    user_agent_pattern = r"User-agent:\s*(\*)"
    allow_pattern = r"Allow:\s*(/\S*)"
    disallow_pattern = r"Disallow:\s*(/\S*)"
    sitemap_pattern = r"Sitemap:\s*(\S*)"

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
                robots_data[current_agent] = {'allows': [], 'disallows': [], 'sitemaps': []}
            continue  # Move to next line after setting current_agent

        # Check for Allow directive
        if current_agent:
            allow_match = re.search(allow_pattern, line)
            if allow_match:
                robots_data[current_agent]['allows'].append(allow_match.group(1))
                continue

        # Check for Disallow directive
        if current_agent:
            disallow_match = re.search(disallow_pattern, line)
            if disallow_match:
                robots_data[current_agent]['disallows'].append(disallow_match.group(1))
                continue

        sitemap_match = re.search(sitemap_pattern, line)
        if sitemap_match:
            robots_data[current_agent]['sitemaps'].append(sitemap_match.group(1))
            continue

    return robots_data


def can_visit(url):
    for disallow in parser_obj['*']['disallows']:
        if disallow in url:
            regex = re.compile(disallow)
            if regex.search(url):
                return False
    return True



if __name__ == '__main__':
    robots_text = get_robots_file('https://www.bt.dk')
    parser_obj = robots_parser_from_text(robots_text)
    print(f'parser_obj: {parser_obj}')

    print(f'can visit? {can_visit('https://www.bt.dk/api')}')


