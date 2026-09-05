-- Stop app writes and back up the database first. Use a MySQL client supporting
-- DELIMITER; abort on errors (do NOT use --force). The guard prevents the old
-- backend from interpreting original foreign amounts as the group currency.
DELIMITER //
CREATE PROCEDURE equa_rollback_004()
BEGIN
    IF EXISTS (
        SELECT 1 FROM expenses AS e
        JOIN `groups` AS g ON g.id = e.group_id
        WHERE e.currency <> g.currency
           OR e.exchange_rate IS NULL
           OR e.exchange_rate <> 1
           OR e.exchange_rate_source <> 'identity'
    ) OR EXISTS (
        SELECT 1 FROM settlements AS s
        JOIN `groups` AS g ON g.id = s.group_id
        WHERE s.currency <> g.currency
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Rollback 004 blocked: preserve multi-currency data and restore a compatible backup instead';
    END IF;

    ALTER TABLE settlements DROP COLUMN currency;
    ALTER TABLE expenses
        DROP COLUMN exchange_rate_source,
        DROP COLUMN exchange_rate_date,
        DROP COLUMN exchange_rate,
        DROP COLUMN expense_date,
        DROP COLUMN currency;
    ALTER TABLE `groups` DROP COLUMN closing_balance_mode;
END//
CALL equa_rollback_004()//
DROP PROCEDURE equa_rollback_004//
DELIMITER ;
