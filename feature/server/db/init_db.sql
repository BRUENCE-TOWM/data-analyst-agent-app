-- =============================================
-- 数据分析智能体项目 - 数据库初始化脚本
-- 存放路径：feature/server/db/init_db.sql
-- 适用数据库：MySQL 8.0+
-- =============================================

-- 1. 创建数据库（若不存在）
CREATE DATABASE IF NOT EXISTS data_analyst_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE data_analyst_agent;

-- 2. 用户信息表（user）
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名（唯一）',
  `password` varchar(100) NOT NULL COMMENT 'MD5加密密码',
  `email` varchar(100) DEFAULT NULL COMMENT '用户邮箱',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1-正常/0-禁用',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

-- 3. 任务记录表（task）
DROP TABLE IF EXISTS `task`;
CREATE TABLE `task` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `user_id` int(11) NOT NULL COMMENT '关联用户ID',
  `requirement` text NOT NULL COMMENT '用户需求',
  `generated_code` text DEFAULT NULL COMMENT '生成的Python代码',
  `status` varchar(20) NOT NULL DEFAULT 'pending' COMMENT '任务状态',
  `priority` varchar(10) NOT NULL DEFAULT 'normal' COMMENT '优先级',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_task_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务记录表';

-- 4. 执行日志表（execution_log）
DROP TABLE IF EXISTS `execution_log`;
CREATE TABLE `execution_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `task_id` int(11) NOT NULL COMMENT '关联任务ID',
  `output` text DEFAULT NULL COMMENT '执行结果',
  `error_msg` text DEFAULT NULL COMMENT '错误信息',
  `execute_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `execute_duration` float DEFAULT NULL COMMENT '执行耗时（秒）',
  PRIMARY KEY (`id`),
  KEY `idx_task_id` (`task_id`),
  CONSTRAINT `fk_log_task` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代码执行日志表';

-- 5. 插入测试数据
INSERT INTO `user` (`username`, `password`, `email`) VALUES 
('test_user', 'e10adc3949ba59abbe56e057f20f883e', 'test@example.com'); -- 密码：123456

-- 脚本执行完成
SELECT '数据库初始化完成' AS `result`;