CREATE TABLE IF NOT EXISTS Guild_Settings (
	guild_id integer PRIMARY KEY,
	prefix text DEFAULT "!m"
);

CREATE TABLE IF NOT EXISTS Profile(
    member_id integer PRIMARY KEY,
    new bool DEFAULT FALSE,
    xp integer DEFAULT 0,
    level integer DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Member_Settings (
    member_id integer PRIMARY KEY
);