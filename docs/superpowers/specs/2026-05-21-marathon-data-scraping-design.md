# 马拉松数据爬取设计方案

## 1. 背景与目标

**目标**：从 World Athletics 官网爬取全球马拉松运动员数据，为异常检测系统建立基准数据库。

**数据用途**：
- 横向基准分析：建立不同性别+年龄组+人种的成绩提升幅度分布
- 支持异常检测的双轨验证

---

## 2. 数据源

### 2.1 World Athletics (worldathletics.org)

- 精英运动员官方数据库
- URL 结构：`https://worldathletics.org/athletes/[country]/[athlete-name]-[id]`
- 数据包含：出生日期、性别、国籍、所有赛事成绩（包含马拉松）

### 2.2 目标字段

| 源字段 | 目标字段 | 说明 |
|-------|---------|------|
| name | Runner.name | 运动员姓名 |
| gender | Runner.gender | M/F |
| DOB | Runner.birth_year | 从出生日期提取年份 |
| nationality | Runner.ethnicity | 通过国籍推断（见 2.3）|
| competition results | RaceResult | 赛事名称 + 日期 + 成绩（秒）|

### 2.3 Ethnicity 推断规则

基于国籍/地区的启发式推断：

| 国籍 | 推断 Ethnicity |
|-----|--------------|
| 肯尼亚、埃塞俄比亚、厄立特里亚、乌干达、坦桑尼亚 | Black-African |
| 摩洛哥、埃及、阿尔及利亚、突尼斯、利比亚 | Black-Maghrebi |
| 牙买加、巴哈马、特立尼达和多巴哥、美国（非裔）、加勒比岛国 | Black-Caribbean |
| 日本、韩国、中国、朝鲜、蒙古、越南、泰国、菲律宾、印度尼西亚 | Asian |
| 印度、巴基斯坦、孟加拉国、斯里兰卡、尼泊尔 | Asian-South |
| 卡塔尔、巴林、阿联酋、沙特阿拉伯、科威特、阿曼 | Asian-MiddleEast |
| 英国、法国、德国、意大利、西班牙、荷兰、比利时、瑞士、瑞典、波兰、俄罗斯（欧洲）、葡萄牙、希腊 | White |
| 澳大利亚、新西兰、加拿大、墨西哥、巴西、阿根廷、秘鲁、智利 | Other |
| 其他 | Unknown |

---

## 3. 爬取范围

### 3.1 国家列表（35 个）

覆盖全球各地区，确保基准数据库多样性：

| 地区 | 国家 |
|-----|------|
| 东非（精英最多） | 肯尼亚、埃塞俄比亚、厄立特里亚、乌干达、坦桑尼亚 |
| 北非 | 摩洛哥、埃及、阿尔及利亚、突尼斯 |
| 西非/加勒比 | 牙买加、巴、美国（多民族）、特立尼达和多巴哥 |
| 东亚 | 日本、中国、韩国、朝鲜、蒙古 |
| 东南亚 | 泰国、越南、印度尼西亚、菲律宾 |
| 南亚 | 印度、巴基斯坦、孟加拉国、斯里兰卡 |
| 中东 | 卡塔尔、巴林、阿联酋、沙特阿拉伯 |
| 欧洲 | 英国、法国、德国、意大利、西班牙、荷兰、比利时、瑞士、瑞典、波兰、俄罗斯 |
| 其他 | 澳大利亚、新西兰、加拿大、墨西哥、巴西 |

### 3.2 筛选条件

- 仅爬取有**至少一场马拉松完赛成绩**的运动员
- 马拉松成绩需在 2:00:00 ~ 6:00:00 范围内（排除异常值）
- 年龄范围：18 ~ 70 岁

---

## 4. 爬虫架构

```
src/data_collection/
├── scraper.py              # 基类 Scraper
└── world_athletics_scraper.py  # WA 专用实现
        ├── search_athletes(country)     # 按国家搜索运动员列表
        ├── get_athlete_profile(url)     # 获取单个运动员详情
        ├── parse_results(html)          # 解析成绩数据
        └── ethnicity_infer(nationality) # ethnicity 推断
```

### 4.1 关键类

**`WorldAthleticsScraper`**
- `search_athletes(country: str) -> List[str]`：返回该国所有运动员 profile URL
- `get_athlete_profile(url: str) -> Optional[Runner]`：抓取并解析单个运动员档案
- `scrape_results(runner_id: str, url: str) -> List[RaceResult]`：抓取该运动员所有成绩
- `scrape_country(country: str) -> Tuple[List[Runner], List[RaceResult]]`：抓取整个国家的数据

**`Scraper`（基类）**
- `fetch(url: str) -> str`：HTTP GET 请求，带重试和延时
- `parse_html(html: str) -> BeautifulSoup`：HTML 解析
- `rate_limit()`：请求间隔控制（避免被封）

---

## 5. 数据存储

### 5.1 存储方式

- 原始 HTML 缓存（`data/raw/html/`）
- 结构化数据：CSV (`data/processed/`) + SQLite (`data/marathon.db`)

### 5.2 输出文件

```
data/
├── raw/
│   └── html/
│       └── [country]/[athlete_id].html   # 原始页面缓存
└── processed/
    ├── runners.csv        # 运动员信息
    └── results.csv       # 比赛成绩
```

### 5.3 CSV 格式

**runners.csv**
```csv
id,name,gender,birth_year,ethnicity,country
1,Eliud Kipchoge,M,1984,Black-African,Kenya
2,Brigid Kosgei,F,1993,Black-African,Kenya
```

**results.csv**
```csv
runner_id,race_name,race_date,finish_time_seconds,is_certified
1,Berlin Marathon,2022-09-25,9012,1
1,Tokyo Marathon,2023-03-05,9023,1
```

---

## 6. 爬取流程

```
1. 初始化 SQLite 数据库
2. 遍历 35 个国家列表
   3. 调用 search_athletes(country) 获取运动员 URL 列表
   4. 遍历每个运动员 URL：
      5. 检查是否已缓存（避免重复抓取）
      6. 调用 get_athlete_profile(url) 获取基本信息
      7. 调用 scrape_results() 获取所有成绩
      8. 推断 ethnicity
      9. 写入 SQLite
   10. 延时（每国家间 5 秒，每运动员间 1 秒）
11. 导出 CSV
```

---

## 7. 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 网络请求失败 | 重试 3 次，间隔 2s/5s/10s |
| 页面不存在/404 | 跳过，记录日志 |
| HTML 解析失败 | 跳过，记录日志 |
| 反爬封禁（403/429） | 停止爬取，等待 5 分钟 |
| 数据不完整 | 跳过或标记为 Unknown |

---

## 8. 进度追踪

- SQLite 中记录已爬取国家、运动员数、成绩数
- 支持断点续爬（重启后可跳过已爬取的数据）
- 实时输出进度到控制台

---

## 9. 实施步骤

1. 实现 `Scraper` 基类（HTTP 请求、延时、反封）
2. 实现 `WorldAthleticsScraper` 爬虫
3. 测试单个国家爬取（日本）
4. 批量爬取所有 35 个国家
5. 数据清洗 + 导入 SQLite
6. 导出 CSV 供分析使用

---

## 10. 依赖

已在 `requirements.txt` 中：
- `requests>=2.28.0`
- `beautifulsoup4>=4.12.0`
- `lxml>=4.9.0`
