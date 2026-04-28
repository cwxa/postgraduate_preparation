"""
可视化模块

包含TSP实验结果的可视化函数，用于生成各种图表：
- 路径图：展示各算法的旅行路线
- 条形图：比较各算法的代价和运行时间
- 收敛曲线：展示模拟退火的收敛过程
"""

import matplotlib
from pathlib import Path

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from constants import ROUTE_COLORS
from tsp_types import AlgorithmResult, ExperimentBundle
from utils import format_time_ms


def get_output_dir() -> Path:
    """
    获取输出目录路径，如果不存在则创建
    
    Returns:
        输出目录路径
    """
    output_dir = Path(__file__).resolve().parent / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def plot_tour(
    ax,
    cities: list[tuple[int, int]],
    result: AlgorithmResult,
    baseline_cost: float,
    line_color: str,
) -> None:
    """
    在指定坐标轴上绘制一条旅行路径
    
    Args:
        ax: 坐标轴对象
        cities: 城市坐标列表
        result: 算法结果对象
        baseline_cost: 基准解代价
        line_color: 路径颜色
    """
    xs = [cities[city][0] for city in result.tour]
    ys = [cities[city][1] for city in result.tour]
    city_x = [city[0] for city in cities]
    city_y = [city[1] for city in cities]

    ax.plot(xs, ys, color=line_color, linewidth=2, zorder=1)
    ax.scatter(city_x, city_y, color="white", edgecolor="#333", s=50, zorder=2)
    ax.scatter(
        cities[0][0], cities[0][1], color="#dc2626", edgecolor="#991b1b", s=80, zorder=3
    )

    gap = result.gap_pct(baseline_cost)
    ax.set_title(
        f"{result.name}\nCost: {result.cost:.1f} (gap: {gap:.1f}%)", fontsize=10
    )
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)


def plot_routes(bundle: ExperimentBundle) -> str:
    """
    绘制所有算法的路径图并保存
    
    Args:
        bundle: 实验数据集合
    
    Returns:
        生成的文件路径
    """
    n_results = len(bundle.results)
    cols = 3
    rows = (n_results + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3.5))
    axes = axes.flatten() if rows > 1 else [axes]

    for idx, (result, color) in enumerate(zip(bundle.results, ROUTE_COLORS)):
        plot_tour(axes[idx], bundle.cities, result, bundle.baseline_cost, color)

    for idx in range(n_results, len(axes)):
        axes[idx].axis("off")

    fig.suptitle(f"Comparison of TSP Routes: {bundle.spec.name}", fontsize=14, y=0.99)
    plt.tight_layout()

    output_path = get_output_dir() / bundle.spec.name.lower().replace(" ", "_") / "routes.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return str(output_path)


def plot_summary_bar(bundle: ExperimentBundle) -> str:
    """
    绘制算法性能对比条形图（代价和时间）
    
    Args:
        bundle: 实验数据集合
    
    Returns:
        生成的文件路径
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    labels = [r.name for r in bundle.results]
    colors = ROUTE_COLORS[: len(bundle.results)]

    costs = [r.cost for r in bundle.results]
    ax1.bar(labels, costs, color=colors)
    ax1.axhline(bundle.baseline_cost, color="#dc2626", linestyle="--", label="Baseline")
    ax1.set_ylabel("Total Cost")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    times = [r.time_ms for r in bundle.results]
    ax2.bar(labels, times, color=colors)
    ax2.set_ylabel("Time (ms)")
    ax2.set_xlabel("Algorithm")
    ax2.grid(axis="y", alpha=0.3)

    plt.setp(ax2.get_xticklabels(), rotation=30, ha="right")
    fig.suptitle(f"Algorithm Comparison: {bundle.spec.name}", fontsize=14)
    plt.tight_layout()

    output_path = get_output_dir() / bundle.spec.name.lower().replace(" ", "_") / "summary.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return str(output_path)


def plot_sa_convergence(bundles: list[ExperimentBundle]) -> str:
    """
    绘制模拟退火的收敛曲线对比图
    
    Args:
        bundles: 多个实验数据集合
    
    Returns:
        生成的文件路径
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    for bundle, color in zip(bundles, ROUTE_COLORS):
        sa_result = bundle.by_name.get("2-opt + SA")
        if sa_result and sa_result.history:
            steps = [h[0] for h in sa_result.history]
            costs = [h[1] for h in sa_result.history]
            temps = [h[2] for h in sa_result.history]

            ax1.plot(steps, costs, marker="o", markersize=4, color=color, label=bundle.spec.name)
            ax2.semilogy(steps, temps, marker="x", markersize=4, color=color, label=bundle.spec.name)

    ax1.set_ylabel("Best Cost")
    ax1.set_title("Simulated Annealing Convergence")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.set_xlabel("Iteration Steps")
    ax2.set_ylabel("Temperature")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()

    output_path = get_output_dir() / "cross_instance" / "sa_convergence.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return str(output_path)


