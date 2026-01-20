from demoparser2 import DemoParser
import pandas as pd
from pathlib import Path
import numpy as np

from src.utils import inventory_convert
from src.demo.constants import (PLAYER_PROPS, 
                                KEEP_COLS, 
                                EVENT_PROPS, 
                                DEATH_COLS, 
                                HURT_COLS, 
                                NADE_COLS)

BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / 'data'
RAR_DIR = DATA_DIR / 'rars'
DEMO_DIR = DATA_DIR / 'demos'

def parse_demo(path):
    #Parse Demo using DemoParser2
    parser = DemoParser(path)

    players = parser.parse_ticks(PLAYER_PROPS)
    events = parser.parse_events(EVENT_PROPS, player=["last_place_name"])
    info = parser.parse_header()

    return players, events, info

def parse_file(file):
    players, events, info = parse_demo(file)
    players['steamid'] = players['steamid'].astype(str)
    players = players[players['is_match_started'] == True]
    players = players.copy()
    map_name = info.get('map_name')

    #EVENTS INTO DICT
    frames = {frame[0]:frame[1] for frame in events}
    
    #EXTRACT EVENTS
    ticks = [] #ticks is what will be concat'd for important ticks
    match_start = frames.get('round_announce_match_start')
    if match_start is not None:
        match_start = match_start.loc[0, 'tick']
    round_starts = frames.get('cs_round_final_beep')
    if round_starts is not None:
        ticks.append(round_starts['tick'])
    match_end = frames.get('cs_win_panel_match')
    if match_end is not None:
        match_end = match_end.loc[0, 'tick']
    round_ends = frames.get('round_end')
    if round_ends is not None:
        round_ends = round_ends[(round_ends['reason'].notna()) & (round_ends['tick'] != 0) & (round_ends['winner'].notna())]
        round_ends['round'] = np.arange(1, len(round_ends) + 1)
        ticks.append(round_ends['tick'])
    rounds = frames.get('round_start')
    if rounds is not None:
        rounds = rounds.loc[rounds.groupby('round')['tick'].idxmax()]
        rounds['round'] = np.arange(1, len(rounds) + 1)
        ticks.append(rounds['tick'])
    deaths = frames.get('player_death')
    if deaths is not None:
        deaths = deaths[DEATH_COLS]
        ticks.append(deaths['tick'])
    hurt = frames.get('player_hurt')
    if hurt is not None:
        hurt = hurt[HURT_COLS]
        ticks.append(hurt['tick'])
    nades = frames.get('grenade_thrown')
    if nades is not None:
        nades = nades[NADE_COLS]
        ticks.append(nades['tick'])
    
    #IN CASE OF NO PLANT, DEFUSE, EXPLODE
    planted = frames.get('bomb_planted') 
    if planted is None:
        planted = pd.DataFrame()
    elif not planted.empty:
        planted['action'] = 'plant'

    defused = frames.get('bomb_defused')
    if defused is None:
        defused = pd.DataFrame()
    elif not defused.empty:
        defused['action'] = 'defuse'

    explode = frames.get('bomb_exploded')
    if explode is None:
        explode = pd.DataFrame()
    elif not explode.empty:
        explode['action'] = 'explode'
        
    bombs = pd.concat([planted, defused, explode], ignore_index=True)
    if not bombs.empty:
        ticks.append(bombs['tick'])

    #START AND END OF ROUND
    round_numbers = (players[players['tick'].isin(round_starts['tick'])][['tick', 'total_rounds_played']]
                        .rename(columns={'tick':'start_tick', 'total_rounds_played':'start_total_rounds_played'}))
    
    #MATCH BOUNDARIES
    if match_end:
        players = players[players['tick'] <= match_end]
    if match_start:
        players = players[players['tick'] >= match_start]
    players = players.copy()

    #START TICK MERGE
    players = pd.merge_asof(players, round_numbers, left_on='tick', right_on='start_tick', direction='backward')
    in_round = players['total_rounds_played'] == players['start_total_rounds_played']
    shifted_in_round = in_round.shift(1).fillna(False)
    players = players[in_round | shifted_in_round]
    players['round_num'] = players['total_rounds_played'] + 1
    players['has_armor'] = players['armor_value'] > 0
    players['is_ct'] = players['team_name'].map({'CT':True,'TERRORIST':False})

    #BOMB INFO
    if not planted.empty:
        bomb_df = players.merge(planted.drop(columns='user_name'), left_on=['tick', 'steamid'], right_on=['tick', 'user_steamid'], how='left').rename(columns={'user_last_place_name':'bomb_site'})
        players['bomb_planted'] = bomb_df['site'].notna().astype(int)

        players['is_planted'] = np.where(players['bomb_planted']==1, True, None)
        players['is_planted'] = players.groupby('round_num')['is_planted'].ffill()
        players['is_planted'] = players['is_planted'].astype('boolean').fillna(False)

        players['bomb_site'] = np.where(bomb_df['bomb_site'].notna(), bomb_df['bomb_site'], None)
        players['bomb_site'] = players.groupby('round_num')['bomb_site'].ffill()

    #GET TICKS WHERE EVENT OCCURS
    important_ticks = pd.concat(ticks)

    #CREATE MASKS FOR EVENTS
    important_ticks = important_ticks[important_ticks.isin(players['tick'])]
    event_mask = players['tick'].isin(important_ticks)

    #CREATE MASKS FOR 8TH TICKS
    players['round_tick'] = players['tick']-players['start_tick']
    eighth_mask = (players['round_tick'] % 8 == 0)
    players = players[event_mask | eighth_mask]

    inventory_df = players['inventory'].apply(inventory_convert).apply(pd.Series)
    players = pd.concat([players.drop(columns='inventory'), inventory_df], axis=1)

    players = players[KEEP_COLS]

    return {
        'map_name': map_name,
        'ticks': players,
        'starts': rounds,
        'ends': round_ends,
        'deaths': deaths,
        'hurt': hurt,
        'nades': nades,
        'bombs': bombs
    }