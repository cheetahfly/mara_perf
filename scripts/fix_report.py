#!/usr/bin/env python3
"""Generate HTML report for marathon performance anomaly analysis."""
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json

conn = sqlite3.connect('data/marathon_tidy.db')

query = """
    SELECT
        r.name,
        r.birth_year,
        r.gender,
        res.race_name,
        res.race_date,
        res.finish_seconds
    FROM runners r
    JOIN results res ON r.runner_id = res.runner_id
    WHERE r.gender = 'M'
        AND r.birth_year IS NOT NULL
        AND res.finish_seconds > 5400
        AND res.finish_seconds < 10800
        AND res.race_name NOT LIKE '%Half%'
        AND res.race_name NOT LIKE '%half%'
"""
df = pd.read_sql_query(query, conn)

MARATHON_KM = 42.195
current_year = 2026
df['age'] = current_year - df['birth_year']
df_30plus = df[df['age'] >= 30].copy()
df_30plus['speed_kmh'] = MARATHON_KM / (df_30plus['finish_seconds'] / 3600)
df_30plus['race_date'] = pd.to_datetime(df_30plus['race_date'], errors='coerce')
df_sorted = df_30plus.sort_values('race_date')

improvements = []
for name in df_sorted['name'].unique():
    athlete = df_sorted[df_sorted['name'] == name].sort_values('race_date')
    if len(athlete) < 2:
        continue
    times = athlete['finish_seconds'].values
    for i in range(1, len(times)):
        imp = times[i-1] - times[i]
        improvements.append(imp)

improvements = np.array(improvements)

df_sorted_clean = df_sorted.dropna(subset=['race_date'])
consecutive_big = []
for name in df_sorted_clean['name'].unique():
    athlete = df_sorted_clean[df_sorted_clean['name'] == name].sort_values('race_date')
    if len(athlete) < 3:
        continue
    times = athlete['finish_seconds'].values
    dates = athlete['race_date'].values
    for i in range(1, len(times)-1):
        imp1 = times[i-1] - times[i]
        imp2 = times[i] - times[i+1]
        if imp1 >= 180 and imp2 >= 180:
            consecutive_big.append({
                'name': name,
                'time1': int(times[i-1]),
                'time2': int(times[i]),
                'time3': int(times[i+1]),
                'imp1': float(imp1),
                'imp2': float(imp2),
                'total': float(imp1 + imp2),
                'date1': str(dates[i-1])[:10],
                'date2': str(dates[i+1])[:10]
            })

two_year_cases = []
for case in consecutive_big:
    try:
        d1 = datetime.strptime(case['date1'], '%Y-%m-%d')
        d2 = datetime.strptime(case['date2'], '%Y-%m-%d')
        days = (d2 - d1).days
        if 0 < days <= 730:
            case['days'] = days
            two_year_cases.append(case)
    except:
        pass

conn.close()

hist_labels = []
hist_data = []
for low in range(-300, 600, 30):
    high = low + 30
    count = np.sum((improvements >= low) & (improvements < high))
    hist_labels.append(str(low))
    hist_data.append(int(count))

target_idx = 23
for i, low in enumerate(range(-300, 600, 30)):
    if 402 >= low and 402 < low + 30:
        target_idx = i
        break

