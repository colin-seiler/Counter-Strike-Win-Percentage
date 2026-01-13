from src.sql.select import check_pending_count
from src.sql.create import create_connection
from src.sql.update import update_queue

from src.workflow.queue import scrape_new, scrape_initial_matches, get_match_in_queue
from src.workflow.process import process

def main():
    conn = create_connection()
    count = check_pending_count(conn)

    if count == 0:
        scrape_initial_matches(conn)
    elif count == None:
        print('Connection to PostgreSQL failed')
        return

    while count:
        demo = get_match_in_queue(conn)
        if demo:
            match_info = demo[0]
            dem_files = demo[1]
            process(conn, match_info, dem_files)
        count = check_pending_count(conn)

if __name__ == "__main__":
    main()