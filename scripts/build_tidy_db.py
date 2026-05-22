#!/usr/bin/env python3
"""Build a unified tidy database from all data sources - optimized version."""
import pandas as pd
import sqlite3
from datetime import datetime
import re
import os

print("=" * 60)
print("开始数据整合与去重 (优化版)")
print("=" * 60)

# ============ 1. 读取 World Athletics 数据 ============
print("\n[1] 读取 World Athletics 数据...")
df_wa = pd.read_csv("data/raw/data.csv", delimiter=";", low_memory=False)
print(f"  总行数: {len(df_wa)}")

# 筛选马拉松数据
df_wa_marathon = df_wa[df_wa['Event'].str.contains('Marathon', case=False, na=False)].copy()
print(f"  马拉松记录: {len(df_wa_marathon)}")

# ============ 2. 处理 WA 数据 ============
print("\n[2] 处理 WA 数据...")

def parse_time_vec(series):
    """Vectorized time parser."""
    def parse_single(x):
        if pd.isna(x):
            return None
        parts = str(x).strip().split(":")
        try:
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
        except:
            return None
        return None

    return series.apply(parse_single)

def parse_date_vec(series):
    """Vectorized date parser."""
    def parse_single(x):
        if pd.isna(x):
            return None
        x = str(x).strip()
        formats = ["%d %b %Y", "%Y-%m-%d", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(x, fmt).date()
            except:
                continue
        return None

    return series.apply(parse_single)

def normalize_name_vec(series):
    """Vectorized name normalizer."""
    return (series
            .fillna('')
            .astype(str)
            .str.upper()
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True))

# 标准化 WA 数据
df_wa_marathon['name'] = normalize_name_vec(df_wa_marathon['Competitor'])
df_wa_marathon['birth_year'] = pd.to_datetime(df_wa_marathon['DOB'], errors='coerce').dt.year.astype('Int64')
df_wa_marathon['finish_seconds'] = parse_time_vec(df_wa_marathon['Mark'])
df_wa_marathon['race_date'] = parse_date_vec(df_wa_marathon['Date'])
df_wa_marathon['race_name'] = df_wa_marathon['Venue'].fillna('').astype(str).str.strip()
df_wa_marathon['gender'] = df_wa_marathon['Sex'].map({'male': 'M', 'female': 'F'}).fillna('M')
df_wa_marathon['source'] = 'world_athletics'

# 过滤有效记录
wa_valid = df_wa_marathon.dropna(subset=['name', 'finish_seconds']).copy()
wa_valid = wa_valid[wa_valid['name'] != '']
print(f"  有效 WA 记录: {len(wa_valid)}")

# ============ 3. 读取 marathon_results ============
print("\n[3] 读取 7城市马拉松数据...")
all_dfs = []
marathon_dir = "data/raw/marathon_results"

for city in sorted(os.listdir(marathon_dir)):
    city_path = os.path.join(marathon_dir, city)
    if not os.path.isdir(city_path):
        continue

    for f in sorted(os.listdir(city_path)):
        if not f.endswith('.csv'):
            continue

        year_match = re.search(r'(\d{4})', f)
        year = year_match.group(1) if year_match else None

        df = pd.read_csv(os.path.join(city_path, f), low_memory=False)
        df['race_year'] = year
        df['city'] = city
        all_dfs.append(df)
        print(f"  {city}/{f}: {len(df)} rows")

df_mr = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
print(f"  Marathon Results 总记录: {len(df_mr)}")

# ============ 4. 处理 marathon_results ============
print("\n[4] 处理 marathon_results...")

def parse_mr_time(x):
    if pd.isna(x):
        return None
    parts = str(x).strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except:
        return None
    return None

df_mr['name'] = normalize_name_vec(df_mr['first_name'].fillna('') + ' ' + df_mr['last_name'].fillna(''))
df_mr['finish_seconds'] = df_mr['time_full'].apply(parse_mr_time)
df_mr['race_name'] = df_mr['city'] + ' (' + df_mr['race_year'].fillna('') + ')'
df_mr['source'] = 'marathon_results'
df_mr['race_date'] = None
df_mr['birth_year'] = pd.NA

gender_map = {'M': 'M', 'male': 'M', 'F': 'F', 'female': 'F'}
df_mr['gender'] = df_mr['gender'].map(gender_map).fillna('M')

# 过滤有效记录
mr_valid = df_mr.dropna(subset=['name', 'finish_seconds']).copy()
mr_valid = mr_valid[(mr_valid['name'] != '') & (mr_valid['name'] != 'NAN NAN')]
print(f"  有效 MR 记录: {len(mr_valid)}")

# ============ 5. 合并数据 ============
print("\n[5] 合并数据...")

cols = ['name', 'birth_year', 'gender', 'finish_seconds', 'race_name', 'race_date', 'source']

wa_subset = wa_valid[cols].copy()
mr_subset = mr_valid[cols].copy()

df_all = pd.concat([wa_subset, mr_subset], ignore_index=True)
print(f"  合并后总记录: {len(df_all)}")

# ============ 6. 去重 ============
print("\n[6] 数据去重...")

before_dedup = len(df_all)
df_unique = df_all.drop_duplicates(subset=['name', 'finish_seconds', 'race_name'], keep='first')
print(f"  按 (name, time, race) 去重: {before_dedup} -> {len(df_unique)}")

# ============ 7. 构建运动员表 ============
print("\n[7] 构建运动员表...")

runner_summary = df_unique.groupby('name').agg({
    'birth_year': 'first',
    'gender': 'first'
}).reset_index()

# 分配 runner_id
runner_summary['runner_id'] = range(1, len(runner_summary) + 1)
print(f"  去重后运动员数: {len(runner_summary)}")

# ============ 8. 构建成绩表 ============
print("\n[8] 构建成绩表...")

df_results = df_unique.merge(runner_summary[['name', 'runner_id']], on='name', how='left')

# 最终去重
df_results_final = df_results.drop_duplicates(
    subset=['runner_id', 'race_name', 'race_date', 'finish_seconds'],
    keep='first'
)

print(f"  最终成绩记录: {len(df_results_final)}")

# ============ 9. 保存到数据库 ============
print("\n[9] 保存到数据库...")

db_path = "data/marathon_tidy.db"
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)

# 写入运动员
runner_summary[['runner_id', 'name', 'gender', 'birth_year']].to_sql(
    'runners', conn, index=False, if_exists='replace'
)

# 写入成绩
df_results_final[['runner_id', 'race_name', 'race_date', 'finish_seconds', 'source']].to_sql(
    'results', conn, index=False, if_exists='replace'
)

# 创建索引
cursor = conn.cursor()
cursor.execute("CREATE INDEX idx_results_runner ON results(runner_id)")
cursor.execute("CREATE INDEX idx_results_race ON results(race_name)")
conn.commit()
conn.close()

print(f"\n{'='*60}")
print("数据库创建完成!")
print(f"{'='*60}")

# 验证
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM runners")
runners_count = cursor.fetchone()[0]
print(f"运动员数: {runners_count}")

cursor.execute("SELECT COUNT(*) FROM results")
results_count = cursor.fetchone()[0]
print(f"成绩记录: {results_count}")

cursor.execute("SELECT gender, COUNT(*) FROM runners GROUP BY gender")
print("\n性别分布:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

cursor.execute("SELECT source, COUNT(*) FROM results GROUP BY source")
print("\n数据来源:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

cursor.execute("SELECT COUNT(*) FROM results WHERE finish_seconds < 8400")
print(f"\n2:20以内成绩: {cursor.fetchone()[0]}")

conn.close()
print("\n完成!")