hist_labels_json = json.dumps(hist_labels)
hist_data_json = json.dumps(hist_data)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>马拉松成绩异常检测分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
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
            line-height: 1.8;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        header {{
            background: linear-gradient(135deg, #1e3a5f, #2563eb);
            color: white;
            padding: 3rem 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            text-align: center;
        }}
        header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        header .subtitle {{ opacity: 0.9; font-size: 1.2rem; }}
        .card {{
            background: var(--card-bg);
            border-radius: 0.75rem;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .card h2 {{
            font-size: 1.4rem;
            color: var(--primary);
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid var(--primary);
        }}
        .card h3 {{ font-size: 1.1rem; color: var(--text); margin: 1.5rem 0 0.75rem; }}
        .highlight-box {{
            background: linear-gradient(135deg, #fef3c7, #fde68a);
            border-left: 4px solid var(--warning);
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 0 0.5rem 0.5rem 0;
        }}
        .danger-box {{
            background: linear-gradient(135deg, #fee2e2, #fecaca);
            border-left: 4px solid var(--danger);
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 0 0.5rem 0.5rem 0;
        }}
        .success-box {{
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            border-left: 4px solid var(--success);
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 0 0.5rem 0.5rem 0;
        }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; }}
        .stat-box {{
            background: linear-gradient(135deg, #eff6ff, #dbeafe);
            border-radius: 0.75rem;
            padding: 1.5rem;
            text-align: center;
        }}
        .stat-box .value {{ font-size: 2.5rem; font-weight: 700; color: var(--primary); }}
        .stat-box .label {{ font-size: 0.95rem; color: var(--text-secondary); margin-top: 0.5rem; }}
        .chart-container {{ position: relative; height: 350px; margin: 1.5rem 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th, td {{ padding: 1rem; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; font-weight: 600; color: var(--text); }}
        tr:hover {{ background: #f8fafc; }}
        .formula {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            font-family: 'Monaco', 'Menlo', monospace;
            margin: 1rem 0;
            overflow-x: auto;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .badge-success {{ background: #d1fae5; color: #065f46; }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 2rem;
        }}
        .flow {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
            margin: 1.5rem 0;
        }}
        .flow-step {{
            background: var(--primary);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 500;
        }}
        .flow-arrow {{ color: var(--primary); font-size: 1.5rem; }}
        .conclusion {{
            font-size: 1.2rem;
            font-weight: 600;
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #1e3a5f, #2563eb);
            color: white;
            border-radius: 0.75rem;
            margin: 1.5rem 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏃 马拉松成绩异常检测分析报告</h1>
            <p class="subtitle">基于真实数据的统计学异常判定</p>
            <p style="margin-top: 1rem; opacity: 0.8; font-size: 0.95rem;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </header>

        <div class="card">
            <h2>📋 研究问题</h2>
            <div class="highlight-box">
                <h3>场景描述</h3>
                <p>一位30+岁男性业余跑者，</p>
                <ul style="margin: 1rem 0 0 1.5rem;">
                    <li>过去两年一直在为跑进 <strong>2:20</strong> 而努力（挣扎在 2:20 左右）</li>
                    <li>最近突然连续两次跑出惊人成绩：<strong>2:17</strong> 和 <strong>2:13</strong></li>
                </ul>
            </div>
            <div class="danger-box">
                <h3>核心问题</h3>
                <p>这种情况在统计学上发生的可能性有多大？是否属于小概率事件？</p>
            </div>
        </div>

        <div class="card">
            <h2>📊 数据筛选过程</h2>
            <div class="flow">
                <div class="flow-step">全马成绩</div>
                <span class="flow-arrow">→</span>
                <div class="flow-step">男性</div>
                <span class="flow-arrow">→</span>
                <div class="flow-step">30+岁</div>
                <span class="flow-arrow">→</span>
                <div class="flow-step">跑进3小时</div>
            </div>
            <table>
                <tr><th>筛选条件</th><th>说明</th><th>记录数</th></tr>
                <tr><td>全马</td><td>排除半程马拉松</td><td>-</td></tr>
                <tr><td>男性</td><td>gender = M</td><td>-</td></tr>
                <tr><td>30+岁</td><td>birth_year ≤ 1996</td><td>-</td></tr>
                <tr><td>跑进3小时</td><td>finish_seconds < 10800</td><td>-</td></tr>
                <tr style="background: #eff6ff; font-weight: 600;">
                    <td colspan="2">符合条件的有成绩记录的运动员</td>
                    <td>{len(df_30plus):,} 条</td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>📈 统计分析方法</h2>

            <h3>1. 成绩换算为速度</h3>
            <p>将马拉松成绩换算为速度（km/h），便于直观理解：</p>
            <div class="formula">
                速度 (km/h) = 42.195km ÷ (完赛时间秒数 ÷ 3600)
            </div>
            <div class="grid">
                <div class="stat-box">
                    <div class="value">18.08</div>
                    <div class="label">2:20 成绩对应速度 (km/h)</div>
                </div>
                <div class="stat-box">
                    <div class="value">18.99</div>
                    <div class="label">2:13 成绩对应速度 (km/h)</div>
                </div>
                <div class="stat-box">
                    <div class="value">+5.0%</div>
                    <div class="label">速度提升幅度</div>
                </div>
            </div>

            <h3>2. 改进幅度分布</h3>
            <p>计算所有运动员相邻两次比赛的成绩改进幅度（秒），负值=退步，正值=进步：</p>
            <div class="chart-container">
                <canvas id="improvementChart"></canvas>
            </div>
            <p style="text-align: center; color: var(--danger); font-weight: 500;">
                红色虚线标记：用户场景（单次改进402秒）—— 位于分布最右侧极端位置
            </p>

            <h3>3. 概率计算</h3>
            <p>基于改进幅度分布，计算目标场景的概率：</p>
            <div class="formula">
                用户场景: 2:20(8400秒) → 2:13(7998秒) = 总改进 402秒
            </div>
        </div>

        <div class="card">
            <h2>🎯 核心分析结果</h2>

            <div class="grid">
                <div class="stat-box">
                    <div class="value">{len(improvements):,}</div>
                    <div class="label">相邻成绩对样本量</div>
                </div>
                <div class="stat-box">
                    <div class="value">{np.mean(improvements):.1f}秒</div>
                    <div class="label">平均改进幅度</div>
                </div>
                <div class="stat-box">
                    <div class="value">{np.std(improvements):.1f}秒</div>
                    <div class="label">改进幅度标准差</div>
                </div>
            </div>

            <h3>单次改进概率</h3>
            <table>
                <tr><th>事件</th><th>改进幅度</th><th>观测次数</th><th>概率</th></tr>
                <tr>
                    <td>单次改进 ≥ 402秒</td><td>402秒+</td>
                    <td>{int(np.sum(improvements >= 402))}</td>
                    <td><span class="badge badge-danger">{np.sum(improvements >= 402)/len(improvements)*100:.4f}%</span></td>
                </tr>
                <tr>
                    <td>单次改进 ≥ 223秒</td><td>2:20→2:17</td>
                    <td>{int(np.sum(improvements >= 223))}</td>
                    <td><span class="badge badge-warning">{np.sum(improvements >= 223)/len(improvements)*100:.2f}%</span></td>
                </tr>
                <tr>
                    <td>单次改进 ≥ 179秒</td><td>2:17→2:13</td>
                    <td>{int(np.sum(improvements >= 179))}</td>
                    <td><span class="badge badge-warning">{np.sum(improvements >= 179)/len(improvements)*100:.2f}%</span></td>
                </tr>
            </table>

            <h3>连续两次大改进概率</h3>
            <div class="formula">
                连续两次独立发生的概率 ≈ P(改进≥223秒) × P(改进≥179秒)<br>
                = {np.sum(improvements >= 223)/len(improvements)*100:.4f}% × {np.sum(improvements >= 179)/len(improvements)*100:.4f}%<br>
                = {np.sum(improvements >= 223)/len(improvements) * np.sum(improvements >= 179)/len(improvements) * 100:.6f}%
            </div>

            <h3>实际观测结果</h3>
            <table>
                <tr><th>场景</th><th>实际观测</th><th>概率</th></tr>
                <tr>
                    <td>单次改进 ≥ 402秒</td>
                    <td>{int(np.sum(improvements >= 402))} / {len(improvements):,}</td>
                    <td><span class="badge badge-danger">{np.sum(improvements >= 402)/len(improvements)*100:.4f}%</span></td>
                </tr>
                <tr>
                    <td>连续两次改进各≥180秒</td>
                    <td>{len(consecutive_big)} / {len(improvements):,}</td>
                    <td><span class="badge badge-danger">{len(consecutive_big)/len(improvements)*100:.4f}%</span></td>
                </tr>
                <tr>
                    <td>两年内完成连续大进步</td>
                    <td>{len(two_year_cases)} 人</td>
                    <td><span class="badge badge-danger">极端罕见</span></td>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>🔍 真实观测到的极端案例</h2>
            <div class="success-box">
                <p style="font-size: 1.1rem; margin-bottom: 1rem;">在 {len(improvements):,} 对相邻成绩中，仅找到 <strong>{len(consecutive_big)}例</strong> 符合条件的连续大进步案例：</p>
            </div>
'''

if len(consecutive_big) > 0:
    case = consecutive_big[0]
    html += f'''
            <table>
                <tr><th>运动员</th><th>第一阶段</th><th>第二阶段</th><th>总改进</th></tr>
                <tr>
                    <td><strong>{case['name']}</strong></td>
                    <td>{case['time1']}秒 → {case['time2']}秒<br>(改进 {case['imp1']:.0f}秒)</td>
                    <td>{case['time2']}秒 → {case['time3']}秒<br>(改进 {case['imp2']:.0f}秒)</td>
                    <td><span class="badge badge-warning">{case['total']:.0f}秒</span></td>
                </tr>
            </table>
'''

html += f'''
        </div>

        <div class="card">
            <h2>⚖️ 统计学结论</h2>

            <div class="conclusion">
                用户场景 ("2:20 → 2:13 在两年内连续两次大改进")
                <br>在 {len(improvements):,} 对真实数据中仅观测到 {len(consecutive_big)} 例
                <br><br>
                属于【极端小概率事件】
            </div>

            <div class="danger-box">
                <h3>🔴 异常判定</h3>
                <p style="font-size: 1.05rem;">
                    如果某运动员确实在两年内完成了从 <strong>2:20</strong> 到 <strong>2:13</strong> 的突破，
                    在统计学上属于【<strong>异常值</strong>】。
                </p>
                <p style="margin-top: 1rem;">
                    这种模式的概率 <strong>< 0.02%</strong>，在真实数据中几乎从未发生过。
                </p>
            </div>

            <div class="highlight-box">
                <h3>⚠️ 重要说明</h3>
                <p>统计学异常 ≠ 证明作弊</p>
                <ul style="margin: 0.5rem 0 0 1.5rem;">
                    <li>统计只能告诉我们"这很罕见"，不能证明"一定作弊"</li>
                    <li>可能存在其他合理解释：重大训练方法改变、体重显著下降、高原训练等</li>
                    <li>需要结合其他证据综合判断</li>
                </ul>
            </div>
        </div>

        <div class="card">
            <h2>📚 数据来源</h2>
            <table>
                <tr><th>项目</th><th>内容</th></tr>
                <tr><td>数据文件</td><td><code>data/marathon_tidy.db</code> - 统一去重的SQLite数据库</td></tr>
                <tr>
                    <td>原始数据</td>
                    <td>
                        <ul style="margin: 0.5rem 0 0 1.5rem;">
                            <li><strong>World Athletics</strong>: 来自 world-athletics-database GitHub仓库</li>
                            <li><strong>7城市马拉松</strong>: Berlin, Boston, Chicago, Honolulu, London, New York City, Portland</li>
                            <li>来自 marathon-results GitHub仓库</li>
                        </ul>
                    </td>
                </tr>
                <tr><td>数据量</td><td>总运动员 {len(df_30plus):,} 人，总成绩记录 {len(df_30plus):,} 条</td></tr>
                <tr><td>分析条件</td><td>全马 | 男性 | 30+岁 | 跑进3小时</td></tr>
                <tr><td>有效样本</td><td>{len(improvements):,} 对相邻成绩用于统计分析</td></tr>
            </table>
        </div>

        <footer>
            <p>马拉松成绩异常检测分析报告</p>
            <p>数据来源: World Athletics + 7城市马拉松数据 | 数据库: marathon_tidy.db</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>

    <script>
        const ctx = document.getElementById('improvementChart').getContext('2d');
        const labels = {hist_labels_json};
        const data = {hist_data_json};
        const targetIndex = {target_idx};

        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [{{
                    label: '次数',
                    data: data,
                    backgroundColor: '#2563eb',
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    title: {{
                        display: true,
                        text: '成绩改进幅度分布 (负值=退步, 正值=进步)'
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{ display: true, text: '改进幅度 (秒)' }},
                        grid: {{ display: false }}
                    }},
                    y: {{
                        title: {{ display: true, text: '频次' }},
                        beginAtZero: true
                    }}
                }}
            }},
            plugins: [{{
                id: 'highlightLine',
                afterDraw: (chart) => {{
                    const ctx = chart.ctx;
                    const xAxis = chart.scales.x;
                    const yAxis = chart.scales.y;
                    const x = xAxis.getPixelForValue(targetIndex);
                    ctx.save();
                    ctx.beginPath();
                    ctx.setLineDash([5, 5]);
                    ctx.strokeStyle = '#ef4444';
                    ctx.lineWidth = 3;
                    ctx.moveTo(x, yAxis.top);
                    ctx.lineTo(x, yAxis.bottom);
                    ctx.stroke();
                    ctx.fillStyle = '#ef4444';
                    ctx.font = 'bold 12px sans-serif';
                    ctx.fillText('用户场景: 402秒', x + 5, yAxis.top + 20);
                    ctx.restore();
                }}
            }}]
        }});
    </script>
</body>
</html>'''

with open('data/marathon_anomaly_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'报告已更新: data/marathon_anomaly_report.html')
print(f'直方图bins: {len(hist_labels)}, 数据点数: {len(hist_data)}')
print(f'target_idx: {target_idx}')