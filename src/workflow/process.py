from src.demo.parse import parse_file

from src.sql.insert import (insert_event, insert_match, insert_maps, insert_rounds, 
                            insert_teams, insert_players, insert_rosters,
                            insert_ticks, insert_damage, insert_death, insert_bomb, insert_nades)

from src.utils import delete_file

def process(conn, match_info, dem_files):
    update_match = True
    event_name = match_info['event_name']
    event_url = match_info['event_url']
    match_date = match_info['match_date']
    match_url = match_info['match_url']

    event_id = insert_event(conn, event_url, event_name)
    
    for file in dem_files:
        demo_info = parse_file(file)

        map_name = demo_info['map_name']
        ticks = demo_info['ticks']
        starts = demo_info['starts']
        ends = demo_info['ends']
        deaths = demo_info['deaths']
        hurts = demo_info['hurt']
        nades = demo_info['nades']
        bombs = demo_info['bombs']

        unique_pairs = ticks[['steamid', 'name', 'team_clan_name']].drop_duplicates()
        teams = insert_teams(conn, unique_pairs)
        team_ids = [v for k, v in teams.items()]
        match_team_1 = team_ids[0]
        match_team_2 = team_ids[1]

        if update_match:
            match_id = insert_match(conn, event_id, match_url, match_date, match_team_1, match_team_2)
            update_match = False

        num_rounds = ticks['round_num'].max()
        map_id = insert_maps(conn, match_id, map_name, num_rounds)
        players, players_to_teams = insert_players(conn, unique_pairs, teams)
        insert_rounds(conn, map_id, starts, ends)
        insert_rosters(conn, map_id, players, players_to_teams)
        insert_ticks(conn, map_id, players, ticks)
        insert_damage(conn, map_id, players, hurts)
        insert_death(conn, map_id, players, deaths)
        insert_nades(conn, map_id, players, nades)
        insert_bomb(conn, map_id, players, bombs)

        deleted = delete_file(file)
        print(f'File was deleted: {deleted}')