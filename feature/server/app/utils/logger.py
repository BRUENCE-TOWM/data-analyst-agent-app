import logging
import os

# 创建logs目录（自动创建，无需手动建）
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)

# 配置日志：同时输出到文件和控制台
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "api.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """获取日志实例"""
    return logging.getLogger(name)