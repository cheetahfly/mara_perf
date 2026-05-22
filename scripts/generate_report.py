#!/usr/bin/env python3
"""Generate HTML data exploration report."""
import json
from datetime import datetime

# 读取统计数据
with open('data/exploration_stats.json', 'r', encoding='utf-8') as f:
    stats = json.load(f)

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>马拉松数据探索报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --primary: #2563eb;
            --secondary: #64748b;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-secondary: #64748b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
        header {{
            background: linear-gradient(135deg, var(--primary), #1d4ed8);
            color: white;
            padding: 3rem 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }}
        header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        header p {{ opacity: 0.9; font-size: 1.1rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }}
        .card {{
            background: var(--card-bg);
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .card h2 {{ font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 1rem; border-bottom: 2px solid var(--primary); padding-bottom: 0.5rem; }}
        .stat {{ text-align: center; padding: 1rem 0; }}
        .stat-value {{ font-size: 2.5rem; font-weight: 700; color: var(--primary); }}
        .stat-label {{ color: var(--text-secondary); font-size: 0.9rem; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }}
        .stat-item {{ text-align: center; }}
        .stat-item .value {{ font-size: 1.5rem; font-weight: 600; color: var(--primary); }}
        .stat-item .label {{ font-size: 0.8rem; color: var(--text-secondary); }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; font-weight: 600; }}
        tr:hover {{ background: #f8fafc; }}
        .chart-container {{ position: relative; height: 300px; margin-top: 1rem; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; }}
        .badge-success {{ background: #d1fae5; color: #065f46; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        .progress-bar {{ height: 24px; background: #e2e8f0; border-radius: 4px; overflow: hidden; margin: 0.25rem 0; }}
        .progress-fill {{ height: 100%; background: var(--primary); transition: width 0.3s; }}
        footer {{ text-align: center; padding: 2rem; color: var(--text-secondary); font-size: 0.9rem; }}
        .section {{ margin-bottom: 2rem; }}
        .section-title {{ font-size: 1.5rem; margin: 2rem 0 1rem; color: var(--text); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏃 马拉松数据探索报告</h1>
            <p>基于统一去重数据库的全面数据分析 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </header>

        <div class="grid">
            <div class="card">
                <h2>📊 核心指标</h2>
                <div class="stat">
                    <div class="stat-value">{stats['total_runners']:,}</div>
                    <div class="stat-label">运动员总数</div>
                </div>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="value">{stats['total_results']:,}</div>
                        <div class="label">成绩记录</div>
                    </div>
                    <div class="stat-item">
                        <div class="value">{stats['repeat_runners']:,}</div>
                        <div class="label">多次完赛运动员</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>👥 性别分布</h2>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="value">{stats['gender_dist'].get('M', 0):,}</div>
                        <div class="label">男性</div>
                    </div>
                    <div class="stat-item">
                        <div class="value">{stats['gender_dist'].get('F', 0):,}</div>
                        <div class="label">女性</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="genderChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2>📁 数据来源</h2>
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="value">{stats['source_dist'].get('marathon_results', 0):,}</div>
                        <div class="label">7城市马拉松</div>
                    </div>
                    <div class="stat-item">
                        <div class="value">{stats['source_dist'].get('world_athletics', 0):,}</div>
                        <div class="label">World Athletics</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="sourceChart"></canvas>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">⏱️ 成绩分布</h2>
            <div class="grid">
                <div class="card">
                    <h2>完赛时间分布 (全马 3:00-6:00)</h2>
                    <div class="chart-container">
                        <canvas id="timeDistChart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <h2>年度完赛趋势</h2>
                    <div class="chart-container">
                        <canvas id="yearTrendChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">🏅 最快成绩 TOP 20</h2>
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>姓名</th>
                            <th>成绩</th>
                            <th>赛事</th>
                            <th>性别</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for i, (name, time, race, gender) in enumerate(stats['fastest_times'][:20], 1):
    badge_class = 'badge-success' if time < '2:10:00' else ('badge-warning' if time < '2:20:00' else '')
    html += f"""                        <tr>
                            <td>{i}</td>
                            <td><strong>{name}</strong></td>
                            <td><span class="badge {badge_class}">{time}</span></td>
                            <td>{race}</td>
                            <td>{gender}</td>
                        </tr>
"""

html += """                    </tbody>
                </table>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">🏙️ 赛事分布 (Top 15)</h2>
            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>赛事</th>
                            <th>完赛人数</th>
                            <th>占比</th>
                        </tr>
                    </thead>
                    <tbody>
"""

total_results = stats['total_results']
for i, (race, cnt) in enumerate(stats['race_dist'][:15], 1):
    pct = cnt / total_results * 100
    html += f"""                        <tr>
                            <td>{i}</td>
                            <td>{race}</td>
                            <td>{cnt:,}</td>
                            <td>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {pct:.1f}%"></div>
                                </div>
                                {pct:.1f}%
                            </td>
                        </tr>
"""

html += """                    </tbody>
                </table>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">📈 运动员完赛次数分布</h2>
            <div class="grid">
                <div class="card">
                    <h2>完赛次数统计</h2>
                    <div class="chart-container">
                        <canvas id="recordsPerRunnerChart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <h2>出生年分布</h2>
                    <div class="chart-container">
                        <canvas id="birthYearChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <footer>
            <p>马拉松数据探索报告 | 数据来源: World Athletics + 7城市马拉松数据</p>
            <p>生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </footer>
    </div>

    <script>
        // 性别分布饼图
        new Chart(document.getElementById('genderChart'), {
            type: 'doughnut',
            data: {
                labels: ['男性', '女性'],
                datasets: [{
                    data: [""" + str(stats['gender_dist'].get('M', 0)) + """, """ + str(stats['gender_dist'].get('F', 0)) + """],
                    backgroundColor: ['#2563eb', '#ec4899']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        // 数据来源饼图
        new Chart(document.getElementById('sourceChart'), {
            type: 'doughnut',
            data: {
                labels: ['7城市马拉松', 'World Athletics'],
                datasets: [{
                    data: [""" + str(stats['source_dist'].get('marathon_results', 0)) + """, """ + str(stats['source_dist'].get('world_athletics', 0)) + """],
                    backgroundColor: ['#10b981', '#f59e0b']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        // 成绩分布柱状图
        new Chart(document.getElementById('timeDistChart'), {
            type: 'bar',
            data: {
                labels: """ + json.dumps([x[0] for x in stats['time_dist']]) + """,
                datasets: [{
                    label: '人数',
                    data: """ + json.dumps([x[1] for x in stats['time_dist']]) + """,
                    backgroundColor: '#2563eb'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });

        // 年度趋势图
        new Chart(document.getElementById('yearTrendChart'), {
            type: 'line',
            data: {
                labels: """ + json.dumps([str(x[0]) for x in stats['year_trend']]) + """,
                datasets: [{
                    label: '完赛人次',
                    data: """ + json.dumps([x[1] for x in stats['year_trend']]) + """,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: false } }
            }
        });

        // 完赛次数分布
        new Chart(document.getElementById('recordsPerRunnerChart'), {
            type: 'bar',
            data: {
                labels: """ + json.dumps([f"{x[0]}次" for x in stats['records_per_runner']]) + """,
                datasets: [{
                    label: '运动员数',
                    data: """ + json.dumps([x[1] for x in stats['records_per_runner']]) + """,
                    backgroundColor: '#8b5cf6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });

        // 出生年分布
        new Chart(document.getElementById('birthYearChart'), {
            type: 'line',
            data: {
                labels: """ + json.dumps([str(x[0]) for x in stats['birth_year_dist']]) + """,
                datasets: [{
                    label: '运动员数',
                    data: """ + json.dumps([x[1] for x in stats['birth_year_dist']]) + """,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    </script>
</body>
</html>"""

# 保存HTML报告
with open('data/marathon_exploration_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML报告已生成: data/marathon_exploration_report.html")
print(f"文件大小: {len(html) / 1024:.1f} KB")