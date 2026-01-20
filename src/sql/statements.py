EVENT_SQL = """
    INSERT INTO events (event_url, event_name)
    VALUES (%s, %s)
    ON CONFLICT (event_url)
    DO UPDATE SET event_url = EXCLUDED.event_url
    RETURNING event_id;
    """

MATCH_SQL = """
    INSERT INTO matches (event_id, match_url, match_date, match_team_1, match_team_2)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (match_url)
    DO UPDATE SET match_url = EXCLUDED.match_url
    RETURNING match_id;
    """

MAP_SQL = """
    INSERT INTO maps (match_id, map_name, total_rounds)
    VALUES (%s, %s, %s)
    RETURNING map_id;
    """

ROUND_SQL = """
    INSERT INTO rounds (map_id, round_num, winner_side, round_end_reason, start_tick, end_tick, ct_score, t_score)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (map_id, round_num)
    DO NOTHING
    """

TEAM_SQL = """
    INSERT INTO teams (team_name)
    VALUES (%s)
    ON CONFLICT (team_name)
    DO UPDATE SET team_name = EXCLUDED.team_name
    RETURNING team_id
    """

PLAYER_SQL = """
    INSERT INTO players (steam_id, player_name)
    VALUES (%s, %s)
    ON CONFLICT (steam_id)
    DO UPDATE SET steam_id = EXCLUDED.steam_id
    RETURNING player_id
    """

ROSTER_SQL = """
    INSERT INTO rosters (map_id, player_id, team_id)
    VALUES (%s, %s, %s)
    ON CONFLICT (map_id, player_id)
    DO NOTHING
    """

TICK_SQL = """
    INSERT INTO ticks (
        map_id, 
        user_player_id, 
        tick, round_tick, round_num, 
        health, 
        x, y, z, 
        velocity_x, velocity_y, velocity_z,
        yaw, pitch, 
        primary, secondary,
        smoke, flash, he, molotov, incend, decoy,
        inventory_value,
        has_armor,
        has_helmet,
        has_defuser,
        has_zeus,
        is_ct,
        is_defusing,
        is_planted,
        bomb_site,
        is_alive
        )
    VALUES %s
    """

DAMAGE_SQL = """
    INSERT INTO damage_ticks (
        map_id, 
        user_player_id, 
        attacker_player_id, 
        tick, 
        damage, 
        weapon, 
        hitgroup
    ) VALUES %s
    """

DEATH_SQL = """
    INSERT INTO death_ticks (
        map_id,
        user_player_id, attacker_player_id, assister_player_id,
        tick, damage, weapon, hitgroup,
        is_headshot, is_attackerblind, is_attackerinair, is_noscope,
        is_penetrated, is_thrusmoke, is_assistedflash
    ) VALUES %s
    """

NADE_SQL = """
    INSERT INTO nade_ticks (
        map_id,
        user_player_id,
        tick, weapon
    ) VALUES %s
    """

BOMB_SQL = """
    INSERT INTO bomb_ticks (
        map_id,
        user_player_id,
        tick, action
    ) VALUES %s
    """

QUEUE_SQL = """
    INSERT INTO match_queue (match_url) 
    VALUES %s
    ON CONFLICT (match_url)
    DO NOTHING
    RETURNING match_url
    """

UPDATE_PASS = """
    UPDATE queue.match_queue
    SET 
        demo_url = %s,
        status = 'completed',
        processed_at = NOW()
    WHERE queue_id = %s
    """

UPDATE_FAIL = """
    UPDATE queue.match_queue
    SET
        demo_url = %s,
        status = 'failed',
        processed_at = NOW()
    WHERE queue_id = %s
    """

SELECT_BY_QUEUE = """
    SELECT queue_id, match_url
    FROM match_queue
    WHERE status = 'pending'
    ORDER BY queue_id ASC
    LIMIT 1
    """

SELECT_BY_GAME_ID = """
    SELECT queue_id, match_url
    FROM match_queue
    WHERE queue_id = %s
    """