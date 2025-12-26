import sys
import os
# 确保app目录加入系统路径，适配config导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.pool import QueuePool
from datetime import datetime
# 从app/config导入配置
from config.db_config import DB_CONFIG, TABLES

# ====================== 初始化数据库连接 ======================
# 创建引擎（带连接池）- 修复：字符集通过URL指定，移除charset参数
engine = create_engine(
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4",
    poolclass=QueuePool,
    pool_size=DB_CONFIG['pool_size'],
    pool_recycle=DB_CONFIG['pool_recycle'],
    echo=DB_CONFIG['echo']
)

# 创建会话工厂
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# 线程安全的会话
ScopedSession = scoped_session(SessionFactory)

# 基础模型类
Base = declarative_base()

# ====================== 数据模型定义（ORM映射） ======================
class User(Base):
    """用户信息模型"""
    __tablename__ = TABLES["USER"]
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password = Column(String(100), nullable=False, comment="加密密码")
    email = Column(String(100), nullable=True, comment="用户邮箱")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    status = Column(Boolean, default=True, comment="用户状态：True-正常，False-禁用")
    
    # 关联任务
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

class Task(Base):
    """任务记录模型"""
    __tablename__ = TABLES["TASK"]
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="任务ID")
    user_id = Column(Integer, ForeignKey(f"{TABLES['USER']}.id"), nullable=False, comment="关联用户ID")
    requirement = Column(Text, nullable=False, comment="用户需求")
    generated_code = Column(Text, nullable=True, comment="生成的Python代码")
    status = Column(String(20), default="pending", nullable=False, comment="任务状态")
    priority = Column(String(10), default="normal", nullable=False, comment="任务优先级")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="tasks")
    execution_log = relationship("ExecutionLog", back_populates="task", cascade="all, delete-orphan")
    charts = relationship("Chart", back_populates="task", cascade="all, delete-orphan")

class ExecutionLog(Base):
    """代码执行日志模型"""
    __tablename__ = TABLES["EXECUTION_LOG"]
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    task_id = Column(Integer, ForeignKey(f"{TABLES['TASK']}.id"), nullable=False, comment="关联任务ID")
    output = Column(Text, nullable=True, comment="执行输出结果")
    error_msg = Column(Text, nullable=True, comment="执行错误信息")
    execute_time = Column(DateTime, default=datetime.now, comment="执行时间")
    execute_duration = Column(Float, nullable=True, comment="执行耗时（秒）")
    
    # 关联关系
    task = relationship("Task", back_populates="execution_log")

class Chart(Base):
    """图表存储模型"""
    __tablename__ = TABLES["CHART"] if "CHART" in TABLES else "chart"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="图表ID")
    task_id = Column(Integer, ForeignKey(f"{TABLES['TASK']}.id"), nullable=False, comment="关联任务ID")
    filename = Column(String(255), nullable=False, comment="图表文件名")
    chart_data = Column(LargeBinary(2**32), nullable=False, comment="图表二进制数据")  # 修改：支持最大4GB的二进制数据
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    task = relationship("Task", back_populates="charts")

