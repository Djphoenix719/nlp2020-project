from bs4 import BeautifulSoup
import requests
import os
from tqdm import tqdm
from time import sleep
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin, ParseResult


def parse_robots(site: ParseResult) -> RobotFileParser:
    """
    Process a robots file for the specified domain.
    :param site:
    :return:
    """
    robots = RobotFileParser()
    robots.set_url(f"{site.scheme}://{site.netloc}/robots.txt")
    robots.read()
    return robots


def safe_file_name(file_name: str) -> str:
    """
    Remove characters that may cause errors in writing file names.
    :param file_name:
    :return:
    """
    return "".join([c for c in file_name if c.isalpha() or c.isdigit()]).strip().replace(' ', '_')


def process_common(folder: str, url: str) -> (str, BeautifulSoup, ParseResult, int):
    """
    Complete tasks common to all sites. Fetches the index page, soupifies it, parses
    the site meta-data, and checks for a delay in robots.txt
    :param folder:
    :param url:
    :return:
    """
    path = os.path.join('data', 'raw', folder)
    path = os.path.abspath(path)

    os.makedirs(path, exist_ok=True)

    site = urlparse(url)
    robots = parse_robots(site)
    try:
        delay = int(robots.crawl_delay('*'))
    except TypeError:
        delay = 0

    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html.parser")

    return path, soup, site, delay


def process_3pp(folder: str, url: str) -> None:
    """
    Process the d20pfsrd site
    :param folder:
    :param url:
    :return:
    """
    path, soup, site, delay = process_common(folder, url)

    links = soup.find('table').find_all('a')
    links = [f"http://{site.netloc}/{a['href']}" for a in links if "(3pp)" in a.text]

    download_all(path, links, delay)


def process_other(folder: str, url: str) -> None:
    """
    Process all non-d20pfsrd sites.
    :param folder:
    :param url:
    :return:
    """
    path, soup, site, delay = process_common(folder, url)

    links = soup.find('table').find_all('a')
    links = [f"http://{site.netloc}/{a['href']}" for a in links if "javascript" not in a["href"]]

    download_all(path, links, delay)


def download_all(folder: str, links: [str], delay: int):
    """
    Fetch all links, waiting the specified delay between each fetch.
    :param folder:
    :param links:
    :param delay:
    :return:
    """
    for idx, url in tqdm(enumerate(links), unit='pages', total=len(links), desc='Fetching monsters...'):
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "html.parser")
        title = soup.find('title').text.strip().replace(' ', '_')

        file_name = f"{idx:05}_{title}.html"
        with open(os.path.join(folder, file_name), 'w', encoding='utf-8') as file:
            file.write(request.text)

        if delay > 0:
            sleep(delay)


def main():
    listing_urls = [
        ('pf2e', 'http://2e.aonprd.com/Monsters.aspx?Letter=All'),
        ('pf1e', 'http://aonprd.com/Monsters.aspx?Letter=All'),
        ('dd35', 'https://www.realmshelps.net/allmonsters.shtml'),
        ('pf1e_3pp', 'https://www.d20pfsrd.com/bestiary/monster-listings/'),
    ]

    for folder, url in tqdm(listing_urls, unit='sites', total=len(listing_urls), desc='Fetching all data...'):
        process_other(folder, url)


if __name__ == '__main__':
    main()
