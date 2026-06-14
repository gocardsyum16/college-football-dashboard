-- ==========================================
-- MSBA-692 Final Project
-- SEC & Big Ten College Football Analytics Dashboard
-- Initial PostgreSQL Load Script
-- Developer: Matt Kurtz
-- ==========================================

DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
    team_name VARCHAR(100) PRIMARY KEY,
    conference VARCHAR(50) NOT NULL,
    wins INTEGER NOT NULL,
    losses INTEGER NOT NULL,
    win_percentage NUMERIC(5,3) NOT NULL
);

-- Example Records

INSERT INTO teams (
    team_name,
    conference,
    wins,
    losses,
    win_percentage
)
VALUES
('Indiana','Big Ten',16,0,1.000),
('Oregon','Big Ten',13,2,0.867),
('Ohio State','Big Ten',12,2,0.857),
('Georgia','SEC',12,2,0.857),
('Alabama','SEC',11,2,0.846);

-- Validation Query

SELECT *
FROM teams;

-- Summary Statistics

SELECT
    conference,
    COUNT(*) AS total_teams,
    AVG(win_percentage) AS avg_win_percentage
FROM teams
GROUP BY conference;
