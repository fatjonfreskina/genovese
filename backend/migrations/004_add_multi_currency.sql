-- Run once, after 001, 002 and 003, before deploying the multi-currency backend.
-- Existing amounts are already expressed in their group's currency: never convert them.
ALTER TABLE `groups`
    ADD COLUMN closing_balance_mode VARCHAR(10) NOT NULL DEFAULT 'separate';

ALTER TABLE expenses
    ADD COLUMN currency VARCHAR(3) NULL,
    ADD COLUMN expense_date DATE NULL,
    ADD COLUMN exchange_rate DECIMAL(24, 12) NULL,
    ADD COLUMN exchange_rate_date DATE NULL,
    ADD COLUMN exchange_rate_source VARCHAR(20) NULL;

UPDATE expenses AS e
JOIN `groups` AS g ON g.id = e.group_id
SET e.currency = g.currency,
    e.expense_date = COALESCE(DATE(e.created_at), CURRENT_DATE()),
    e.exchange_rate = 1,
    e.exchange_rate_date = COALESCE(DATE(e.created_at), CURRENT_DATE()),
    e.exchange_rate_source = 'identity';

ALTER TABLE expenses
    MODIFY COLUMN currency VARCHAR(3) NOT NULL,
    MODIFY COLUMN expense_date DATE NOT NULL;

ALTER TABLE settlements ADD COLUMN currency VARCHAR(3) NULL;

UPDATE settlements AS s
JOIN `groups` AS g ON g.id = s.group_id
SET s.currency = g.currency;

ALTER TABLE settlements MODIFY COLUMN currency VARCHAR(3) NOT NULL;
