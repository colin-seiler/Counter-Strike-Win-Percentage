import pandas as pd

PLAYER_FEATURES = [
    'is_alive',
    'x', 'y', 'z', 
    'velocity_x', 'velocity_y', 'velocity_z',
    'yaw', 'pitch',
    'health', 'has_armor', 'has_helmet', 'has_defuser', 'has_zeus',
    'primary', 'secondary', 
    'smoke', 'flash', 'he', 'molotov', 'incend', 'decoy', 'inventory_value',
    'is_defusing'
    ]

def data_loader(conn):
    to_join = []

    for team, is_ct in [('ct', True), ('t', False)]:
        for p in range(1, 6):
            for f in PLAYER_FEATURES:
                to_join.append(f'MAX(CASE WHEN is_ct = {is_ct} AND p_num = {p} THEN {f} END) AS {team}{p}_{f}')


    sql_statement = f"""
    WITH numbered_players AS (
        SELECT 
            t.*,
            m.map_name,
            r.winner_side,
            r.round_end_reason,
            ROW_NUMBER() OVER (
                PARTITION BY t.map_id, t.round_num, t.round_tick, t.is_ct 
                ORDER BY t.x
            ) as p_num
        FROM data.ticks t
        JOIN data.maps m ON t.map_id = m.map_id
        JOIN data.rounds r ON t.map_id = r.map_id AND t.round_num = r.round_num
    )
    SELECT
        map_id,
        map_name,
        tick,
        round_num,
        round_tick,
        winner_side,
        round_end_reason,
        is_planted,
        bomb_site,
        {',\n   '.join(to_join)}
    FROM numbered_players
    GROUP BY map_id, map_name, tick, round_num, round_tick, winner_side, round_end_reason, is_planted, bomb_site
    ORDER BY map_id, round_num, round_tick
    """

    df = pd.read_sql(sql_statement, conn)

    return df