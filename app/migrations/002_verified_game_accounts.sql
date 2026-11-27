-- Existing manually entered identifiers retain their original, unverified status.
ALTER TABLE connected_accounts ADD COLUMN display_name text;
ALTER TABLE connected_accounts ADD COLUMN verified_at timestamptz;
CREATE UNIQUE INDEX verified_platform_identity ON connected_accounts(platform, platform_user_id)
    WHERE verified_at IS NOT NULL;

CREATE TABLE game_link_flows (
    state_hash bytea PRIMARY KEY,
    session_hash bytea NOT NULL REFERENCES sessions(token_hash) ON DELETE CASCADE,
    platform text NOT NULL,
    expires_at timestamptz NOT NULL,
    UNIQUE (session_hash, platform)
);
CREATE INDEX game_link_expiry ON game_link_flows(expires_at);
