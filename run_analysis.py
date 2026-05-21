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