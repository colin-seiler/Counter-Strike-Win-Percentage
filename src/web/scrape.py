from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

from src.web.constants import HEADERS

def scrape_results_page(results_url, offset):
    #Used in scrape_results() to get matches from each results page
    print(f'Scraping results from {offset+1} to {offset+101}')
    response = requests.get(results_url, headers=HEADERS, impersonate="chrome")
    
    if response.status_code != 200:
        print(f'Unable to reach results {offset} to {offset+100}')
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    matches = soup.find_all('a', href=re.compile(r'^/?matches/(\d+)/([^/\s]+)'))

    return [match['href'] for match in matches]

def scrape_results(min_star=1, min_offset=0, max_offset=1):
    #Using scrape_results_page() scrapes pages given a min_star rating and min and max offset
    scraped_matches = []
    if max_offset <= min_offset:
        raise ValueError

    for num in range(min_offset, (max_offset)):
        offset = num * 100
        results_url = f'https://www.hltv.org/results?stars={min_star}&offset={offset}'

        temp_matches = scrape_results_page(results_url=results_url, offset=offset)
        if temp_matches:
            scraped_matches.extend(temp_matches)
        else:
            print('Unable to connect to HLTV: Most likely blocked by CloudFlare')

        if num != max_offset-1:
            time.sleep(20)

    print(f'Scraped {len(scraped_matches)} from hltv.org')
    return [f'https://www.hltv.org{url}' for url in scraped_matches]

def scrape_match(match_url):
    #Once scrape_results is done, use scrape_demo to get demo link from each match page for download
    response = requests.get(match_url, headers=HEADERS, impersonate="chrome")
    
    if response.status_code != 200:
        print(f"Error {response.status_code}")
        return None

    match_info = {}

    soup = BeautifulSoup(response.text, 'html.parser')
    demo_tag = soup.find('a', href=re.compile(r'/download/demo/\d+'))
    if demo_tag:
        match_info['demo_download'] = f"https://www.hltv.org{demo_tag['href']}"
        
    event = soup.find('a', href=lambda x: x and '/events/' in x, title=True)
    if event:
        match_info['event_name'] = event.get('title') or event.get_text(strip=True)
        match_info['event_url'] = f"https://www.hltv.org{event['href']}"

    match_info['match_url'] = match_url
    date_div = soup.find('div', class_='date', attrs={'data-unix': True})
    if date_div:
        unix_ms = int(date_div['data-unix'])
        match_info['match_date'] = datetime.fromtimestamp(unix_ms / 1000)
        
    team1_div = soup.find('div', class_='team1-gradient') or soup.find('div', class_='team')
    if team1_div:
        team1_link = team1_div.find('a', href=lambda x: x and '/team/' in x)
        if team1_link:
            match_info['team1_name'] = team1_link.find('div', class_='teamName').get_text(strip=True)
            match_info['team1_link'] = f"https://www.hltv.org{team1_link['href']}"
            match_info['team1_logo'] = team1_link.find('img', class_='logo')['src']

    team2_div = soup.find('div', class_='team2-gradient')
    if team2_div:
        team2_link = team2_div.find('a', href=lambda x: x and '/team/' in x)
        if team2_link:
            match_info['team2_name'] = team2_link.find('div', class_='teamName').get_text(strip=True)
            match_info['team2_link'] = f"https://www.hltv.org{team2_link['href']}"
            match_info['team2_logo'] = team2_link.find('img', class_='logo')['src']

    return match_info