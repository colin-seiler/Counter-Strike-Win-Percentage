SCHEMA_DATA = """
CREATE SCHEMA IF NOT EXISTS data;
SET search_path TO data, queue, public;

-- Events
CREATE TABLE IF NOT EXISTS data.events (
    event_id SERIAL PRIMARY KEY,
    event_url TEXT UNIQUE,
    event_name TEXT NOT NULL
);

-- TEAMS
CREATE TABLE IF NOT EXISTS data.teams (
    team_id SERIAL PRIMARY KEY,
    team_name TEXT UNIQUE NOT NULL
);

-- MATCHES
CREATE TABLE IF NOT EXISTS data.matches (
    match_id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(event_id) ON DELETE CASCADE,
    match_url TEXT UNIQUE,
    match_date TIMESTAMP,
    match_team_1 INTEGER REFERENCES teams(team_id) ON DELETE CASCADE,
    match_team_2 INTEGER REFERENCES teams(team_id) ON DELETE CASCADE
);

-- MAPS
CREATE TABLE IF NOT EXISTS data.maps (
    map_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id) ON DELETE CASCADE,
    map_name TEXT,
    total_rounds INTEGER
);

--ROUNDS
CREATE TABLE IF NOT EXISTS data.rounds(
    round_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    map_id INTEGER NOT NULL REFERENCES maps(map_id) ON DELETE CASCADE,
    round_num INTEGER NOT NULL,
    winner_side TEXT NOT NULL,
    round_end_reason TEXT,
    start_tick INTEGER,
    end_tick INTEGER,
    ct_score INTEGER,
    t_score INTEGER,
    UNIQUE(map_id, round_num)
);

-- PLAYERS
CREATE TABLE IF NOT EXISTS data.players (
    player_id SERIAL PRIMARY KEY,
    steam_id BIGINT UNIQUE NOT NULL,
    player_name TEXT NOT NULL     
);

-- ROSTERS
CREATE TABLE IF NOT EXISTS data.rosters (
    map_id INTEGER REFERENCES maps(map_id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    team_id INTEGER REFERENCES teams(team_id) ON DELETE CASCADE,
    PRIMARY KEY (map_id, player_id)
);

-- PLAYER TICKS
CREATE TABLE IF NOT EXISTS data.ticks (
    tick_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    map_id INTEGER NOT NULL REFERENCES maps(map_id) ON DELETE CASCADE,
    user_player_id INTEGER NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    tick INTEGER NOT NULL,
    round_tick INTEGER NOT NULL,
    round_num INTEGER NOT NULL,            
    health INTEGER NOT NULL,
    x FLOAT NOT NULL,                      
    y FLOAT NOT NULL,
    z FLOAT NOT NULL,
    velocity_x FLOAT,
    velocity_y FLOAT,
    velocity_z FLOAT,
    yaw FLOAT,
    pitch FLOAT,
    primary TEXT,
    secondary TEXT,
    smoke INTEGER NOT NULL,
    flash INTEGER NOT NULL,
    he INTEGER NOT NULL,
    molotov INTEGER NOT NULL,
    incend INTEGER NOT NULL,
    decoy INTEGER NOT NULL,
    inventory_value INTEGER NOT NULL,
    has_armor BOOLEAN NOT NULL,
    has_helmet BOOLEAN NOT NULL,
    has_defuser BOOLEAN NOT NULL,
    has_zeus BOOLEAN NOT NULL,
    is_ct BOOLEAN NOT NULL,
    is_defusing BOOLEAN NOT NULL,
    is_planted BOOLEAN NOT NULL,
    bomb_site TEXT,
    is_alive BOOLEAN NOT NULL
);

-- DAMAGE TICKS
CREATE TABLE IF NOT EXISTS data.damage_ticks (
    damage_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    map_id INTEGER NOT NULL REFERENCES maps(map_id) ON DELETE CASCADE,
    user_player_id INTEGER NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    attacker_player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    tick INTEGER NOT NULL,
    damage INTEGER NOT NULL,
    weapon TEXT,
    hitgroup TEXT
);

-- DEATH TICKS
CREATE TABLE IF NOT EXISTS data.death_ticks (
    death_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    map_id INTEGER NOT NULL REFERENCES maps(map_id) ON DELETE CASCADE,
    user_player_id INTEGER NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    attacker_player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    assister_player_id INTEGER REFERENCES players(player_id) ON DELETE CASCADE,
    tick INTEGER NOT NULL,
    damage INTEGER NOT NULL,
    weapon TEXT,
    hitgroup TEXT,
    is_headshot BOOLEAN,
    is_attackerblind BOOLEAN,
    is_attackerinair BOOLEAN,
    is_noscope BOOLEAN,
    is_penetrated BOOLEAN,
    is_thrusmoke BOOLEAN,
    is_assistedflash BOOLEAN
);

-- Nades
CREATE TABLE IF NOT EXISTS data.nade_ticks (
    nade_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    map_id INTEGER NOT NULL REFERENCES maps(map_id) ON DELETE CASCADE,
    user_player_id INTEGER NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    tick INTEGER NOT NULL,
    weapon TEXT NOT NULL
);

-- Bomb
CREATE TABLE IF NOT EXISTS data.bomb_ticks (
    bomb_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    map_id INTEGER NOT NULL REFERENCES maps(map_id) ON DELETE CASCADE,
    user_player_id INTEGER NOT NULL REFERENCES players(player_id) ON DELETE CASCADE,
    tick INTEGER NOT NULL,
    action bomb_action NOT NULL --explode, defuse, plant
);
"""

INDEX_DATA = """
CREATE INDEX IF NOT EXISTS idx_player_ticks_map_tick ON ticks(map_id, tick);
CREATE INDEX IF NOT EXISTS idx_player_ticks_player ON ticks(user_player_id, tick);
CREATE INDEX IF NOT EXISTS idx_player_ticks_round ON ticks(map_id, round_num);
CREATE INDEX IF NOT EXISTS idx_damage_map_tick ON damage_ticks(map_id, tick);
CREATE INDEX IF NOT EXISTS idx_damage_user ON damage_ticks(user_player_id, tick);
CREATE INDEX IF NOT EXISTS idx_death_map_tick ON death_ticks(map_id, tick);
CREATE INDEX IF NOT EXISTS idx_nade_map_tick ON nade_ticks(map_id, tick);
CREATE INDEX IF NOT EXISTS idx_inventory_gin ON ticks USING GIN (inventory);
CREATE INDEX IF NOT EXISTS idx_roster_team ON map_rosters(team_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_player_ticks_unique ON ticks(map_id, user_player_id, tick);
CREATE UNIQUE INDEX IF NOT EXISTS idx_death_unique ON death_ticks(map_id, user_player_id, tick);
CREATE INDEX IF NOT EXISTS idx_rounds_map ON rounds(map_id);
CREATE INDEX IF NOT EXISTS idx_rounds_lookup ON rounds(map_id, round_num);
"""

SCHEMA_QUEUE = """
CREATE SCHEMA IF NOT EXISTS queue;
SET search_path TO data, queue, public;

CREATE TABLE IF NOT EXISTS queue.match_queue (
    queue_id SERIAL PRIMARY KEY,
    match_url TEXT UNIQUE NOT NULL,
    demo_url TEXT,
    status queue_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
"""

INDEX_QUEUE = """
CREATE INDEX IF NOT EXISTS idx_queue_status ON queue.match_queue(status);
"""

SCHEMA_ENUMS = """
DO $$ BEGIN
    CREATE TYPE bomb_action AS ENUM ('plant', 'defuse', 'explode');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE queue_status AS ENUM ('pending', 'processing', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
"""