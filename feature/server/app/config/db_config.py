# 数据库连接配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",          # 替换为你的MySQL用户名
    "password": "123456",  # 替换为你的MySQL密码
    "database": "data_analyst_agent",
    "pool_size": 10,         # 连接池大小
    "pool_recycle": 3600,    # 连接回收时间（秒）
    "echo": False            # 调试时设为True，打印SQL语句
}

# 表名常量
TABLES = {
    "USER": "user",
    "TASK": "task",
    "EXECUTION_LOG": "execution_log",
    "CHART": "chart"
}