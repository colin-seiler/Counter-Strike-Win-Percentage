import pandas as pd
from psycopg2 import sql, Error
from psycopg2.extras import execute_values

from src.utils import inventory_convert
from src.sql.statements import (EVENT_SQL, MATCH_SQL, MAP_SQL, ROUND_SQL,
                                    TEAM_SQL, PLAYER_SQL, ROSTER_SQL,
                                    TICK_SQL, DAMAGE_SQL, DEATH_SQL, NADE_SQL, BOMB_SQL,
                                    QUEUE_SQL)

def insert_event(conn, event_url, event_name):
    cur = conn.cursor()

    cur.execute(EVENT_SQL, (event_url, event_name))
    event_id = cur.fetchone()[0]

    conn.commit()
    cur.close()

    return event_id

def insert_match(conn, event_id, match_url, match_date, match_team_1, match_team_2):
    cur = conn.cursor()

    cur.execute(MATCH_SQL, (event_id, match_url, match_date, match_team_1, match_team_2))
    match_id = cur.fetchone()[0]

    conn.commit()
    cur.close()

    return match_id

def insert_maps(conn, match_id, map_name, num_rounds):
    cur = conn.cursor()

    cur.execute(MAP_SQL, (match_id, map_name, num_rounds))
    map_id = cur.fetchone()[0]

    conn.commit()
    cur.close()

    return map_id

def insert_rounds(conn, map_id, starts, ends):
    cur = conn.cursor()

    starts = starts.rename(columns={'tick':'start_tick'})
    ends = ends.rename(columns={'tick':'end_tick'})

    comb = starts.merge(ends, on='round', how='left')

    t_rounds = 0
    ct_rounds = 0
    for _, row in comb.iterrows():
        if row['winner'] == 'T':
            t_rounds += 1
        if row['winner'] == 'CT':
            ct_rounds += 1
        cur.execute(ROUND_SQL, (map_id, 
                                row['round'], 
                                row['winner'], 
                                row['reason'], 
                                row['start_tick'], 
                                row['end_tick'], 
                                ct_rounds, 
                                t_rounds))

    conn.commit()    
    cur.close()

def insert_teams(conn, unique_pairs): #unique_pairs = ticks[['steamid', 'name', 'team_clan_name']].drop_duplicates()
    cur = conn.cursor()

    teams = unique_pairs['team_clan_name'].unique()

    cur.execute(TEAM_SQL, (teams[0],))
    team1_id = cur.fetchone()[0]

    cur.execute(TEAM_SQL, (teams[1],))
    team2_id = cur.fetchone()[0]
    
    conn.commit()
    cur.close()

    teams = {teams[0]: team1_id, teams[1]: team2_id}

    return teams

def insert_players(conn, unique_pairs, teams):
    cur = conn.cursor

    players = {}
    teams = {}
    for pair in unique_pairs.iterrows():
        steamid = pair['steamid']
        name = pair['name']
        team = pair['team_clan_name']
        teamid = teams.get(team)

        cur.execute(PLAYER_SQL, (steamid, name))

        playerid = cur.fetchone()[0]
        players[steamid] = playerid
        teams[steamid] = teamid

    conn.commit()
    cur.close()

    return players, teams

def insert_rosters(conn, map_id, players, teams):
    cur = conn.cursor

    for player in players.keys():
        cur.execute(ROSTER_SQL, (map_id, players.get(player), teams.get(player)))

    conn.commit()
    cur.close()

def insert_ticks(conn, map_id, players, ticks):
    cur = conn.cursor()

    ticks['map_id'] = map_id
    ticks['user_player_id'] = ticks['steam'].map(players)
    ticks['inventory'] = ticks['inventory'].apply(inventory_convert)

    data = [tuple(row) for row in ticks[['map_id', 
                                         'user_player_id', 
                                         'tick',
                                         'round_num',
                                         'health',
                                         'X','Y','Z',
                                         'velocity_X','velocity_Y','velocity_Z',
                                         'yaw','pitch',
                                         'inventory',
                                         'current_equip_value',
                                         'has_armor',
                                         'has_helmet',
                                         'has_defuser',
                                         'is_ct',
                                         'is_defusing',
                                         'is_planted',
                                         'bomb_site',
                                         'is_alive']].values]
    
    execute_values(cur, TICK_SQL, data)

    conn.commit()
    cur.close()

def insert_damage(conn, map_id, players, hurts):
    cur = conn.cursor()

    hurts['map_id'] = map_id
    hurts['user_player_id'] = hurts['user_steamid'].map(players)
    hurts['attacker_player_id'] = hurts['attacker_steamid'].map(players)

    data = [tuple(row) for row in hurts[['map_id', 
                  'user_player_id', 'attacker_player_id', 
                  'tick', 'damage', 'weapon', 'hitgroup']].values]
    
    execute_values(cur, DAMAGE_SQL, data)

    conn.commit()
    cur.close()

def insert_death(conn, map_id, players, deaths):
    cur = conn.cursor()

    deaths['map_id'] = map_id
    deaths['user_player_id'] = deaths['user_steamid'].map(players)
    deaths['attacker_player_id'] = deaths['attacker_steamid'].map(players)

    data = [tuple(row) for row in deaths[['map_id',
                        'user_player_id', 'attacker_player_id', 'assister_player_id',
                        'tick', 'damage', 'weapon', 'hitgroup',
                        'is_headshot', 'is_attackerblind', 'is_attackerinair', 'is_noscope',
                        'is_penetrated', 'is_thrusmoke', 'is_assistedflash']].values]
    
    execute_values(cur, DEATH_SQL, data)

    conn.commit()
    cur.close()

def insert_nades(conn, map_id, players, nades):
    cur = conn.cursor()

    nades['map_id'] = map_id
    nades['user_player_id'] = nades['user_steamid'].map(players)

    data = [tuple(row) for row in nades[['map_id', 'user_player_id', 'tick', 'weapon']].values]

    execute_values(cur, NADE_SQL, data)

    conn.commit()
    cur.close()

def insert_bomb(conn, map_id, players, bombs):
    cur = conn.cursor()

    bombs['map_id'] = map_id
    bombs['user_player_id'] = bombs['user_steamid'].map(players)

    data = [tuple(row) for row in bombs[['map_id', 'user_player_id', 'tick', 'action']].values]

    if data:
        execute_values(cur, BOMB_SQL, data)

    conn.commit()
    cur.close()

def insert_queue(conn, match_list):
    cur = conn.cursor()

    match_list = [(url,) for url in match_list]

    execute_values(cur, QUEUE_SQL, match_list)

    conn.commit()
    cur.close()

    return len(match_list)