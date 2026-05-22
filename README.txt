===============================================================================
                    马拉松历史成绩数据库分析项目
                         Marathon Performance Analysis
===============================================================================

项目概述
--------
本项目整合了 World Athletics 和 7 大城市马拉松赛（Berlin, Boston, Chicago,
Honolulu, London, New York City, Portland）的历史成绩数据，构建统一数据库，
进行统计分析。

核心数据库
----------
data/marathon_tidy.db    - 统一去重后的 SQLite 数据库

  runners 表: 443,098 名运动员
    - runner_id   (INTEGER) - 运动员唯一ID
    - name        (TEXT)    - 姓名（大写标准化）
    - gender      (TEXT)    - 性别（M/F）
    - birth_year  (INTEGER) - 出生年份

  results 表: 698,431 条成绩记录
    - runner_id      (INTEGER) - 运动员ID（外键）
    - race_name      (TEXT)    - 赛事名称（含年份）
    - race_date       (TEXT)    - 比赛日期（ISO格式）
    - finish_seconds  (REAL)    - 完赛时间（秒）
    - source          (TEXT)    - 数据来源

数据来源分布
------------
  marathon_results: 678,568 条（7城市马拉松）
  world_athletics:  19,863 条（世界田径）

核心统计
--------
  完赛时间范围: 0 ~ 31,639 秒（约 8:47）
  中位时间:     14,513 秒（约 4:02）
  2:20内成绩:   7,906 条（仅限精英跑者）

分析报告
--------
data/marathon_anomaly_report.html  - 异常成绩分析报告（含图表）
  - 分析 30+ 男性跑者 2:20 → 2:17 → 2:13 的概率
  - 改进幅度分布直方图
  - 连续大幅改进检测

数据构建
--------
scripts/build_tidy_db.py   - 构建统一数据库（去重处理）
scripts/generate_new_report.py - 生成分析报告

运行环境
--------
  Python 3.8+
  R 4.0+ (可选，用于 tidyverse::glimpse 检查)

依赖包
------
  Python: pandas, sqlite3, numpy
  R:      tidyverse, DBI, RSQLite

使用示例
--------
# 构建数据库
python scripts/build_tidy_db.py

# 生成分析报告
python scripts/generate_new_report.py

# R语言检查数据库
Rscript -e "library(tidyverse); library(DBI); library(RSQLite);
db <- dbConnect(RSQLite::SQLite(), 'data/marathon_tidy.db');
runners <- tbl(db, 'runners'); glimpse(runners)"

注意事项
--------
1. 名字中的 '#' 前缀和尾部逗号已清洗（Excel/CSV解析问题）
2. 部分运动员 birth_year 缺失
3. marathon_anomaly_report.html 已内联 Chart.js，可离线使用

===============================================================================
