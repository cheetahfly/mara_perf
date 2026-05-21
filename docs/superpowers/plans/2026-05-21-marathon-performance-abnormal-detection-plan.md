# 马拉松成绩异常检测 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal：** 构建一套可判断中国马拉松跑者成绩提升是否异常的 双轨分析系统

**Architecture：**
- 数据层：结构化存储马拉松成绩数据（SQLite + CSV）
- 分析层：两条分析轨道——横向基准比较 + 纵向轨迹建模
- 判定层：综合两条轨道结果，输出异常判定

**Tech Stack：** Python 3.10+ / pandas / scipy / sqlite3 / matplotlib

---

## 文件结构

```
F:\ai_data_ana\mara_perf\
├── data/
│   ├── raw/                      # 原始数据
│   └── processed/                # 清洗后数据
├── src/
│   ├── __init__.py
│   ├── data_collection/          # 数据采集模块
│   │   ├── __init__.py
│   │   ├── scraper.py             # 网页爬虫基类
│   │   └── data_models.py         # 数据模型定义
│   ├── analysis/                  # 分析模块
│   │   ├── __init__.py
│   │   ├── baseline.py            # 横向基准比较
│   │   ├── trajectory.py          # 纵向轨迹建模
│   │   └── detector.py            # 异常判定
│   └── utils/
│       ├── __init__.py
│       └── time_converter.py      # 成绩时间格式转换
├── notebooks/
│   └── exploratory_analysis.ipynb # 探索性分析
├── tests/
│   ├── __init__.py
│   ├── test_time_converter.py
│   ├── test_baseline.py
│   ├── test_trajectory.py
│   └── test_detector.py
└── docs/superpowers/specs/        # 设计文档（已有）
```

---

## Task 1: 项目初始化

**Files:**
- Create: `src/__init__.py`
- Create: `src/data_collection/__init__.py`
- Create: `src/analysis/__init__.py`
- Create: `src/utils/__init__.py`
- Create: `tests/__init__.py`
- Create: `data/raw/.gitkeep`
- Create: `data/processed/.gitkeep`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p data/raw data/processed
mkdir -p src/data_collection src/analysis src/utils
mkdir -p notebooks tests
touch data/raw/.gitkeep data/processed/.gitkeep
touch src/__init__.py src/data_collection/__init__.py src/analysis/__init__.py src/utils/__init__.py
touch tests/__init__.py
```

- [ ] **Step 2: 创建 requirements.txt**

```
pandas>=2.0.0
scipy>=1.10.0
matplotlib>=3.7.0
requests>=2.28.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pytest>=7.3.0
```

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "chore: initial project structure"
```

---

## Task 2: 成绩时间格式转换工具

**Files:**
- Create: `src/utils/time_converter.py`
- Create: `tests/test_time_converter.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_time_converter.py
import pytest
from src.utils.time_converter import (
    parse_time,          # "2:20:00" → 8400 (秒)
    format_time,          # 8400 → "2:20:00"
    time_to_minutes,      # 转为分钟 float
    minutes_to_time,      # 分钟 float → "HH:MM:SS"
)

class TestParseTime:
    def test_standard_format(self):
        assert parse_time("2:20:00") == 8400

    def test_single_digit_hours(self):
        assert parse_time("1:05:30") == 3930

    def test_no_hours(self):
        assert parse_time("25:00") == 1500  # 半马常用格式

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_time("invalid")

class TestFormatTime:
    def test_standard(self):
        assert format_time(8400) == "2:20:00"

    def test_with_leading_zero(self):
        assert format_time(3930) == "1:05:30"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_time_converter.py -v
# 预期: FAIL - import error 或 test failures
```

- [ ] **Step 3: 实现 time_converter.py**

