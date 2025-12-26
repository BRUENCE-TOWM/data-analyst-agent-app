from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    # 替换为你的MySQL密码，先不创建表（避免报错）
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/data_analytics_db?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    # 暂不创建表，先保证服务启动