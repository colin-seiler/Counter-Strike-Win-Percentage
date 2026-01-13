from src.sql.statements import UPDATE_PASS, UPDATE_FAIL

def update_queue(conn, demo_url, queue_id, updated=False):
    cur = conn.cursor()

    if updated:
        cur.execute(UPDATE_PASS, (demo_url, queue_id))
        conn.commit()

    else:
        cur.execute(UPDATE_FAIL, (demo_url, queue_id))
        conn.commit()

    cur.close()