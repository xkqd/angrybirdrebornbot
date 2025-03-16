CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 0,
    point_balance INTEGER DEFAULT 0,
    last_claim INTEGER DEFAULT 0,
    voice_time INTEGER DEFAULT 0,
    messages INTEGER DEFAULT 0,
    last_voice_time INTEGER DEFAULT 0,
    defeed BOOLEAN DEFAULT 0,
    married_with INTEGER DEFAULT 0
);