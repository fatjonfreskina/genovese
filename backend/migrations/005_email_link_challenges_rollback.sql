-- Stop the updated backend / disable email first. Only temporary challenges and limits are removed.
DROP TABLE `email_link_challenges`;
DROP TABLE `email_link_rate_limits`;
