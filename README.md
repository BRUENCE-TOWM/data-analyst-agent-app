# data-analyst-agent-app
8 周课程作业：数据分析师智能体 APP（前端 HTML + 后端 Python+MySQL）
# 数据分析智能体多端应用

一个基于大语言模型的数据分析智能体应用，支持多平台访问，提供代码生成、执行、可视化等功能。

## 功能特性

### 🎯 核心功能
- **智能代码生成**：基于数据分析需求自动生成Python代码
- **代码执行**：在线执行生成的代码，支持数据处理和可视化
- **任务管理**：保存和管理历史分析任务
- **多平台支持**：Web、Windows桌面应用、Android、iOS

### 🛠️ 技术特性
- **后端API**：FastAPI构建的高性能RESTful API
- **前端框架**：Flutter开发的跨平台应用
- **数据存储**：MySQL数据库持久化存储
- **AI驱动**：集成通义千问API实现智能代码生成
- **代码高亮**：支持Python代码语法高亮显示
- **文件上传**：支持上传数据文件进行分析

## 技术栈

### 后端技术栈
- **框架**：FastAPI 🏃
- **语言**：Python 3.9 🐍
- **数据库**：MySQL 🗄️
- **ORM**：SQLAlchemy 🔗
- **AI接口**：通义千问API 🧠
- **代码执行**：安全沙箱环境

### 前端技术栈
- **框架**：Flutter 3.38.4 📱
- **语言**：Dart 🎯
- **网络请求**：http 📡
- **状态管理**：Provider 🔄
- **代码高亮**：flutter_highlight 🌈
- **文件选择**：file_picker 📁

## 项目结构
data-analyst-agent-app/
├── .env                    # 环境变量配置文件
├── .gitignore              # Git忽略文件配置
├── LICENSE                 # 项目许可证
├── README.md               # 项目说明文档
├── conda_env.yml           # Conda环境配置文件
├── docs/                   # 项目文档目录
│   ├── 代码.docx            # 代码文档
│   ├── 代码.pdf             # 代码文档（PDF格式）
│   ├── 数据分析智能体多端开发概要设计说明书.docx  # 概要设计文档
│   ├── 数据分析智能体多端开发概要设计说明书.pdf   # 概要设计文档（PDF格式）
│   ├── 数据分析智能体多端开发项目 - 详细设计文档.pdf  # 详细设计文档
│   ├── 调研报告.docx        # 调研报告
│   ├── 调研报告.pdf         # 调研报告（PDF格式）
│   ├── 需求规格说明书（SRS）- 数据分析智能体多端开发（前四部分）1.docx  # 需求规格说明书
│   └── 需求规格说明书（SRS）- 数据分析智能体多端开发（前四部分）1.pdf   # 需求规格说明书（PDF格式）
├── feature/                # 主功能目录
│   ├── client/             # 客户端代码
│   │   ├── electron_desktop/  # Electron桌面应用（可选）
│   │   └── flutter_app/    # Flutter跨平台应用
│   │       ├── .dart_tool/  # Dart工具缓存
│   │       ├── .flutter-plugins-dependencies  # Flutter插件依赖信息
│   │       ├── .gitignore   # Flutter项目Git忽略配置
│   │       ├── .metadata    # Flutter项目元数据
│   │       ├── README.md    # Flutter项目说明
│   │       ├── analysis_options.yaml  # Dart代码分析配置
│   │       ├── android/     # Android平台代码
│   │       ├── build/       # 构建输出目录
│   │       ├── code_generator.iml  # IDE项目配置文件
│   │       ├── flutter_app.iml/  # IDE项目配置文件
│   │       ├── ios/         # iOS平台代码
│   │       ├── lib/         # Flutter核心代码
│   │       ├── linux/       # Linux平台代码
│   │       ├── macos/       # macOS平台代码
│   │       ├── pubspec.lock  # 依赖版本锁定文件
│   │       ├── pubspec.yaml  # Flutter依赖配置
│   │       ├── test/        # 测试代码
│   │       ├── web/         # Web平台代码
│   │       └── windows/     # Windows平台代码
│   └── server/              # 服务器端代码
│       ├── app/             # FastAPI应用主目录
│       │   ├── __pycache__/  # Python编译缓存
│       │   ├── api/         # API接口定义
│       │   │   ├── analysis.py  # 分析相关接口
│       │   │   ├── code_api.py  # 代码生成接口
│       │   │   ├── code_exec_api.py  # 代码执行接口
│       │   │   ├── task_api.py  # 任务管理接口
│       │   │   └── user.py  # 用户相关接口
│       │   ├── app/         # 应用核心配置
│       │   ├── backup.sql   # 数据库备份文件
│       │   ├── config/      # 配置文件
│       │   │   ├── database.py  # 数据库配置
│       │   │   └── db_config.py  # 数据库连接配置
│       │   ├── logs/        # 日志文件目录
│       │   ├── main.py      # FastAPI应用入口
│       │   ├── models/      # 数据模型
│       │   │   └── analysis_record.py  # 分析记录模型
│       │   ├── services/    # 业务逻辑服务
│       │   │   ├── code_executor.py  # 代码执行服务
│       │   │   ├── db_service.py  # 数据库服务
│       │   │   └── llm_service.py  # LLM服务（本地模型，未被生产使用）
│       │   └── utils/       # 工具函数
│       │       ├── auth.py  # 认证工具
│       │       └── logger.py  # 日志工具
│       ├── db/              # 数据库初始化脚本
│       │   └── init_db.sql  # 数据库初始化SQL
│       ├── run.py           # 后端运行脚本
│       ├── test_llm.py      # LLM测试脚本
│       └── test_local_qwen.py  # 本地千问模型测试脚本
├── start_all.bat           # Windows一键启动脚本
├── temp/                   # 临时文件目录
└── test_api.http           # API测试文件

