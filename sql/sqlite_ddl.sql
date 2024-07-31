CREATE TABLE
    IF NOT EXISTS token (
        id INTEGER PRIMARY KEY,
        email TEXT DEFAULT '' NOT NULL,
        type TEXT DEFAULT 'openai' NOT NULL,
        refresh_token TEXT DEFAULT '' NOT NULL,
        access_token TEXT DEFAULT '' NOT NULL,
        prefix TEXT DEFAULT '' NOT NULL,
        assign_to TEXT DEFAULT '' NOT NULL,
        remark TEXT DEFAULT '' NOT NULL,
        deleted INTEGER DEFAULT 0 NOT NULL,
        last_refresh_time DATETIME DEFAULT '1970-01-01 00:00:00' NOT NULL,
        expire_time DATETIME DEFAULT '1970-01-01 00:00:00' NOT NULL,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS token_relation (
        id INTEGER PRIMARY KEY,
        token_id INTEGER NOT NULL,
        user_key TEXT DEFAULT '' NOT NULL,
        share_token TEXT DEFAULT '' NOT NULL,
        deleted INTEGER DEFAULT 0 NOT NULL,
        last_refresh_time DATETIME DEFAULT '1970-01-01 00:00:00' NOT NULL,
        last_used_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
    );
