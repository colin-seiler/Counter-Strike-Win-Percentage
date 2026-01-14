from src.sql.statements import SELECT_BY_QUEUE, SELECT_BY_GAME_ID

def select_match(conn, game_id=None):
    if not game_id:
        cur = conn.cursor()
        cur.execute(SELECT_BY_QUEUE)
        row = cur.fetchone()

        return row
    else:
        cur = conn.cursor()
        cur.execute(SELECT_BY_GAME_ID)
        row = cur.fetchone()

        return row
    
def check_pending_count(conn):
    cur = conn.cursor()
    cur.execute("""
    SELECT COUNT(*) FROM match_queue WHERE status = 'pending'
    """)
    count = cur.fetchone()[0]
    return count