## 快速开始

### 环境要求

#### 后端环境
- Python 3.9+
- MySQL 5.7+
- Conda（推荐）或虚拟环境

#### 前端环境
- Flutter SDK 3.0+
- Dart 3.0+
- 各平台开发环境（可选）

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/yourusername/data-analyst-agent-app.git
cd data-analyst-agent-app
```

#### 2. 配置后端环境

##### 使用Conda（推荐）
```bash
# 创建并激活环境
conda env create -f conda_env.yml
conda activate data_agent
```

##### 使用虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活环境（Windows）
venv\Scripts\activate

# 激活环境（Linux/macOS）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置数据库

1. 创建MySQL数据库
```sql
CREATE DATABASE data_analyst_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改数据库配置
编辑 `feature/server/app/config/db_config.py` 文件：
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",          # 替换为你的MySQL用户名
    "password": "123456",  # 替换为你的MySQL密码
    "database": "data_analyst_agent",
    "pool_size": 10,
    "pool_recycle": 3600,
    "echo": False
}
```

3. 初始化数据库
```bash
python feature/server/app/services/db_service.py
```

#### 4. 配置AI API

编辑 `feature/server/app/api/code_api.py` 文件，配置通义千问API密钥：
```python
# 通义千问API配置（兼容OpenAI接口）
THIRD_PARTY_API_KEY = "your-api-key"  # 替换为你的API密钥
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

### 运行项目

#### 使用启动脚本（Windows）
```bash
start_all.bat
```

#### 手动启动

1. 启动后端服务
```bash
cd feature/server/app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

2. 启动Flutter Web开发服务器
```bash
cd feature/client/flutter_app
flutter run -d chrome
```

3. 启动Windows桌面应用
```bash
cd feature/client/flutter_app
flutter run -d windows
```

## 访问地址

- **后端API**：http://localhost:8000
- **API文档**：http://localhost:8000/docs
- **Web前端**：将在Chrome浏览器中自动打开

## 部署方案

### 后端部署

#### 生产环境部署

1. 使用Gunicorn启动FastAPI
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

2. 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 前端部署

#### Web前端部署

1. 打包Web应用
```bash
cd feature/client/flutter_app
flutter build web --release
```

2. 部署到Nginx
将 `build/web` 目录下的文件复制到Nginx的网站根目录。

#### Windows桌面应用部署

1. 打包Windows应用
```bash
cd feature/client/flutter_app
flutter build windows --release
```

2. 分发应用
将 `build/windows/runner/Release/` 目录下的文件打包分发给用户。

## 主要API接口

### 代码生成接口
- **URL**: `/api/code/generate`
- **Method**: `POST`
- **Description**: 根据需求生成Python代码

### 代码执行接口
- **URL**: `/api/code/exec`
- **Method**: `POST`
- **Description**: 执行Python代码并返回结果

### 任务列表接口
- **URL**: `/api/task/list`
- **Method**: `POST`
- **Description**: 获取用户任务列表

### 任务详情接口
- **URL**: `/api/task/detail`
- **Method**: `POST`
- **Description**: 获取任务详情

## 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者：[Your Name]
- 项目地址：[https://github.com/yourusername/data-analyst-agent-app](https://github.com/yourusername/data-analyst-agent-app)

## 更新日志

### v1.0.0 (2025-12-24)
- 初始版本发布
- 支持代码生成、执行功能
- 支持多平台前端访问
- 集成通义千问API