# ====================== 数据库操作封装类 ======================
class DBService:
    def __init__(self):
        self.session = ScopedSession()
    
    def __del__(self):
        """销毁时关闭会话"""
        self.session.close()
    
    # -------------------- 用户表操作 --------------------
    def create_user(self, username: str, password: str, email: str = None) -> User:
        """创建用户"""
        try:
            user = User(
                username=username,
                password=password,
                email=email
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception as e:
            self.session.rollback()
            raise Exception(f"创建用户失败：{str(e)}")
    
    def get_user_by_username(self, username: str) -> User:
        """根据用户名查询用户"""
        return self.session.query(User).filter(User.username == username, User.status == True).first()
    
    def get_user_by_id(self, user_id: int) -> User:
        """根据ID查询用户"""
        return self.session.query(User).filter(User.id == user_id, User.status == True).first()
    
    # -------------------- 任务表操作 --------------------
    def create_task(self, user_id: int, requirement: str, priority: str = "normal") -> Task:
        """创建任务"""
        try:
            task = Task(
                user_id=user_id,
                requirement=requirement,
                priority=priority,
                status="pending"
            )
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
            return task
        except Exception as e:
            self.session.rollback()
            raise Exception(f"创建任务失败：{str(e)}")

    def update_task_code(self, task_id: int, generated_code: str, status: str = "success") -> bool:
        """更新任务生成的代码和状态"""
        try:
            task = self.session.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise ValueError(f"任务ID {task_id} 不存在")
            
            task.generated_code = generated_code
            task.status = status
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise Exception(f"更新任务代码失败：{str(e)}")
    
    def get_task_by_id(self, task_id: int) -> Task:
        """根据ID查询任务"""
        return self.session.query(Task).filter(Task.id == task_id).first()
    
    def get_user_tasks(self, user_id: int, page: int = 1, page_size: int = 10) -> tuple:
        """分页查询用户任务"""
        offset = (page - 1) * page_size
        query = self.session.query(Task).filter(Task.user_id == user_id).order_by(Task.create_time.desc())
        
        total = query.count()
        tasks = query.offset(offset).limit(page_size).all()
        return total, tasks
    
    # -------------------- 执行日志表操作 --------------------
    def create_execution_log(self, task_id: int, output: str = None, error_msg: str = None, execute_duration: float = None) -> ExecutionLog:
        """创建执行日志"""
        try:
            log = ExecutionLog(
                task_id=task_id,
                output=output,
                error_msg=error_msg,
                execute_duration=execute_duration
            )
            self.session.add(log)
            self.session.commit()
            self.session.refresh(log)
            return log
        except Exception as e:
            self.session.rollback()
            raise Exception(f"创建执行日志失败：{str(e)}")
    
    def get_log_by_task_id(self, task_id: int) -> ExecutionLog:
        """根据任务ID查询执行日志"""
        return self.session.query(ExecutionLog).filter(ExecutionLog.task_id == task_id).first()
    
    # -------------------- 图表表操作 --------------------
    def save_chart(self, task_id: int, filename: str, chart_data: bytes) -> Chart:
        """保存图表到数据库"""
        try:
            chart = Chart(
                task_id=task_id,
                filename=filename,
                chart_data=chart_data
            )
            self.session.add(chart)
            self.session.commit()
            self.session.refresh(chart)
            return chart
        except Exception as e:
            self.session.rollback()
            raise Exception(f"保存图表失败：{str(e)}")
    
    def get_charts_by_task_id(self, task_id: int) -> list:
        """根据任务ID查询所有图表"""
        return self.session.query(Chart).filter(Chart.task_id == task_id).all()
    
    def get_chart_by_id(self, chart_id: int) -> Chart:
        """根据图表ID查询图表"""
        return self.session.query(Chart).filter(Chart.id == chart_id).first()
    
    def get_chart_by_filename(self, task_id: int, filename: str) -> Chart:
        """根据任务ID和文件名查询图表"""
        return self.session.query(Chart).filter(
            Chart.task_id == task_id,
            Chart.filename == filename
        ).first()

# ====================== 测试代码 ======================
if __name__ == "__main__":
    # 初始化数据库（首次运行时执行）
    Base.metadata.create_all(engine)
    print("数据库表初始化完成（若不存在则创建）")
    
    # 测试DB操作
    db_service = DBService()
    
    # 1. 创建测试用户（密码MD5加密：123456 -> e10adc3949ba59abbe56e057f20f883e）
    try:
        user = db_service.create_user(
            username="test_user",
            password="e10adc3949ba59abbe56e057f20f883e",
            email="test@example.com"
        )
        print(f"创建用户成功：ID={user.id}, 用户名={user.username}")
    except Exception as e:
        print(f"创建用户失败：{e}")  # 重复创建会报错，属于正常现象
    
    # 2. 创建测试任务
    user = db_service.get_user_by_username("test_user")
    if user:
        task = db_service.create_task(
            user_id=user.id,
            requirement="计算1到100的累加和",
            priority="normal"
        )
        print(f"创建任务成功：ID={task.id}, 需求={task.requirement}")
        
        # 3. 更新任务代码
        db_service.update_task_code(
            task_id=task.id,
            generated_code="total = sum(range(1, 101))\nprint(total)",
            status="success"
        )
        print("更新任务代码成功")
        
        # 4. 创建执行日志
        log = db_service.create_execution_log(
            task_id=task.id,
            output="5050",
            execute_duration=0.01
        )
        print(f"创建执行日志成功：ID={log.id}, 输出={log.output}")