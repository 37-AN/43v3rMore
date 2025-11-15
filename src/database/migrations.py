"""Database schema migrations."""

from loguru import logger

# SQL schema definitions for Supabase
# These would be executed in Supabase SQL Editor or via migration tools

USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    phone TEXT,
    plan TEXT NOT NULL CHECK (plan IN ('basic', 'pro', 'premium', 'bot', 'enterprise')),
    status TEXT NOT NULL CHECK (status IN ('active', 'paused', 'cancelled', 'trial')),
    telegram_id TEXT,
    whatsapp_number TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
"""

SUBSCRIPTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan TEXT NOT NULL,
    monthly_fee DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'ZAR',
    status TEXT NOT NULL CHECK (status IN ('active', 'paused', 'cancelled', 'past_due')),
    trial_end TIMESTAMPTZ,
    current_period_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_period_end TIMESTAMPTZ NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    payment_method TEXT,
    last_payment_date TIMESTAMPTZ,
    next_billing_date TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_next_billing ON subscriptions(next_billing_date);
"""

SIGNALS_TABLE = """
CREATE TABLE IF NOT EXISTS signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('BUY', 'SELL', 'HOLD')),
    confidence DECIMAL(5, 4) NOT NULL,
    entry_price DECIMAL(10, 5) NOT NULL,
    stop_loss DECIMAL(10, 5),
    take_profit DECIMAL(10, 5),
    risk_reward DECIMAL(5, 2),
    timeframe TEXT DEFAULT 'H1',
    reason TEXT,
    metadata JSONB DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'executed', 'hit_tp', 'hit_sl', 'expired')),
    result_pnl DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
"""

SIGNAL_DELIVERIES_TABLE = """
CREATE TABLE IF NOT EXISTS signal_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID NOT NULL REFERENCES signals(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel TEXT NOT NULL CHECK (channel IN ('telegram', 'whatsapp', 'email', 'sms')),
    status TEXT NOT NULL CHECK (status IN ('pending', 'sent', 'delivered', 'failed')),
    error_message TEXT,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deliveries_signal_id ON signal_deliveries(signal_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_user_id ON signal_deliveries(user_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_status ON signal_deliveries(status);
"""

ANALYTICS_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    data JSONB DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON analytics_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON analytics_events(user_id);
"""

PAYMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'ZAR',
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    payment_method TEXT NOT NULL,
    transaction_id TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at DESC);
"""

LEAD_SCORES_TABLE = """
CREATE TABLE IF NOT EXISTS lead_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    source TEXT NOT NULL,
    score INTEGER DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
    stage TEXT DEFAULT 'new' CHECK (stage IN ('new', 'contacted', 'qualified', 'converted', 'lost')),
    interests TEXT[],
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_leads_email ON lead_scores(email);
CREATE INDEX IF NOT EXISTS idx_leads_score ON lead_scores(score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_stage ON lead_scores(stage);
"""

# Row Level Security (RLS) policies
RLS_POLICIES = """
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE signal_deliveries ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY users_select_own ON users
    FOR SELECT USING (auth.uid()::text = id::text);

-- Users can update their own data
CREATE POLICY users_update_own ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Users can read their own subscriptions
CREATE POLICY subscriptions_select_own ON subscriptions
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- Anyone can read signals (they're broadcast)
CREATE POLICY signals_select_all ON signals
    FOR SELECT TO authenticated USING (true);

-- Users can read their own signal deliveries
CREATE POLICY deliveries_select_own ON signal_deliveries
    FOR SELECT USING (auth.uid()::text = user_id::text);
"""

# Database functions
DB_FUNCTIONS = """
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON lead_scores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""


class Migration:
    """Database migration manager."""

    @staticmethod
    def get_all_schemas() -> str:
        """
        Get all schema definitions.

        Returns:
            Complete SQL schema

        Example:
            >>> schema = Migration.get_all_schemas()
            >>> # Execute in Supabase SQL Editor
        """
        return "\n\n".join(
            [
                "-- Quantum Trading AI Database Schema",
                "-- Generated: " + str(__import__("datetime").datetime.now(timezone.utc)),
                "",
                "-- Users Table",
                USERS_TABLE,
                "",
                "-- Subscriptions Table",
                SUBSCRIPTIONS_TABLE,
                "",
                "-- Signals Table",
                SIGNALS_TABLE,
                "",
                "-- Signal Deliveries Table",
                SIGNAL_DELIVERIES_TABLE,
                "",
                "-- Analytics Events Table",
                ANALYTICS_EVENTS_TABLE,
                "",
                "-- Payments Table",
                PAYMENTS_TABLE,
                "",
                "-- Lead Scores Table",
                LEAD_SCORES_TABLE,
                "",
                "-- Row Level Security",
                RLS_POLICIES,
                "",
                "-- Database Functions",
                DB_FUNCTIONS,
            ]
        )

    @staticmethod
    def save_schema_file(filepath: str = "database_schema.sql") -> None:
        """
        Save schema to SQL file.

        Args:
            filepath: Output file path

        Example:
            >>> Migration.save_schema_file("schema.sql")
        """
        try:
            schema = Migration.get_all_schemas()
            with open(filepath, "w") as f:
                f.write(schema)
            logger.info(f"Schema saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving schema: {e}")


if __name__ == "__main__":
    # Generate and print schema
    print(Migration.get_all_schemas())
