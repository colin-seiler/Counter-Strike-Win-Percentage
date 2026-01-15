import time
import random

from src.sql.select import check_pending_count
from src.sql.create import create_connection, create_table

from src.workflow.queue import scrape_initial_matches, get_match_in_queue
from src.workflow.process import process

import warnings
import pandas as pd

warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

def main():
    conn = create_connection()
    create_table(conn)
    count = check_pending_count(conn)

    if count == 0:
        print('Connection Success: Scraping for matches!')
        scrape_initial_matches(conn)
    elif count == None:
        print('Connection to PostgreSQL failed')
        return
    else:
        print(f'Connection Success: There are {count} matches already in queue!')
    

    while count:
        demo = get_match_in_queue(conn)
        if demo:
            match_info = demo[0]
            dem_files = demo[1]
            process(conn, match_info, dem_files)
        count = check_pending_count(conn)
        print(f'Action completed: There are {count} matches left in queue')
        
        if count > 0:
            sleep = random.uniform(20, 30)
            print(f'Sleeping for {sleep:.1f} seconds')
            time.sleep(sleep)

if __name__ == "__main__":
    main()