from src.sql.select import check_pending_count
from src.sql.create import create_connection, create_table

from src.workflow.queue import scrape_initial_matches, get_match_in_queue
from src.workflow.process import process

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

if __name__ == "__main__":
    main()