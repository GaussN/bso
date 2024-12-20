CREATE TABLE IF NOT EXISTS blanks (
	id          INTEGER NOT NULL,
	number      INTEGER NOT NULL CHECK(number <= 9999999),
	series TEXT NOT NULL,
	date        TEXT,
	comment     TEXT,
	status      INTEGER DEFAULT 0,
	created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
	updated_at  TEXT,
	deleted_at  TEXT,
	CONSTRAINT pk_id PRIMARY KEY(id AUTOINCREMENT),
	CONSTRAINT unique_num_ser UNIQUE(number, series)
);

CREATE VIEW IF NOT EXISTS c_blanks AS SELECT * FROM blanks WHERE deleted_at IS NULL;