```python
# src/utils/time_converter.py
"""马拉松成绩时间格式转换工具"""

def parse_time(time_str: str) -> int:
    """将时间字符串转为秒数"""
    parts = time_str.strip().split(":")
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)
    else:
        raise ValueError(f"Invalid time format: {time_str}")

def format_time(seconds: int) -> str:
    """将秒数转为 HH:MM:SS 格式"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h}:{m:02d}:{s:02d}"

def time_to_minutes(seconds: int) -> float:
    """秒数转为分钟（浮点）"""
    return seconds / 60.0

def minutes_to_time(minutes: float) -> str:
    """分钟浮点数转为时间字符串"""
    total_seconds = int(round(minutes * 60))
    return format_time(total_seconds)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_time_converter.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交**

```bash
git add tests/test_time_converter.py src/utils/time_converter.py
git commit -m "feat: add time format converter utility"
```

---

## Task 3: 数据模型定义

**Files:**
- Create: `src/data_collection/data_models.py`
- Create: `tests/test_data_models.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_data_models.py
import pytest
from datetime import date
from src.data_collection.data_models import Runner, RaceResult

class TestRunner:
    def test_create_runner(self):
        runner = Runner(
            name="张三",
            gender="M",
            birth_year=1990,
            ethnicity="Asian"
        )
        assert runner.name == "张三"
        assert runner.gender == "M"
        assert runner.age_group(2024) == 34  # 2024 - 1990

    def test_age_group_calculation(self):
        runner = Runner(name="李四", gender="F", birth_year=1985, ethnicity="Asian")
        assert runner.age_group(2025) == 40  # 2025 - 1985

class TestRaceResult:
    def test_create_race_result(self):
        result = RaceResult(
            runner_id="runner_001",
            race_name="北京马拉松",
            race_date=date(2024, 10, 20),
            finish_time_seconds=8400,
            is_certified=True
        )
        assert result.finish_time_seconds == 8400
        assert result.finish_time_formatted == "2:20:00"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_data_models.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现 data_models.py**

```python
# src/data_collection/data_models.py
"""马拉松数据模型"""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from src.utils.time_converter import format_time

@dataclass
class Runner:
    name: str
    gender: str  # "M" or "F"
    birth_year: int
    ethnicity: str  # "Black", "White", "Asian", etc.

    def age_group(self, reference_year: int) -> int:
        return reference_year - self.birth_year

@dataclass
class RaceResult:
    runner_id: str
    race_name: str
    race_date: date
    finish_time_seconds: int
    is_certified: bool = True
    notes: Optional[str] = None

    @property
    def finish_time_formatted(self) -> str:
        return format_time(self.finish_time_seconds)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_data_models.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交**

```bash
git add tests/test_data_models.py src/data_collection/data_models.py
git commit -m "feat: add data models for Runner and RaceResult"
```

---

## Task 4: 数据存储层（SQLite）

**Files:**
- Create: `src/data_collection/database.py`
- Create: `tests/test_database.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_database.py
import pytest
import tempfile
import os
from src.data_collection.database import Database

