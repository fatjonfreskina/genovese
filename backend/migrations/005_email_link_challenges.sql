CREATE TABLE `email_link_challenges` (
  `token_hash` VARCHAR(64) NOT NULL,
  `group_id` VARCHAR(36) NOT NULL,
  `code_hash` VARCHAR(64) NOT NULL,
  `attempts` INT NOT NULL DEFAULT 0,
  `expires_at` DATETIME NOT NULL,
  PRIMARY KEY (`token_hash`),
  KEY `ix_email_link_challenges_group_id` (`group_id`),
  KEY `ix_email_link_challenges_expires_at` (`expires_at`),
  CONSTRAINT `fk_email_link_challenges_group` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE
);

CREATE TABLE `email_link_rate_limits` (
  `key` VARCHAR(64) NOT NULL,
  `count` INT NOT NULL DEFAULT 0,
  `expires_at` DATETIME NOT NULL,
  PRIMARY KEY (`key`),
  KEY `ix_email_link_rate_limits_expires_at` (`expires_at`)
);
