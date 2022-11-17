-- ----------------------------
--  Creating (or replacing) database
-- ----------------------------

-- DROP DATABASE IF EXISTS `kitty_pit`;
-- CREATE DATABASE `kitty_pit`;
USE `kitty_pit`;

-- ----------------------------
--  Creating users for replication from master and code operational user
-- ----------------------------

# User for local replication. Primary (master) and replica (slave) servers must be configured.
-- CREATE USER IF NOT EXISTS `replicator`@`192.168.1.%` IDENTIFIED BY 'password';
-- GRANT Replication Slave ON *.* TO `replicator`@`192.168.1.%`;

# This user will connects from code, so the same parameters you should put in your .env file
-- CREATE USER IF NOT EXISTS `kitty_pit`@`localhost` IDENTIFIED BY 'password';
GRANT INSERT, SELECT, UPDATE ON `kitty_pit`.* TO `kitty_pit`@`localhost`;


-- ----------------------------
-- Table structure for users
-- ----------------------------

CREATE TABLE `users`  (
  `id_vk` int NOT NULL,
  `profile_key` varchar(32) NULL UNIQUE COMMENT 'Profile auth key',
  `is_active` tinyint(1) NULL,
  `is_leader` tinyint(1) NULL,
  `is_officer` tinyint(1) NULL,
  `equipment` varchar(255) NULL COMMENT 'Array of item_id\'s',
  `class_id` int NULL,
  `balance` int NULL DEFAULT 0,
  PRIMARY KEY (`id_vk`)
);

-- ----------------------------
-- Table structure for user_data
-- ----------------------------
CREATE TABLE `user_data`  (
  `id_vk` int NOT NULL,
  `level` int NULL,
  `attack` int NULL,
  `defence` int NULL,
  `strength` int NULL,
  `agility` int NULL,
  `endurance` int NULL,
  `luck` int NULL,
  `accuracy` int NULL COMMENT 'Can get only via profile',
  `concentration` int NULL COMMENT 'Can get only via profile',
  `last_update` DATETIME DEFAULT NOW(),
  PRIMARY KEY (`id_vk`)
);

-- ----------------------------
-- Table structure for items
-- ----------------------------
CREATE TABLE `items`  (
  `item_id` int NOT NULL,
  `item_name` varchar(64) NULL,
  `has_price` tinyint(1) NULL,
  PRIMARY KEY (`item_id`)
);

/* This is temporary tables for testing

CREATE TABLE `kitty_pit`.`roles`  (
  `role_id` int NOT NULL,
  `role_name` varchar(63) NOT NULL,
  `parent_role_id` int NULL,
  PRIMARY KEY (`role_id`),
  CONSTRAINT `parent_role` FOREIGN KEY (`parent_role_id`) REFERENCES `kitty_pit`.`roles` (`role_id`) ON UPDATE CASCADE ON DELETE NO ACTION
);

CREATE TABLE `buff_types`  (
  `type_id` int NOT NULL,
  `buff_list` varchar(255) NOT NULL COMMENT 'JSON Keyboard',
  PRIMARY KEY (`type_id`)
);

INSERT INTO `buff_types` VALUES
                             (14088, 'очищение - снимает с цели все активные проклятия'),
                             (14093, 'проклятие боли, проклятие неудачи, проклятие добычи'),
                             (14256, 'Очищение огнем - наносит игроку травму'),
                             (14257, 'Очищение светом - снимает игроку травму'),
                             (14264, 'Благословение удачи, атаки, защиты, расы');

CREATE TABLE `buff_users`  (
  `id_vk` int NOT NULL,
  `token` varchar(255) NOT NULL,
  `class` int NOT NULL,
  `race_id_1` int NOT NULL,
  `race_id_2` int NULL,
  PRIMARY KEY (`id_vk`)
);
 */