# =====
# USERS
# =====

CREATE_TABLE_USERS = """CREATE TABLE IF NOT EXISTS users (
                            id VARCHAR(255) NOT NULL PRIMARY KEY,
                            email VARCHAR(255) NOT NULL,
                            image_url VARCHAR(255) NOT NULL,
                            joined TIMESTAMP NOT NULL DEFAULT NOW(),
                            name VARCHAR(255) DEFAULT '',
                            profile_bg VARCHAR(255) NOT NULL);"""

DELETE_USER = "DELETE FROM users WHERE id = %s;"

INSERT_USER = "INSERT INTO users (id, email, image_url, joined, name, profile_bg) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"

SELECT_USER = "SELECT email, image_url, joined, name, profile_bg FROM users WHERE id = %s;"

UPDATE_USER = "UPDATE users SET (email, image_url, name, profile_bg) = (%s, %s, %s, %s) WHERE id = %s;"

# =======
# LEAGUES
# =======

CREATE_TABLE_LEAGUES = """CREATE TABLE IF NOT EXISTS leagues (
                            id VARCHAR(255) PRIMARY KEY,
                            created TIMESTAMP NOT NULL DEFAULT NOW(),
                            name VARCHAR(255) NOT NULL,
                            owner_id VARCHAR(255) NOT NULL REFERENCES users(id));"""

DELETE_LEAGUE = "DELETE FROM leagues WHERE id = %s;"

INSERT_LEAGUE = "INSERT INTO leagues (id, created, name, owner_id) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"

UPDATE_LEAGUE = "UPDATE leagues SET (name) = (%s) WHERE id = %s;"

# ===========
# MEMBERSHIPS
# ===========

CREATE_TABLE_MEMBERSHIPS = """CREATE TABLE IF NOT EXISTS memberships (
                                created TIMESTAMP NOT NULL DEFAULT NOW(),
                                league_id VARCHAR(255) NOT NULL REFERENCES leagues(id),
                                user_id VARCHAR(255) NOT NULL REFERENCES users(id),
                                UNIQUE (league_id, user_id));"""

DELETE_MEMBERSHIP = "DELETE FROM memberships WHERE league_id = %s AND user_id = %s;"

DELETE_MEMBERSHIPS = "DELETE FROM memberships WHERE league_id = %s;"

INSERT_MEMBERSHIP = """INSERT INTO memberships (league_id, user_id)
                            VALUES (%s, %s) ON CONFLICT (league_id, user_id) DO NOTHING;"""

# ======
# ROUNDS
# ======

CREATE_TABLE_ROUNDS = """CREATE TABLE IF NOT EXISTS rounds (
                            id VARCHAR(255) PRIMARY KEY,
                            created TIMESTAMP NOT NULL DEFAULT NOW(),
                            description VARCHAR(255) DEFAULT '',
                            league_id VARCHAR(255) NOT NULL REFERENCES leagues(id),
                            name VARCHAR(255) NOT NULL,
                            playlist_url VARCHAR(255) DEFAULT '',
                            submissions_due TIMESTAMP NOT NULL,
                            votes_due TIMESTAMP NOT NULL);"""

DELETE_ROUND = "DELETE FROM users WHERE id = %s;"

DELETE_ROUNDS = "DELETE FROM rounds WHERE league_id = %s;"

INSERT_ROUND = """INSERT INTO rounds (id, created, description, league_id, name, submissions_due, votes_due)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;"""

UPDATE_ROUND = """UPDATE rounds SET (description, name, submissions_due, votes_due)
                    VALUES (%s, %s, %s, %s) WHERE id = %s;"""

# ===========
# SUBMISSIONS
# ===========

CREATE_TABLE_SUBMISSIONS = """CREATE TABLE IF NOT EXISTS submissions (
                                    created TIMESTAMP NOT NULL DEFAULT NOW(),
                                    round_id VARCHAR(255) NOT NULL REFERENCES rounds(id),
                                    spotify_uri VARCHAR(255) NOT NULL,
                                    submitter_id VARCHAR(255) NOT NULL REFERENCES users(id),
                                    updated TIMESTAMP NOT NULL DEFAULT NOW(),
                                    UNIQUE (round_id, spotify_uri));"""

INSERT_SUBMISSION = """INSERT INTO submissions (created, round_id, spotify_uri, submitter_id, updated)
                            VALUES (%s, %s, %s, %s, %s) ON CONFLICT (round_id, spotify_uri) DO NOTHING;"""

SELECT_SUBMISSIONS = """SELECT submissions.spotify_uri as uri,
                               su.id as submitter_id,
                               su.name as submitter_name
                        FROM submissions
                        LEFT JOIN users su ON su.id = submissions.submitter_id
                        WHERE submissions.round_id = %s
                        ORDER BY submissions.created;"""

# =====
# VOTES
# =====

CREATE_TABLE_VOTES = """CREATE TABLE IF NOT EXISTS votes (
                            created TIMESTAMP DEFAULT NOW(),
                            round_id VARCHAR(255) NOT NULL,
                            spotify_uri VARCHAR(255) NOT NULL,
                            updated TIMESTAMP NOT NULL DEFAULT NOW(),
                            voter_id VARCHAR(255) NOT NULL REFERENCES users(id),
                            weight SMALLINT NOT NULL,
                            FOREIGN KEY (round_id, spotify_uri) REFERENCES submissions(round_id, spotify_uri));"""

INSERT_VOTE = """INSERT INTO votes (created, round_id, spotify_uri, updated, voter_id, weight)
                    VALUES (%s, %s, %s, %s, %s, %s);"""

SELECT_SUBMISSIONS_WITH_VOTES = """SELECT submissions.spotify_uri as uri,
                                          su.id as submitter_id,
                                          su.name as submitter_name,
                                          vu.id as voter_id,
                                          vu.name as voter_name,
                                          votes.weight as points
                                   FROM submissions
                                   RIGHT JOIN votes ON votes.spotify_uri = submissions.spotify_uri
                                   LEFT JOIN users su ON su.id = submissions.submitter_id
                                   LEFT JOIN users vu ON vu.id = votes.voter_id
                                   WHERE submissions.round_id = %s
                                   ORDER BY points DESC;"""