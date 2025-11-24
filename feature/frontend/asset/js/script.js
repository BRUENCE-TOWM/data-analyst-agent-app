document.addEventListener('DOMContentLoaded', function() {
    // 初始化图表（示例：销售TOP10柱状图）
    const initChart = () => {
        const chartDom = document.getElementById('salesChart');
        if (chartDom) {
            const myChart = echarts.init(chartDom);
            const option = {
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' }
                },
                grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                xAxis: { type: 'category', data: ['产品A', '产品B', '产品C', '产品D', '产品E', '产品F', '产品G', '产品H', '产品I', '产品J'] },
                yAxis: { type: 'value', axisLabel: { formatter: '{value:,}' } },
                series: [{
                    data: [12580, 10345, 8923, 7651, 6872, 5430, 4892, 3765, 2980, 1890],
                    type: 'bar',
                    itemStyle: { color: '#4F46E5' }
                }]
            };
            myChart.setOption(option);
            window.addEventListener('resize', () => myChart.resize());
        }
    };

    // 发送消息功能
    const sendMessage = () => {
        const userInput = document.getElementById('userInput');
        const inputText = userInput.value.trim();
        if (!inputText) return;

        // 添加用户消息到聊天区
        const chatContainer = document.getElementById('chatContainer');
        const userMessage = `
            <div class="message user-message">
                <div class="message-avatar">
                    <img src="../asset/image/user.png" alt="用户">
                </div>
                <div class="message-content">
                    <p>${inputText}</p>
                </div>
            </div>
        `;
        chatContainer.insertAdjacentHTML('beforeend', userMessage);

        // 清空输入框并滚动到底部
        userInput.value = '';
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // 模拟AI思考中...
        const loadingMessage = `
            <div class="message ai-message" id="loadingMsg">
                <div class="message-avatar">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="message-content">
                    <p><i class="fa-solid fa-spinner fa-spin"></i> 正在分析...</p>
                </div>
            </div>
        `;
        chatContainer.insertAdjacentHTML('beforeend', loadingMessage);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // 调用Python后端接口（实际项目中替换为真实接口）
        setTimeout(() => {
            // 移除加载状态
            document.getElementById('loadingMsg').remove();

            // 添加AI回复（含图表）
            const aiResponse = `
                <div class="message ai-message">
                    <div class="message-avatar">
                        <i class="fa-solid fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <p>根据您的需求，生成以下分析结果：</p>
                        <div class="chart-wrapper">
                            <div class="chart-inner" id="newChart" style="width:100%;height:300px;"></div>
                            <div class="chart-actions">
                                <button class="chart-btn"><i class="fa-solid fa-expand"></i> 放大</button>
                                <button class="chart-btn"><i class="fa-solid fa-chart-pie"></i> 切换图表</button>
                                <button class="chart-btn"><i class="fa-solid fa-download"></i> 下载</button>
                            </div>
                        </div>
                        <p>分析结论：数据呈现明显增长趋势，建议重点关注TOP3产品的库存管理。</p>
                    </div>
                </div>
            `;
            chatContainer.insertAdjacentHTML('beforeend', aiResponse);
            
            // 初始化新图表
            const newChartDom = document.getElementById('newChart');
            if (newChartDom) {
                const newChart = echarts.init(newChartDom);
                newChart.setOption({
                    tooltip: { trigger: 'axis' },
                    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
                    yAxis: { type: 'value' },
                    series: [{
                        data: [1200, 1900, 3000, 5000, 4500, 6000],
                        type: 'line',
                        smooth: true,
                        lineStyle: { color: '#4F46E5' },
                        itemStyle: { color: '#4F46E5' }
                    }]
                });
                window.addEventListener('resize', () => newChart.resize());
            }

            // 添加到历史任务
            const taskList = document.querySelector('.task-list');
            const now = new Date();
            const timeStr = `${now.getFullYear()}-${(now.getMonth()+1).toString().padStart(2,'0')}-${now.getDate().toString().padStart(2,'0')} ${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`;
            const newTask = `
                <div class="task-item completed" data-task-id="${Date.now()}">
                    <div class="task-status">
                        <i class="fa-solid fa-check text-success"></i>
                    </div>
                    <div class="task-info">
                        <div class="task-title">${inputText}</div>
                        <div class="task-time">${timeStr}</div>
                    </div>
                    <div class="task-actions">
                        <button class="re-run-btn"><i class="fa-solid fa-repeat"></i></button>
                    </div>
                </div>
            `;
            taskList.insertAdjacentHTML('afterbegin', newTask);

            // 滚动到底部
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 2000);
    };

    // 绑定发送按钮事件
    document.getElementById('sendBtn').addEventListener('click', sendMessage);

    // 绑定回车键发送
    document.getElementById('userInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 历史任务筛选
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            document.querySelectorAll('.task-item').forEach(item => {
                if (filter === 'all' || item.classList.contains(filter)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // 重新执行历史任务
    document.addEventListener('click', (e) => {
        if (e.target.closest('.re-run-btn')) {
            const taskItem = e.target.closest('.task-item');
            const taskTitle = taskItem.querySelector('.task-title').textContent;
            document.getElementById('userInput').value = taskTitle;
        }
    });

    // 初始化页面图表
    initChart();
});