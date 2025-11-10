-- 数据库：lab_physics
-- 用户信息表（线上要求表名为 user_info）

CREATE TABLE IF NOT EXISTS `user_info` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `openid` VARCHAR(64) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'normal',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uq_user_openid` (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 绘图记录表：记录每个用户生成的图像及其所属实验
CREATE TABLE IF NOT EXISTS `plot_records` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` INT NOT NULL COMMENT '用户ID，关联 user_info.user_id',
  `experiment` VARCHAR(64) NOT NULL COMMENT '实验类型标识，如 thermal/solar-cell 等',
  `file_path` VARCHAR(255) NOT NULL COMMENT '服务器文件路径',
  `url` VARCHAR(255) NOT NULL COMMENT '对外访问URL（/static/...）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_plot_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;