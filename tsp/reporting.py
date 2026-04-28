"""
报告打印模块

包含实验结果的文本输出函数，用于在终端显示实验数据
"""

from tsp_types import AlgorithmResult, ExperimentBundle
from utils import format_time_ms


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """
    打印简洁的等宽表格
    
    Args:
        headers: 表头列表
        rows: 数据行列表，每行是一个字符串列表
    """
    widths = [len(header) for header in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def format_row(row_values: list[str]) -> str:
        return " | ".join(
            value.ljust(widths[idx]) for idx, value in enumerate(row_values)
        )

    print(format_row(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(format_row(row))


def print_metric_guide() -> None:
    """
    打印实验指标说明，帮助用户理解 baseline 和 gap 的含义
    """
    print("Metric guide:")
    print("  baseline = reference solution used for comparison in the current instance.")
    print("  gap (%)  = (cost - baseline) / baseline * 100%.")
    print("  small/medium instances use exact-optimal baselines;")
    print("  the large instance uses the best heuristic result in the compared set.")


def print_sa_summary(result: AlgorithmResult) -> None:
    """
    把模拟退火的关键收敛节点压缩为一行摘要
    
    Args:
        result: 算法结果对象
    """
    if not result.history:
        return

    selected = result.history[:2] + result.history[2::2]
    if selected[-1] != result.history[-1]:
        selected.append(result.history[-1])

    checkpoints = [
        f"{step}:{cost:.2f}@T={temp:.3f}" for step, cost, temp in selected
    ]
    print(f"  SA summary: {' | '.join(checkpoints)}")


def print_instance_report(bundle: ExperimentBundle) -> None:
    """
    输出一组实例的实验结果表格
    
    Args:
        bundle: 实验数据集合
    """
    print(f"\n=== {bundle.spec.name} ===")
    print(
        f"Baseline: {bundle.spec.baseline_label}, total cost = {bundle.baseline_cost:.2f}"
    )

    headers = ["Method", "Cost", "Gap", "Time (ms)", "Route Preview"]
    rows = [
        [
            result.name,
            f"{result.cost:.2f}",
            f"{result.gap_pct(bundle.baseline_cost):.2f}%",
            format_time_ms(result.time_ms),
            result.route_preview(),
        ]
        for result in bundle.results
    ]
    print_table(headers, rows)

    for result in bundle.results:
        print_sa_summary(result)


def print_city_summary(title: str, cities: list[tuple[int, int]], columns: int = 4) -> None:
    """
    按网格形式打印城市坐标，方便和图片对照
    
    Args:
        title: 标题
        cities: 城市坐标列表
        columns: 每行显示的城市数量（默认4个）
    """
    print(f"\n{title}")
    cells = [f"{idx:>2}:({x:>3},{y:>3})" for idx, (x, y) in enumerate(cities)]
    for start in range(0, len(cells), columns):
        print("  " + "   ".join(cells[start : start + columns]))
