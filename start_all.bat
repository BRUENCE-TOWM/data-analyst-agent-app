@echo off
chcp 65001 >nul

echo =============================
echo 数据分析智能体多端应用启动脚本
echo =============================
echo.

REM 1. 设置项目根目录
set PROJECT_ROOT=c:\Users\12059\Desktop\Data-Analist\data-analyst-agent-app

REM 2. 启动FastAPI后端
echo 正在启动FastAPI后端服务...
start "FastAPI Backend" cmd /k "call conda activate data_agent && cd %PROJECT_ROOT%\feature\server\app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM 3. 等待2秒让后端完全启动
echo 等待后端服务启动...
timeout /t 2 /nobreak >nul

REM 4. 启动Flutter前端
echo 正在启动Flutter前端应用...
start "Flutter Frontend" cmd /k "cd %PROJECT_ROOT%\feature\client\flutter_app && flutter run"

REM 5. 显示启动完成信息
echo.
echo =============================
echo 所有服务已启动完成！
echo - FastAPI后端：http://localhost:8000
echo - API文档：http://localhost:8000/docs
echo - Flutter前端：将在模拟器/真机中启动
echo =============================
echo.
echo 按任意键关闭此窗口...
pause >nul