class TestDatabase:
    def test_init_and_insert_runner(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = Database(db_path)
            runner_id = db.insert_runner("张三", "M", 1990, "Asian")
            assert runner_id == 1

            runner = db.get_runner(runner_id)
            assert runner.name == "张三"
            assert runner.gender == "M"

    def test_insert_and_query_results(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = Database(db_path)

            runner_id = db.insert_runner("李四", "F", 1985, "Asian")
            from datetime import date
            db.insert_result(runner_id, "上海马拉松", date(2024, 10, 20), 8400, True)

            results = db.get_results_by_runner(runner_id)
            assert len(results) == 1
            assert results[0].finish_time_seconds == 8400
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_database.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现 database.py**

```python
# src/data_collection/database.py
"""SQLite 数据存储层"""
import sqlite3
from dataclass import dataclass
from datetime import date
from typing import List, Optional

@dataclass
class Runner:
    id: int
    name: str
    gender: str
    birth_year: int
    ethnicity: str

@dataclass
class RaceResult:
    id: int
    runner_id: int
    race_name: str
    race_date: date
    finish_time_seconds: int
    is_certified: bool

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    birth_year INTEGER NOT NULL,
                    ethnicity TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    runner_id INTEGER NOT NULL,
                    race_name TEXT NOT NULL,
                    race_date TEXT NOT NULL,
                    finish_time_seconds INTEGER NOT NULL,
                    is_certified INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (runner_id) REFERENCES runners(id)
                )
            """)

    def insert_runner(self, name: str, gender: str, birth_year: int, ethnicity: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO runners (name, gender, birth_year, ethnicity) VALUES (?, ?, ?, ?)",
                (name, gender, birth_year, ethnicity)
            )
            return cursor.lastrowid

    def get_runner(self, runner_id: int) -> Optional[Runner]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM runners WHERE id = ?", (runner_id,))
            row = cursor.fetchone()
            if row:
                return Runner(id=row["id"], name=row["name"], gender=row["gender"],
                              birth_year=row["birth_year"], ethnicity=row["ethnicity"])
            return None

    def insert_result(self, runner_id: int, race_name: str, race_date: date,
                     finish_time_seconds: int, is_certified: bool = True) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO results (runner_id, race_name, race_date, finish_time_seconds, is_certified) VALUES (?, ?, ?, ?, ?)",
                (runner_id, race_name, race_date.isoformat(), finish_time_seconds, int(is_certified))
            )
            return cursor.lastrowid

    def get_results_by_runner(self, runner_id: int) -> List[RaceResult]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM results WHERE runner_id = ? ORDER BY race_date",
                (runner_id,)
            )
            rows = cursor.fetchall()
            return [RaceResult(
                id=row["id"], runner_id=row["runner_id"], race_name=row["race_name"],
                race_date=date.fromisoformat(row["race_date"]),
                finish_time_seconds=row["finish_time_seconds"],
                is_certified=bool(row["is_certified"])
            ) for row in rows]
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_database.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交**

```bash
git add tests/test_database.py src/data_collection/database.py
git commit -m "feat: add SQLite database layer"
```

---

## Task 5: 横向基准分析（Baseline）

**Files:**
- Create: `src/analysis/baseline.py`
- Create: `tests/test_baseline.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_baseline.py
import pytest
import numpy as np
from src.analysis.baseline import BaselineAnalyzer

class TestBaselineAnalyzer:
    def test_compute_improvement_distribution(self):
        """测试提升幅度分布计算"""
        # 模拟：100个跑者，每个有3个历史成绩
        # [[time1, time2, time3], ...]
        times = [[8400, 8250, 8100] for _ in range(100)]  # 每人逐步提升
        analyzer = BaselineAnalyzer(times)
        distribution = analyzer.compute_improvement_distribution(window=1)

        assert len(distribution) == 100
        # 第一个间隔：8250-8400 = -150
        assert distribution[0] == -150

    def test_percentile_position(self):
        """测试百分位计算"""
        times = [[8400, 8100, 7950] for _ in range(100)]
        analyzer = BaselineAnalyzer(times)

        # 目标提升：-600秒（巨大提升）
        target_improvement = -600
        percentile = analyzer.get_percentile(target_improvement, window=1)

        # 在这个模拟分布中，-600 应该是极端值（极高百分位）
        assert percentile < 10  # 小于10%分位

    def test_empty_timeseries(self):
        """测试单条时间序列无法计算"""
        times = [[8400]]  # 只有一个成绩
        analyzer = BaselineAnalyzer(times)
        distribution = analyzer.compute_improvement_distribution(window=1)
        assert len(distribution) == 0  # 无法计算间隔
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_baseline.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现 baseline.py**

```python
# src/analysis/baseline.py
"""横向基准分析：比较同条件人群的提升幅度分布"""
import numpy as np
from typing import List

class BaselineAnalyzer:
    """
    按性别+年龄组+人种分组，计算该人群的提升幅度分布
    """

    def __init__(self, runner_times: List[List[int]]):
        """
        runner_times: [[t1, t2, t3], [t1, t2], ...] 每位跑者的历史成绩(秒)，按时间排序
        """
        self.runner_times = runner_times

    def compute_improvement_distribution(self, window: int = 1) -> np.ndarray:
        """
        计算相邻 window 个成绩之间的变化量（秒）
        负值表示成绩提升（时间减少）
        返回所有变化量的数组
        """
        improvements = []
        for times in self.runner_times:
            for i in range(window, len(times)):
                improvement = times[i] - times[i - window]  # 负=提升
                improvements.append(improvement)
        return np.array(improvements)

    def get_percentile(self, target_improvement: int, window: int = 1) -> float:
        """
        计算目标提升幅度在分布中的百分位
        百分位越低说明越罕见（提升越大）
        """
        distribution = self.compute_improvement_distribution(window)
        if len(distribution) == 0:
            raise ValueError("No enough data points to compute distribution")
        return float(np.sum(distribution <= target_improvement)) / len(distribution) * 100
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_baseline.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交**

```bash
git add tests/test_baseline.py src/analysis/baseline.py
git commit -m "feat: add horizontal baseline analyzer"
```

---

## Task 6: 纵向轨迹建模（Trajectory）

**Files:**
- Create: `src/analysis/trajectory.py`
- Create: `tests/test_trajectory.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_trajectory.py
import pytest
import numpy as np
from src.analysis.trajectory import TrajectoryAnalyzer

class TestTrajectoryAnalyzer:
    def test_predict_next_time(self):
        """测试成绩预测"""
        # 模拟一个平稳下降的时间序列
        times = [8400, 8300, 8200, 8100]  # 每步下降100秒
        analyzer = TrajectoryAnalyzer(times)

        predicted, ci = analyzer.predict_next(ci=0.95)
        assert predicted < 8100  # 预测应该继续下降
        assert ci[0] < ci[1]  # 置信区间下限 < 上限

    def test_is_significant_deviation(self):
        """测试偏离检测"""
        # 平稳序列
        times = [8400, 8300, 8200, 8100]
        analyzer = TrajectoryAnalyzer(times)

        # 正常提升（继续下降100秒左右）
        assert analyzer.is_significant_deviation(8000) is False

        # 异常巨大提升（一下子降600秒）
        assert analyzer.is_significant_deviation(7500) is True

    def test_insufficient_data(self):
        """数据点太少无法建模"""
        times = [8400]
        analyzer = TrajectoryAnalyzer(times)
        with pytest.raises(ValueError):
            analyzer.predict_next()
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_trajectory.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现 trajectory.py**

```python
# src/analysis/trajectory.py
"""纵向轨迹建模：分析单跑者自身历史成绩趋势"""
import numpy as np
from typing import Tuple, List

class TrajectoryAnalyzer:
    """
    对单跑者的历史成绩进行时间序列分析
    """

    def __init__(self, times: List[int]):
        """
        times: 按时间排序的成绩列表（秒）
        """
        if len(times) < 3:
            raise ValueError("Need at least 3 time points to model trajectory")
        self.times = np.array(times)
        self.n = len(times)

    def predict_next(self, ci: float = 0.95) -> Tuple[float, Tuple[float, float]]:
        """
        预测下一个成绩，返回 (预测值, 置信区间)
        使用线性回归 + 残差标准差计算置信区间
        """
        x = np.arange(self.n)
        y = self.times

        # 简单线性回归
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs

        predicted = slope * self.n  # 预测下一个点
        residuals = y - np.polyval(coeffs, x)
        std_residuals = np.std(residuals)

        # 置信区间
        z = 1.96 if ci == 0.95 else 2.576  # z-score for 95% / 99%
        margin = z * std_residuals

        return float(predicted), (float(predicted - margin), float(predicted + margin))

    def is_significant_deviation(self, actual_time: int, ci: float = 0.95) -> bool:
        """
        判断实际成绩是否显著偏离预测置信区间
        """
        predicted, (lower, upper) = self.predict_next(ci=ci)
        return not (lower <= actual_time <= upper)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_trajectory.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交**

```bash
git add tests/test_trajectory.py src/analysis/trajectory.py
git commit -m "feat: add longitudinal trajectory analyzer"
```

---

## Task 7: 异常判定器（Detector）

**Files:**
- Create: `src/analysis/detector.py`
- Create: `tests/test_detector.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_detector.py
import pytest
from src.analysis.detector import AnomalyDetector, DetectionResult

class TestAnomalyDetector:
    def test_abnormal_case(self):
        """横向罕见 + 纵向异常 = 异常"""
        # 模拟基准数据：正常提升幅度
        baseline_times = [[8400, 8300] for _ in range(100)]
        # 目标跑者：巨大异常提升
        target_times = [8400, 7800]  # 一下子提升600秒

        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        assert result.percentile < 5
        assert result.is_longitudinal_anomaly is True
        assert result.is_abnormal is True

    def test_normal_breakthrough(self):
        """横向罕见但纵向符合规律 = 正常突破"""
        # 基准数据：正常小幅提升
        baseline_times = [[8400, 8350] for _ in range(100)]  # 提升慢
        # 目标跑者：训练突破，稳步下降
        target_times = [8400, 8100, 7800]  # 持续下降，符合训练规律

        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        assert result.percentile < 5
        assert result.is_longitudinal_anomaly is False
        assert result.is_abnormal is False

    def test_normal_case(self):
        """横向不罕见 = 正常"""
        baseline_times = [[8400, 8100] for _ in range(100)]  # 正常提升200秒
        target_times = [8400, 8100]

        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        assert result.percentile > 5
        assert result.is_abnormal is False
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_detector.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现 detector.py**

```python
# src/analysis/detector.py
"""异常判定器：综合横向基准和纵向轨迹"""
from dataclasses import dataclass
from typing import List
from src.analysis.baseline import BaselineAnalyzer
from src.analysis.trajectory import TrajectoryAnalyzer

@dataclass
class DetectionResult:
    is_abnormal: bool
    percentile: float
    is_longitudinal_anomaly: bool
    verdict: str
    details: str

class AnomalyDetector:
    """
    双轨异常检测
    """

    def __init__(self, baseline_runner_times: List[List[int]], target_times: List[int]):
        """
        baseline_runner_times: 同条件人群的历史成绩
        target_times: 目标跑者的历史成绩
        """
        self.baseline = BaselineAnalyzer(baseline_runner_times)
        self.target_times = target_times

    def detect(self, threshold: float = 5.0) -> DetectionResult:
        """
        执行异常检测
        threshold: 百分位阈值，默认5%
        """
        if len(self.target_times) < 3:
            # 数据不足，只用横向
            improvement = self.target_times[-1] - self.target_times[0]
            percentile = self.baseline.get_percentile(improvement)
            is_longitudinal_anomaly = False
        else:
            # 双轨分析
            trajectory = TrajectoryAnalyzer(self.target_times)

            # 横向：计算最后一个提升幅度
            last_improvement = self.target_times[-1] - self.target_times[-2]
            percentile = self.baseline.get_percentile(last_improvement)

            # 纵向：检查是否超出置信区间
            is_longitudinal_anomaly = trajectory.is_significant_deviation(
                self.target_times[-1]
            )

        # 判定
        is_abnormal = (percentile < threshold) and is_longitudinal_anomaly

        if is_abnormal:
            verdict = "异常"
            details = f"横向百分位={percentile:.1f}%（<{threshold}%）且纵向轨迹异常"
        elif percentile < threshold:
            verdict = "正常（训练突破）"
            details = f"横向罕见（{percentile:.1f}%），但纵向符合运动规律"
        else:
            verdict = "正常"
            details = f"横向百分位={percentile:.1f}%，无异常迹象"

        return DetectionResult(
            is_abnormal=is_abnormal,
            percentile=percentile,
            is_longitudinal_anomaly=is_longitudinal_anomaly,
            verdict=verdict,
            details=details
        )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_detector.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交**

```bash
git add tests/test_detector.py src/analysis/detector.py
git commit -m "feat: add anomaly detector combining both tracks"
```

---

## Task 8: 数据采集脚本（手动录入 + 批量导入）

**Files:**
- Create: `src/data_collection/loader.py`
- Create: `tests/test_loader.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_loader.py
import pytest
import tempfile
import os
import csv
from datetime import date
from src.data_collection.loader import CSVLoader

class TestCSVLoader:
    def test_load_runner_csv(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "gender", "birth_year", "ethnicity"])
            writer.writerow(["张三", "M", 1990, "Asian"])
            writer.writerow(["李四", "F", 1985, "White"])
            f_path = f.name

        try:
            runners = list(CSVLoader.load_runners(f_path))
            assert len(runners) == 2
            assert runners[0].name == "张三"
        finally:
            os.unlink(f_path)

    def test_load_results_csv(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["runner_id", "race_name", "race_date", "finish_time_seconds", "is_certified"])
            writer.writerow([1, "北京马拉松", "2024-10-20", 8400, 1])
            f_path = f.name

        try:
            results = list(CSVLoader.load_results(f_path))
            assert len(results) == 1
            assert results[0].finish_time_seconds == 8400
        finally:
            os.unlink(f_path)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_loader.py -v
# 预期: FAIL
```

- [ ] **Step 3: 实现 loader.py**

```python
# src/data_collection/loader.py
"""CSV 数据导入工具"""
import csv
from datetime import date
from typing import Iterator, List
from src.data_collection.data_models import Runner, RaceResult

class CSVLoader:
    @staticmethod
    def load_runners(csv_path: str) -> Iterator[Runner]:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield Runner(
                    name=row["name"],
                    gender=row["gender"],
                    birth_year=int(row["birth_year"]),
                    ethnicity=row["ethnicity"]
                )

    @staticmethod
    def load_results(csv_path: str) -> Iterator[RaceResult]:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield RaceResult(
                    runner_id=row["runner_id"],
                    race_name=row["race_name"],
                    race_date=date.fromisoformat(row["race_date"]),
                    finish_time_seconds=int(row["finish_time_seconds"]),
                    is_certified=bool(int(row.get("is_certified", 1)))
                )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_loader.py -v
# 预期: PASS
```

- [ ] **Step 5: 提交**

```bash
git add tests/test_loader.py src/data_collection/loader.py
git commit -m "feat: add CSV data loader"
```

---

## Task 9: 端到端集成测试

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: 写集成测试**

```python
# tests/test_integration.py
"""端到端测试：模拟真实分析流程"""
import pytest
from src.analysis.detector import AnomalyDetector
from src.data_collection.database import Database
from src.data_collection.loader import CSVLoader
import tempfile
import os
import csv
from datetime import date

class TestIntegration:
    def test_full_pipeline(self):
        """完整流程：从数据到判定"""
        # 1. 准备基准数据（模拟100个同龄男性黄种人跑者）
        baseline_times = []
        for _ in range(100):
            # 每人3个成绩，均匀分布在8400-7800秒之间
            baseline_times.append([8400, 8200, 8000])

        # 2. 目标跑者：异常情况——从8400突然跳到7500
        target_times = [8400, 7500, 7400]

        # 3. 执行检测
        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        # 4. 验证
        assert result.is_abnormal is True
        assert result.verdict == "异常"

    def test_normal_breakthrough_integration(self):
        """正常突破案例"""
        baseline_times = [[8400, 8350, 8250] for _ in range(100)]
        target_times = [8400, 8200, 8000]  # 符合训练规律的稳步提升

        detector = AnomalyDetector(baseline_times, target_times)
        result = detector.detect()

        # 稳步提升在基准分布中可能偏快（百分位低），但纵向符合规律
        assert result.is_longitudinal_anomaly is False
        assert result.verdict == "正常（训练突破）"
```

- [ ] **Step 2: 运行集成测试**

```bash
pytest tests/test_integration.py -v
# 预期: PASS
```

- [ ] **Step 3: 提交**

```bash
git add tests/test_integration.py
git commit -m "test: add end-to-end integration tests"
```

---

## Task 10: 主程序入口

**Files:**
- Create: `run_analysis.py`

- [ ] **Step 1: 编写主程序**

```python
# run_analysis.py
"""
马拉松成绩异常检测 - 主程序入口

用法:
    python run_analysis.py --target <目标跑者ID> --db <数据库路径>

示例:
    python run_analysis.py --target 1 --db data/marathon.db
"""
import argparse
import sys
from src.data_collection.database import Database
from src.analysis.detector import AnomalyDetector

def main():
    parser = argparse.ArgumentParser(description="马拉松成绩异常检测")
    parser.add_argument("--target", type=int, required=True, help="目标跑者ID")
    parser.add_argument("--db", type=str, default="data/marathon.db", help="数据库路径")
    parser.add_argument("--baseline-db", type=str, default=None, help="基准数据数据库路径（默认同--db）")
    parser.add_argument("--threshold", type=float, default=5.0, help="异常判定百分位阈值")
    args = parser.parse_args()

    baseline_db_path = args.baseline_db or args.db

    # 加载数据
    db = Database(args.db)
    baseline_db = Database(baseline_db_path)

    # TODO: 实现从数据库获取基准数据（留作后续数据积累后实现）
    print("基准数据库功能待实现，请先通过 CSV 导入数据后使用。")
    print("当前仅支持单跑者纵向分析。")

    # 简单纵向分析
    results = db.get_results_by_runner(args.target)
    if len(results) < 3:
        print(f"跑者 {args.target} 成绩记录不足（需要至少3条）")
        sys.exit(1)

    times = [r.finish_time_seconds for r in results]
    print(f"跑者成绩时间序列: {[r.finish_time_formatted for r in results]}")

    from src.analysis.trajectory import TrajectoryAnalyzer
    analyzer = TrajectoryAnalyzer(times)
    predicted, (lower, upper) = analyzer.predict_next()

    print(f"预测下一个成绩: {analyzer.times[-1]}s 置信区间: [{lower:.0f}, {upper:.0f}]")

    is_anomaly = analyzer.is_significant_deviation(times[-1])
    print(f"异常检测结果: {'异常' if is_anomaly else '正常'}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试主程序帮助信息**

```bash
python run_analysis.py --help
# 预期: 显示帮助信息
```

- [ ] **Step 3: 提交**

```bash
git add run_analysis.py
git commit -m "feat: add main entry point for analysis"
```

---

## 实施顺序

1. Task 1: 项目初始化
2. Task 2: 成绩时间转换工具
3. Task 3: 数据模型定义
4. Task 4: SQLite 数据存储层
5. Task 5: 横向基准分析
6. Task 6: 纵向轨迹建模
7. Task 7: 异常判定器
8. Task 8: 数据导入工具
9. Task 9: 端到端集成测试
10. Task 10: 主程序入口

---

## 已知约束与后续任务

- **数据采集**：当前设计支持 CSV 导入，Web 抓取脚本作为后续扩展
- **基准数据积累**：当前测试使用模拟数据，真实基准数据库需要持续积累
- **数据可视化**：探索性分析 notebook 可辅助理解分布特征
