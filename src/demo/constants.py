PLAYER_PROPS = [
    "team_name",
    "tick",
    "total_rounds_played",
    "player_name",
    "team_num",
    "health",
    "X", "Y", "Z",
    "velocity_X", "velocity_Y", "velocity_Z"
    "yaw", "pitch",
    "is_alive",
    "is_defusing",
    "active_weapon_name",
    "inventory",
    "armor_value",
    "has_defuser",
    "has_helmet",
    "current_equip_value",
    "team_rounds_total",
    "team_clan_name",
    "is_match_started",
]

KEEP_COLS = [
    'tick',
    'steamid',
    'name',
    'round_num',
    'health',
    'X', 'Y', 'Z',
    'velocity_X', 'velocity_Y', 'velocity_Z'
    'yaw', 'pitch',
    'team_clan_name',
    'inventory',
    'current_equip_value',
    'has_armor',
    'has_helmet',
    'has_defuser',
    'is_ct',
    'is_defusing',
    'is_planted',
    'bomb_site',
    'is_alive',
]

EVENT_PROPS = [
    'round_announce_match_start',
    'cs_round_final_beep',
    'cs_win_panel_match',
    'bomb_planted',
    'bomb_exploded',
    'bomb_defused',
    'grenade_thrown',
    'player_death',
    'player_hurt',
    'round_start',
    'round_end',
]

DEATH_COLS = [
    'tick',
    'user_steamid',
    'dmg_health', 
    'weapon',
    'attacker_steamid', 
    'attackerblind', 
    'attackerinair', 
    'headshot', 
    'hitgroup', 
    'noscope', 
    'penetrated', 
    'thrusmoke', 
    'assistedflash', 
    'assister_steamid',
]

HURT_COLS = [
    'tick',
    'user_steamid',
    'health',
    'dmg_health',
    'weapon',
    'attacker_steamid',
    'hitgroup',
]

NADE_COLS = [
    'tick',
    'user_steamid',
    'weapon',
]