from src.demo.extract import extract_with_unar

from src.sql.select import select_match
from src.sql.update import update_queue
from src.sql.insert import insert_queue

from src.web.scrape import scrape_match, scrape_results
from src.web.download import download_file

from src.utils import delete_file

MAX_OFF = 15

def scrape_initial_matches(conn):
    #Scrape first -> MAX_OFF pages of results from hltv. Should go back ~1.5 years
    match_list = scrape_results(min_star=1, min_offset=0, max_offset=MAX_OFF)
    insert_queue(conn, match_list)

def scrape_new(conn): #Scrape matches until there are no more to scrape
    scrape = True
    lower = 0
    upper = 1

    while scrape == True and upper < 10:
        match_list = scrape_results(min_star=1, min_offset=0, max_offset=upper)
        inserted = insert_queue(conn, match_list)
        if inserted != 100:
            scrape = False
        lower += 1
        upper += 1

def get_match_in_queue(conn, game_id=None):
    #Pull match in queue and download info and demo
    match = select_match(conn)
    if not match:
        return False
    
    game_id, match_url = match[0], match[1]
    match_info = scrape_match(match_url)
    if match_info:
        demo_link = match_info['demo_download']
        rar_path = download_file(demo_link, f'data/rars/demo{game_id}.rar')
        if rar_path:
            dem_files = extract_with_unar(rar_path, 'data/demos/')
            if dem_files:
                update_queue(conn, demo_link, game_id, updated=True)
                return [match_info, dem_files]

    update_queue(conn, demo_link, game_id, updated=False)
    return None