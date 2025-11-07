-- 数据库：lab_physics
-- 用户表，仅包含需求字段

CREATE TABLE IF NOT EXISTS `users` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `openid` VARCHAR(64) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'normal',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uq_user_openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;