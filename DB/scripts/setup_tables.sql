CREATE TABLE `users`  (
  `id_vk` int NOT NULL,
  `profile_key` varchar(32) NULL UNIQUE COMMENT 'Profile auth key',
  `is_active` tinyint(1) NULL,
  `is_leader` tinyint(1) NULL,
  `is_officer` tinyint(1) NULL,
  `equipment` varchar(255) NULL COMMENT 'Array of item_id\'s',
  `class_id` int NULL,
  PRIMARY KEY (`id_vk`)
);

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

CREATE TABLE `items`  (
  `item_id` int NOT NULL,
  `item_name` varchar(64) NULL,
  `has_price` tinyint(1) NULL,
  PRIMARY KEY (`item_id`)
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