def plot_all_instances_summary(bundles: list[ExperimentBundle]) -> str:
    """
    绘制跨实例的算法性能汇总图
    
    Args:
        bundles: 多个实验数据集合
    
    Returns:
        生成的文件路径
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.18
    instance_names = [b.spec.name for b in bundles]
    x = range(len(instance_names))

    all_names = set()
    for b in bundles:
        for r in b.results:
            all_names.add(r.name)

    for idx, alg_name in enumerate(sorted(all_names)):
        gaps = []
        for bundle in bundles:
            result = bundle.by_name.get(alg_name)
            if result:
                gaps.append(result.gap_pct(bundle.baseline_cost))
            else:
                gaps.append(None)

        ax.bar(
            [xi + idx * bar_width for xi in x],
            [g if g is not None else 0 for g in gaps],
            width=bar_width,
            label=alg_name,
            color=ROUTE_COLORS[idx % len(ROUTE_COLORS)],
        )

    ax.set_xlabel("Instance")
    ax.set_ylabel("Gap (%)")
    ax.set_title("Algorithm Performance Across Instances")
    ax.set_xticks([xi + bar_width * (len(all_names) - 1) / 2 for xi in x])
    ax.set_xticklabels(instance_names, rotation=30, ha="right")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_path = get_output_dir() / "cross_instance" / "all_instances_summary.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return str(output_path)


def plot_log_summary(bundles: list[ExperimentBundle], metric: str) -> str:
    """
    绘制跨实例的算法性能对数刻度汇总图
    
    Args:
        bundles: 多个实验数据集合
        metric: 指标类型 ("time" 或 "gap")
    
    Returns:
        生成的文件路径
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    instance_names = [b.spec.name for b in bundles]

    for result in bundles[0].results:
        values = []
        for bundle in bundles:
            r = bundle.by_name.get(result.name)
            if r:
                if metric == "time":
                    values.append(r.time_ms)
                else:
                    values.append(r.gap_pct(bundle.baseline_cost))
            else:
                values.append(0)

        ax.plot(instance_names, values, marker="o", label=result.name)

    ax.set_xlabel("Instance")
    if metric == "time":
        ax.set_ylabel("Runtime (ms)")
        ax.set_yscale("log")
        ax.set_title("Algorithm Runtime Comparison")
    else:
        ax.set_ylabel("Gap (%)")
        ax.set_title("Algorithm Gap Comparison")

    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(alpha=0.3)
    plt.tight_layout()

    output_path = (
        get_output_dir() / "cross_instance" / f"{metric}_log_summary.png"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return str(output_path)


def generate_visual_demo(
    *bundles: ExperimentBundle,
) -> list[str]:
    """
    为所有实例生成可视化图片
    
    Args:
        bundles: 一个或多个实验数据集合
    
    Returns:
        生成的文件路径列表
    """
    paths = []
    for bundle in bundles:
        paths.append(plot_routes(bundle))
        paths.append(plot_summary_bar(bundle))

    paths.append(plot_sa_convergence(list(bundles)))
    paths.append(plot_all_instances_summary(list(bundles)))
    paths.append(plot_log_summary(list(bundles), "runtime"))
    paths.append(plot_log_summary(list(bundles), "gap"))

    return paths
