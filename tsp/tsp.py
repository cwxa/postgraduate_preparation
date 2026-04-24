import math
import random
import time
from dataclasses import dataclass, field
from itertools import combinations, permutations
from pathlib import Path
from typing import Callable, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


try:
    plt.style.use("seaborn-v0_8-whitegrid")
except OSError:
    pass


EPSILON = 1e-9
HISTORY_INTERVAL = 500
ROUTE_COLORS = ["#2563eb", "#f59e0b", "#16a34a", "#7c3aed", "#dc2626", "#0891b2"]


@dataclass(frozen=True)
class InstanceSpec:
    """描述一次实验实例的配置。"""

    name: str
    city_count: int
    seed: int
    baseline_label: str
    sa_temp: float
    sa_cooling: float
    sa_steps: int


@dataclass
class AlgorithmResult:
    """保存单个算法的结果，避免到处传字典。"""

    name: str
    tour: list[int]
    cost: float
    time_ms: float
    history: list[tuple[int, float, float]] = field(default_factory=list)

    def gap_pct(self, baseline_cost: float) -> float:
        """计算相对基准解的误差率。"""
        if abs(baseline_cost) < EPSILON:
            return 0.0
        return ((self.cost - baseline_cost) / baseline_cost) * 100

    def route_preview(self, max_visible: int = 7) -> str:
        """把较长路径压缩成终端友好的预览。"""
        if len(self.tour) <= max_visible:
            return "->".join(map(str, self.tour))

        head_count = max_visible // 2
        tail_count = max_visible - head_count
        head = "->".join(map(str, self.tour[:head_count]))
        tail = "->".join(map(str, self.tour[-tail_count:]))
        return f"{head}->...->{tail}"


@dataclass
class ExperimentBundle:
    """把一次实例实验的所有数据收拢到一起，方便打印和画图。"""

    spec: InstanceSpec
    cities: list[tuple[int, int]]
    baseline_cost: float
    results: list[AlgorithmResult]
    by_name: dict[str, AlgorithmResult]


def euclidean_distance(city_a: tuple[int, int], city_b: tuple[int, int]) -> float:
    """计算两个城市之间的欧氏距离。"""
    return math.hypot(city_a[0] - city_b[0], city_a[1] - city_b[1])


def build_distance_matrix(cities: list[tuple[int, int]]) -> list[list[float]]:
    """根据城市坐标构建对称距离矩阵。"""
    n = len(cities)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            distance = euclidean_distance(cities[i], cities[j])
            dist[i][j] = distance
            dist[j][i] = distance
    return dist


def tour_cost(dist: list[list[float]], tour: list[int]) -> float:
    """计算一条完整回路的总代价。"""
    return sum(dist[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))


def format_time_ms(value: float) -> str:
    """根据数值量级决定保留位数。"""
    if value < 1:
        return f"{value:.3f}"
    if value < 100:
        return f"{value:.2f}"
    return f"{value:.1f}"


def brute_force_tsp(dist: list[list[float]]) -> tuple[list[int], float]:
    """暴力枚举所有访问顺序，作为小规模实例的最优参考。"""
    n = len(dist)
    if n <= 1:
        return [0, 0], 0.0

    best_tour = None
    best_cost = float("inf")
    for order in permutations(range(1, n)):
        candidate = [0, *order, 0]
        candidate_cost = tour_cost(dist, candidate)
        if candidate_cost < best_cost:
            best_cost = candidate_cost
            best_tour = candidate
    return best_tour, best_cost


def nearest_neighbor_tsp(
    dist: list[list[float]], start: int = 0
) -> tuple[list[int], float]:
    """最近邻贪心：每次都走向最近的未访问城市。"""
    n = len(dist)
    if n <= 1:
        return [start, start], 0.0

    unvisited = set(range(n))
    unvisited.remove(start)
    tour = [start]
    current = start

    while unvisited:
        next_city = min(unvisited, key=lambda city: dist[current][city])
        tour.append(next_city)
        unvisited.remove(next_city)
        current = next_city

    tour.append(start)
    return tour, tour_cost(dist, tour)


def held_karp_tsp(dist: list[list[float]]) -> tuple[list[int], float]:
    """Held-Karp 状压 DP：中小规模 TSP 的经典精确算法。"""
    n = len(dist)
    if n <= 1:
        return [0, 0], 0.0

    dp: dict[tuple[int, int], tuple[float, int]] = {}
    for city in range(1, n):
        mask = 1 << city
        dp[(mask, city)] = (dist[0][city], 0)

    for subset_size in range(2, n):
        for subset in combinations(range(1, n), subset_size):
            mask = 0
            for city in subset:
                mask |= 1 << city

            for end_city in subset:
                prev_mask = mask ^ (1 << end_city)
                best_cost = float("inf")
                best_prev = None

                for prev_city in subset:
                    if prev_city == end_city:
                        continue
                    prev_cost, _ = dp[(prev_mask, prev_city)]
                    candidate = prev_cost + dist[prev_city][end_city]
                    if candidate < best_cost:
                        best_cost = candidate
                        best_prev = prev_city

                dp[(mask, end_city)] = (best_cost, best_prev)

    full_mask = 0
    for city in range(1, n):
        full_mask |= 1 << city

    best_cost = float("inf")
    last_city = None
    for city in range(1, n):
        candidate = dp[(full_mask, city)][0] + dist[city][0]
        if candidate < best_cost:
            best_cost = candidate
            last_city = city

    reversed_path = [last_city]
    mask = full_mask
    current = last_city
    while True:
        _, prev_city = dp[(mask, current)]
        if prev_city == 0:
            break
        reversed_path.append(prev_city)
        mask ^= 1 << current
        current = prev_city

    route = [0] + list(reversed(reversed_path)) + [0]
    return route, best_cost


def two_opt_swap(tour: list[int], i: int, k: int) -> list[int]:
    """执行一次 2-opt 交换。"""
    return tour[:i] + list(reversed(tour[i : k + 1])) + tour[k + 1 :]


def two_opt_delta(dist: list[list[float]], tour: list[int], i: int, k: int) -> float:
    """增量计算 2-opt 交换的代价变化。"""
    a, b = tour[i - 1], tour[i]
    c, d = tour[k], tour[k + 1]
    old_edges = dist[a][b] + dist[c][d]
    new_edges = dist[a][c] + dist[b][d]
    return new_edges - old_edges


def two_opt_tsp(
    dist: list[list[float]], initial_tour: list[int]
) -> tuple[list[int], float]:
    """使用 best-improvement 版本的 2-opt 做局部优化。"""
    best_tour = initial_tour[:]
    best_cost = tour_cost(dist, best_tour)

    while True:
        best_delta = 0.0
        best_move = None

        for i in range(1, len(best_tour) - 2):
            for k in range(i + 1, len(best_tour) - 1):
                delta = two_opt_delta(dist, best_tour, i, k)
                if delta < best_delta - EPSILON:
                    best_delta = delta
                    best_move = (i, k)

        if best_move is None:
            break

        best_tour = two_opt_swap(best_tour, best_move[0], best_move[1])
        best_cost += best_delta

    return best_tour, best_cost


def random_two_opt_move(
    tour: list[int], rng: random.Random
) -> tuple[int, int]:
    """为 SA 随机采样一个 2-opt 邻域动作。"""
    return tuple(sorted(rng.sample(range(1, len(tour) - 1), 2)))


def simulated_annealing_tsp(
    dist: list[list[float]],
    initial_tour: list[int] | None = None,
    initial_temp: float = 300.0,
    cooling_rate: float = 0.995,
    max_steps: int = 5000,
    seed: int = 42,
) -> tuple[list[int], float, list[tuple[int, float, float]]]:
    """模拟退火：用 2-opt 邻域在大规模搜索空间中跳出局部最优。"""
    rng = random.Random(seed)

    if initial_tour is None:
        initial_tour, _ = nearest_neighbor_tsp(dist)

    current_tour = initial_tour[:]
    current_cost = tour_cost(dist, current_tour)
    best_tour = current_tour[:]
    best_cost = current_cost
    temperature = initial_temp
    history = [(0, best_cost, temperature)]

    for step in range(1, max_steps + 1):
        i, k = random_two_opt_move(current_tour, rng)
        delta = two_opt_delta(dist, current_tour, i, k)

        # 温度较高时允许一定概率接受更差解，用来跳出局部最优。
        accept = delta < 0 or rng.random() < math.exp(-delta / max(temperature, EPSILON))
        if accept:
            current_tour = two_opt_swap(current_tour, i, k)
            current_cost += delta

            if current_cost < best_cost - EPSILON:
                best_tour = current_tour[:]
                best_cost = current_cost

        temperature *= cooling_rate

        if step % HISTORY_INTERVAL == 0 or step == max_steps:
            history.append((step, best_cost, temperature))

        if temperature < 1e-4:
            break

    return best_tour, best_cost, history


def run_solver(
    name: str,
    solver: Callable,
    dist: list[list[float]],
    *args,
    **kwargs,
) -> AlgorithmResult:
    """统一记录求解耗时，并兼容是否返回 history。"""
    start_time = time.perf_counter()
    outcome = solver(dist, *args, **kwargs)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    if len(outcome) == 2:
        tour, cost = outcome
        history = []
    else:
        tour, cost, history = outcome

    return AlgorithmResult(
        name=name,
        tour=tour,
        cost=cost,
        time_ms=elapsed_ms,
        history=history,
    )


def is_valid_tour(tour: list[int], city_count: int) -> bool:
    """检查回路是否合法。"""
    return (
        len(tour) == city_count + 1
        and tour[0] == 0
        and tour[-1] == 0
        and set(tour[:-1]) == set(range(city_count))
    )


def validate_results(results: Iterable[AlgorithmResult], city_count: int) -> None:
    """集中校验回路合法性。"""
    for result in results:
        assert is_valid_tour(result.tour, city_count), f"Invalid tour: {result.name}"


def generate_cities(count: int, seed: int = 42) -> list[tuple[int, int]]:
    """固定随机种子，保证实验可复现。"""
    random.seed(seed)
    return [(random.randint(0, 100), random.randint(0, 100)) for _ in range(count)]


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """打印简洁的等宽表格。"""
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
    """打印实验指标说明，帮助理解 baseline 和 gap。"""
    print("Metric guide:")
    print("  baseline = reference solution used for comparison in the current instance.")
    print("  gap (%)  = (cost - baseline) / baseline * 100%.")
    print("  small/medium instances use exact-optimal baselines;")
    print("  the large instance uses the best heuristic result in the compared set.")


def print_sa_summary(result: AlgorithmResult) -> None:
    """把 SA 的关键收敛节点压缩为一行摘要。"""
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
    """输出一组实例的实验结果表格。"""
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
    """按网格形式打印城市坐标，方便和图片对照。"""
    print(f"\n{title}")
    cells = [f"{idx:>2}:({x:>3},{y:>3})" for idx, (x, y) in enumerate(cities)]
    for start in range(0, len(cells), columns):
        print("  " + "   ".join(cells[start : start + columns]))


def get_output_dir() -> Path:
    """创建图片根目录。"""
    output_dir = Path(__file__).resolve().parent / "figures"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def get_output_subdir(name: str) -> Path:
    """创建按实例规模划分的图片子目录。"""
    subdir = get_output_dir() / name
    subdir.mkdir(exist_ok=True)
    return subdir


def annotate_bar_values(ax, bars, formatter: Callable[[float], str], offset_ratio: float = 0.015) -> None:
    """给柱状图加数值标签，提升可读性。"""
    max_height = max((bar.get_height() for bar in bars), default=0.0)
    offset = max(max_height * offset_ratio, 0.02)
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            formatter(height),
            ha="center",
            va="bottom",
            fontsize=8.5,
            rotation=0,
        )


def annotate_cities(ax, cities: list[tuple[int, int]]) -> None:
    """给每个城市加编号，便于核对路径顺序。"""
    for idx, (x, y) in enumerate(cities):
        ax.text(
            x + 1.4,
            y + 1.4,
            str(idx),
            fontsize=8.5,
            color="#1f2937",
            zorder=5,
        )


def draw_direction_arrows(ax, xs: list[float], ys: list[float], color: str) -> None:
    """沿路径抽样绘制方向箭头，让路线方向更直观。"""
    for index in range(0, len(xs) - 1, 2):
        ax.annotate(
            "",
            xy=(xs[index + 1], ys[index + 1]),
            xytext=(xs[index], ys[index]),
            arrowprops=dict(
                arrowstyle="->",
                color=color,
                lw=1.2,
                alpha=0.75,
                shrinkA=7,
                shrinkB=7,
            ),
            zorder=4,
        )


def add_route_info_box(ax, result: AlgorithmResult, baseline_cost: float) -> None:
    """在子图内显示 cost、gap 和 time，减轻标题负担。"""
    gap = result.gap_pct(baseline_cost)
    info = (
        f"cost = {result.cost:.2f}\n"
        f"gap  = {gap:.2f}%\n"
        f"time = {format_time_ms(result.time_ms)} ms"
    )
    ax.text(
        0.03,
        0.04,
        info,
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment="bottom",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.82),
    )


def plot_tour(
    ax,
    cities: list[tuple[int, int]],
    result: AlgorithmResult,
    baseline_cost: float,
    line_color: str,
) -> None:
    """绘制单个算法的路径图。"""
    xs = [cities[city][0] for city in result.tour]
    ys = [cities[city][1] for city in result.tour]
    city_x = [city[0] for city in cities]
    city_y = [city[1] for city in cities]

    ax.scatter(
        city_x,
        city_y,
        s=70,
        color="#0f172a",
        edgecolors="white",
        linewidths=0.8,
        zorder=3,
    )
    ax.scatter(
        cities[0][0],
        cities[0][1],
        s=140,
        color="#dc2626",
        edgecolors="white",
        linewidths=1.5,
        zorder=4,
    )
    ax.plot(xs, ys, color=line_color, linewidth=2.4, alpha=0.92, zorder=2)
    draw_direction_arrows(ax, xs, ys, line_color)
    annotate_cities(ax, cities)
    add_route_info_box(ax, result, baseline_cost)

    padding = 6
    ax.set_xlim(min(city_x) - padding, max(city_x) + padding)
    ax.set_ylim(min(city_y) - padding, max(city_y) + padding)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(result.name, fontsize=12, fontweight="bold")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(alpha=0.25, linestyle="--")


def save_route_comparison(
    cities: list[tuple[int, int]],
    results: list[AlgorithmResult],
    baseline_cost: float,
    file_path: Path,
    figure_title: str,
) -> None:
    """保存路径对比图。"""
    fig, axes = plt.subplots(1, len(results), figsize=(5.0 * len(results), 5.2))
    if len(results) == 1:
        axes = [axes]

    for ax, result, color in zip(axes, results, ROUTE_COLORS):
        plot_tour(ax, cities, result, baseline_cost, color)

    fig.suptitle(figure_title, fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0.02, 1, 0.94])
    fig.savefig(file_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_sa_convergence(
    convergence_specs: list[dict[str, object]],
    file_path: Path,
    figure_title: str,
) -> None:
    """保存 SA 收敛图，同时展示 gap 和温度变化。"""
    fig, axes = plt.subplots(
        1, len(convergence_specs), figsize=(6.2 * len(convergence_specs), 4.9)
    )
    if len(convergence_specs) == 1:
        axes = [axes]

    colors = ["#7c3aed", "#0891b2", "#dc2626"]
    for ax, spec, color in zip(axes, convergence_specs, colors):
        result = spec["result"]
        baseline_cost = spec["baseline_cost"]
        steps = [step for step, _, _ in result.history]
        gaps = [
            ((cost - baseline_cost) / baseline_cost) * 100
            for _, cost, _ in result.history
        ]
        temps = [temp for _, _, temp in result.history]

        ax.plot(
            steps,
            gaps,
            marker="o",
            linewidth=2.4,
            markersize=4.5,
            color=color,
            label="Gap vs baseline",
        )
        ax.axhline(0.0, color="#16a34a", linestyle="--", linewidth=1.8)
        ax.set_title(
            f"{spec['label']}\nstart={gaps[0]:.2f}% -> end={gaps[-1]:.2f}%",
            fontsize=12,
            fontweight="bold",
        )
        ax.set_xlabel("Iteration Step")
        ax.set_ylabel("Gap vs baseline (%)")
        ax.grid(alpha=0.25, linestyle="--")

        twin = ax.twinx()
        twin.plot(
            steps,
            temps,
            color="#94a3b8",
            linestyle=":",
            linewidth=1.8,
            label="Temperature",
        )
        twin.set_ylabel("Temperature")
        twin.grid(False)

        lines, labels = ax.get_legend_handles_labels()
        twin_lines, twin_labels = twin.get_legend_handles_labels()
        ax.legend(lines + twin_lines, labels + twin_labels, loc="upper right", fontsize=8)

    fig.suptitle(figure_title, fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0.02, 1, 0.94])
    fig.savefig(file_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_summary_bars(
    results: list[AlgorithmResult],
    baseline_cost: float,
    baseline_label: str,
    file_path: Path,
    figure_title: str,
) -> None:
    """保存实验总览条形图，对比误差率和耗时。"""
    names = [result.name for result in results]
    gaps = [result.gap_pct(baseline_cost) for result in results]
    times = [result.time_ms for result in results]

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))
    gap_bars = axes[0].bar(names, gaps, color=ROUTE_COLORS[: len(results)])
    axes[0].set_title("Gap vs baseline")
    axes[0].set_ylabel("Gap (%)")
    axes[0].tick_params(axis="x", rotation=18)
    axes[0].axhline(0.0, color="#16a34a", linestyle="--", linewidth=1.6)
    annotate_bar_values(axes[0], gap_bars, lambda value: f"{value:.2f}%")

    time_bars = axes[1].bar(names, times, color=ROUTE_COLORS[: len(results)])
    axes[1].set_title("Runtime")
    axes[1].set_ylabel("Time (ms)")
    axes[1].tick_params(axis="x", rotation=18)
    annotate_bar_values(axes[1], time_bars, lambda value: format_time_ms(value))

    fig.suptitle(figure_title, fontsize=15, fontweight="bold")
    fig.text(
        0.5,
        0.02,
        f"Baseline = {baseline_label} ({baseline_cost:.2f}); gap = (cost - baseline) / baseline * 100%",
        ha="center",
        fontsize=9,
        color="#374151",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.94])
    fig.savefig(file_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_cross_instance_summary(
    bundles: list[ExperimentBundle],
    file_path: Path,
    figure_title: str,
) -> None:
    """保存跨实例总览图，比较每个实例中关键方法的误差率和耗时。"""
    focus_methods = ["Nearest Neighbor", "Nearest + 2-opt", "2-opt + SA", "SA + 2-opt"]
    instance_labels = [f"{bundle.spec.city_count} cities" for bundle in bundles]

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.0))
    bar_width = 0.18
    x_positions = list(range(len(bundles)))

    gap_bar_groups = []
    time_bar_groups = []
    for method_index, method_name in enumerate(focus_methods):
        offsets = [x + (method_index - 1.5) * bar_width for x in x_positions]
        gaps = [
            bundle.by_name[method_name].gap_pct(bundle.baseline_cost)
            for bundle in bundles
        ]
        times = [bundle.by_name[method_name].time_ms for bundle in bundles]

        color = ROUTE_COLORS[method_index]
        gap_bar_groups.append(
            axes[0].bar(offsets, gaps, width=bar_width, color=color, label=method_name)
        )
        time_bar_groups.append(
            axes[1].bar(offsets, times, width=bar_width, color=color, label=method_name)
        )

    axes[0].set_title("Gap vs baseline across instances")
    axes[0].set_ylabel("Gap (%)")
    axes[0].set_xticks(x_positions)
    axes[0].set_xticklabels(instance_labels)
    axes[0].axhline(0.0, color="#16a34a", linestyle="--", linewidth=1.5)

    axes[1].set_title("Runtime across instances")
    axes[1].set_ylabel("Time (ms)")
    axes[1].set_xticks(x_positions)
    axes[1].set_xticklabels(instance_labels)

    for bars in gap_bar_groups:
        annotate_bar_values(axes[0], bars, lambda value: f"{value:.2f}%")
    for bars in time_bar_groups:
        annotate_bar_values(axes[1], bars, lambda value: format_time_ms(value), offset_ratio=0.01)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle(figure_title, fontsize=15, fontweight="bold", y=0.98)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.93),
        ncol=4,
        frameon=False,
    )
    fig.text(
        0.5,
        0.02,
        "Each instance uses its own baseline: exact optimum for small/medium, best heuristic for large.",
        ha="center",
        fontsize=9,
        color="#374151",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.84])
    fig.savefig(file_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_runtime_log_summary(
    bundles: list[ExperimentBundle],
    file_path: Path,
    figure_title: str,
) -> None:
    """保存跨实例运行时间对数坐标图，突出毫秒级跨度差异。"""
    focus_methods = ["Nearest Neighbor", "Nearest + 2-opt", "2-opt + SA", "SA + 2-opt"]
    instance_labels = [f"{bundle.spec.city_count} cities" for bundle in bundles]
    x_positions = list(range(len(bundles)))
    bar_width = 0.18

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    bar_groups = []

    for method_index, method_name in enumerate(focus_methods):
        offsets = [x + (method_index - 1.5) * bar_width for x in x_positions]
        times = [bundle.by_name[method_name].time_ms for bundle in bundles]
        bars = ax.bar(
            offsets,
            times,
            width=bar_width,
            color=ROUTE_COLORS[method_index],
            label=method_name,
        )
        bar_groups.append(bars)

    ax.set_title("Runtime across instances (log scale)")
    ax.set_ylabel("Time (ms, log scale)")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(instance_labels)
    ax.set_yscale("log")
    ax.grid(alpha=0.25, linestyle="--", axis="y", which="both")

    for bars in bar_groups:
        annotate_bar_values(ax, bars, lambda value: format_time_ms(value), offset_ratio=0.05)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.96), ncol=4, frameon=False)
    fig.suptitle(figure_title, fontsize=15, fontweight="bold", y=0.99)
    fig.text(
        0.5,
        0.02,
        "Log scale makes sub-millisecond and multi-millisecond runtimes visible in one chart.",
        ha="center",
        fontsize=9,
        color="#374151",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.88])
    fig.savefig(file_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_gap_log_summary(
    bundles: list[ExperimentBundle],
    file_path: Path,
    figure_title: str,
) -> None:
    """保存 gap 的对数视角图，使用 symlog 兼容 0% 的柱子。"""
    focus_methods = ["Nearest Neighbor", "Nearest + 2-opt", "2-opt + SA", "SA + 2-opt"]
    instance_labels = [f"{bundle.spec.city_count} cities" for bundle in bundles]
    x_positions = list(range(len(bundles)))
    bar_width = 0.18

    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    bar_groups = []

    for method_index, method_name in enumerate(focus_methods):
        offsets = [x + (method_index - 1.5) * bar_width for x in x_positions]
        gaps = [bundle.by_name[method_name].gap_pct(bundle.baseline_cost) for bundle in bundles]
        bars = ax.bar(
            offsets,
            gaps,
            width=bar_width,
            color=ROUTE_COLORS[method_index],
            label=method_name,
        )
        bar_groups.append(bars)

    ax.set_title("Gap across instances (symlog scale)")
    ax.set_ylabel("Gap (%, symlog scale)")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(instance_labels)
    ax.set_yscale("symlog", linthresh=0.1)
    ax.axhline(0.0, color="#16a34a", linestyle="--", linewidth=1.5)
    ax.grid(alpha=0.25, linestyle="--", axis="y", which="both")

    for bars in bar_groups:
        annotate_bar_values(ax, bars, lambda value: f"{value:.2f}%", offset_ratio=0.08)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.96), ncol=4, frameon=False)
    fig.suptitle(figure_title, fontsize=15, fontweight="bold", y=0.99)
    fig.text(
        0.5,
        0.02,
        "Symlog scale is used so 0.00% gaps remain visible while larger gaps still separate clearly.",
        ha="center",
        fontsize=9,
        color="#374151",
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.88])
    fig.savefig(file_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def generate_visual_demo(
    small_bundle: ExperimentBundle,
    medium_bundle: ExperimentBundle,
    large_bundle: ExperimentBundle,
) -> list[Path]:
    """统一生成本章用到的全部图片。"""
    small_dir = get_output_subdir("small")
    medium_dir = get_output_subdir("medium")
    large_dir = get_output_subdir("large")
    cross_dir = get_output_subdir("cross_instance")

    save_route_comparison(
        small_bundle.cities,
        [
            small_bundle.by_name["Brute Force"],
            small_bundle.by_name["Nearest Neighbor"],
            small_bundle.by_name["Nearest + 2-opt"],
            small_bundle.by_name["2-opt + SA"],
        ],
        small_bundle.baseline_cost,
        small_dir / "routes.png",
        "TSP Small Instance Route Comparison",
    )

    save_route_comparison(
        medium_bundle.cities,
        [
            medium_bundle.by_name["Nearest Neighbor"],
            medium_bundle.by_name["Held-Karp DP"],
            medium_bundle.by_name["Nearest + 2-opt"],
            medium_bundle.by_name["2-opt + SA"],
        ],
        medium_bundle.baseline_cost,
        medium_dir / "routes.png",
        "TSP Medium Instance Route Comparison",
    )

    save_route_comparison(
        large_bundle.cities,
        [
            large_bundle.by_name["Nearest Neighbor"],
            large_bundle.by_name["Nearest + 2-opt"],
            large_bundle.by_name["2-opt + SA"],
        ],
        large_bundle.baseline_cost,
        large_dir / "routes.png",
        "TSP Large Instance Heuristic Comparison",
    )

    save_summary_bars(
        [
            small_bundle.by_name["Brute Force"],
            small_bundle.by_name["Held-Karp DP"],
            small_bundle.by_name["Nearest Neighbor"],
            small_bundle.by_name["Nearest + 2-opt"],
            small_bundle.by_name["2-opt + SA"],
            small_bundle.by_name["SA + 2-opt"],
        ],
        small_bundle.baseline_cost,
        small_bundle.spec.baseline_label,
        small_dir / "summary.png",
        "TSP Small Instance Performance Overview",
    )

    save_summary_bars(
        [
            medium_bundle.by_name["Nearest Neighbor"],
            medium_bundle.by_name["Held-Karp DP"],
            medium_bundle.by_name["Nearest + 2-opt"],
            medium_bundle.by_name["2-opt + SA"],
            medium_bundle.by_name["SA + 2-opt"],
        ],
        medium_bundle.baseline_cost,
        medium_bundle.spec.baseline_label,
        medium_dir / "summary.png",
        "TSP Medium Instance Performance Overview",
    )

    save_summary_bars(
        [
            large_bundle.by_name["Nearest Neighbor"],
            large_bundle.by_name["Nearest + 2-opt"],
            large_bundle.by_name["2-opt + SA"],
            large_bundle.by_name["SA + 2-opt"],
        ],
        large_bundle.baseline_cost,
        large_bundle.spec.baseline_label,
        large_dir / "summary.png",
        "TSP Large Instance Performance Overview",
    )

    save_sa_convergence(
        [
            {
                "label": "Small Instance",
                "result": small_bundle.by_name["2-opt + SA"],
                "baseline_cost": small_bundle.baseline_cost,
            },
            {
                "label": "Medium Instance",
                "result": medium_bundle.by_name["2-opt + SA"],
                "baseline_cost": medium_bundle.baseline_cost,
            },
            {
                "label": "Large Instance",
                "result": large_bundle.by_name["2-opt + SA"],
                "baseline_cost": large_bundle.baseline_cost,
            },
        ],
        cross_dir / "sa_convergence.png",
        "Simulated Annealing Convergence Snapshots",
    )

    save_cross_instance_summary(
        [small_bundle, medium_bundle, large_bundle],
        cross_dir / "all_instances_summary.png",
        "TSP Cross-Instance Performance Overview",
    )

    save_runtime_log_summary(
        [small_bundle, medium_bundle, large_bundle],
        cross_dir / "runtime_log_summary.png",
        "TSP Runtime Overview (Log Scale)",
    )

    save_gap_log_summary(
        [small_bundle, medium_bundle, large_bundle],
        cross_dir / "gap_log_summary.png",
        "TSP Gap Overview (Log-Compatible Scale)",
    )

    return [
        small_dir / "routes.png",
        small_dir / "summary.png",
        medium_dir / "routes.png",
        medium_dir / "summary.png",
        large_dir / "routes.png",
        large_dir / "summary.png",
        cross_dir / "sa_convergence.png",
        cross_dir / "all_instances_summary.png",
        cross_dir / "runtime_log_summary.png",
        cross_dir / "gap_log_summary.png",
    ]


def build_result_map(results: list[AlgorithmResult]) -> dict[str, AlgorithmResult]:
    """把结果列表转成名称索引，方便后续画图和查询。"""
    return {result.name: result for result in results}


def run_small_instance(spec: InstanceSpec) -> ExperimentBundle:
    """运行小规模实例，包含精确解和启发式解。"""
    cities = generate_cities(spec.city_count, spec.seed)
    dist = build_distance_matrix(cities)

    results = [
        run_solver("Brute Force", brute_force_tsp, dist),
        run_solver("Nearest Neighbor", nearest_neighbor_tsp, dist),
        run_solver("Held-Karp DP", held_karp_tsp, dist),
    ]

    nearest = build_result_map(results)["Nearest Neighbor"]
    results.append(run_solver("Nearest + 2-opt", two_opt_tsp, dist, nearest.tour))

    nearest_2opt = build_result_map(results)["Nearest + 2-opt"]
    results.append(
        run_solver(
            "2-opt + SA",
            simulated_annealing_tsp,
            dist,
            nearest_2opt.tour,
            initial_temp=spec.sa_temp,
            cooling_rate=spec.sa_cooling,
            max_steps=spec.sa_steps,
            seed=spec.seed,
        )
    )

    sa_result = build_result_map(results)["2-opt + SA"]
    results.append(run_solver("SA + 2-opt", two_opt_tsp, dist, sa_result.tour))

    validate_results(results, spec.city_count)
    baseline_cost = build_result_map(results)["Brute Force"].cost
    assert abs(baseline_cost - build_result_map(results)["Held-Karp DP"].cost) < EPSILON
    return ExperimentBundle(spec, cities, baseline_cost, results, build_result_map(results))


def run_medium_instance(spec: InstanceSpec) -> ExperimentBundle:
    """运行中规模实例，保留 Held-Karp 最优解做对照。"""
    cities = generate_cities(spec.city_count, spec.seed)
    dist = build_distance_matrix(cities)

    results = [
        run_solver("Nearest Neighbor", nearest_neighbor_tsp, dist),
        run_solver("Held-Karp DP", held_karp_tsp, dist),
    ]

    nearest = build_result_map(results)["Nearest Neighbor"]
    results.append(run_solver("Nearest + 2-opt", two_opt_tsp, dist, nearest.tour))

    nearest_2opt = build_result_map(results)["Nearest + 2-opt"]
    results.append(
        run_solver(
            "2-opt + SA",
            simulated_annealing_tsp,
            dist,
            nearest_2opt.tour,
            initial_temp=spec.sa_temp,
            cooling_rate=spec.sa_cooling,
            max_steps=spec.sa_steps,
            seed=spec.seed,
        )
    )

    sa_result = build_result_map(results)["2-opt + SA"]
    results.append(run_solver("SA + 2-opt", two_opt_tsp, dist, sa_result.tour))

    validate_results(results, spec.city_count)
    baseline_cost = build_result_map(results)["Held-Karp DP"].cost
    return ExperimentBundle(spec, cities, baseline_cost, results, build_result_map(results))


def run_large_instance(spec: InstanceSpec) -> ExperimentBundle:
    """运行大规模实例，只保留启发式算法。"""
    cities = generate_cities(spec.city_count, spec.seed)
    dist = build_distance_matrix(cities)

    results = [run_solver("Nearest Neighbor", nearest_neighbor_tsp, dist)]
    nearest = results[0]
    results.append(run_solver("Nearest + 2-opt", two_opt_tsp, dist, nearest.tour))

    nearest_2opt = build_result_map(results)["Nearest + 2-opt"]
    results.append(
        run_solver(
            "2-opt + SA",
            simulated_annealing_tsp,
            dist,
            nearest_2opt.tour,
            initial_temp=spec.sa_temp,
            cooling_rate=spec.sa_cooling,
            max_steps=spec.sa_steps,
            seed=spec.seed,
        )
    )

    sa_result = build_result_map(results)["2-opt + SA"]
    results.append(run_solver("SA + 2-opt", two_opt_tsp, dist, sa_result.tour))

    validate_results(results, spec.city_count)
    baseline_cost = min(result.cost for result in results)
    return ExperimentBundle(spec, cities, baseline_cost, results, build_result_map(results))


def run_demo() -> None:
    """运行整套实验、打印总结，并生成可视化图片。"""
    small_spec = InstanceSpec(
        name="TSP Small Instance (9 cities)",
        city_count=9,
        seed=7,
        baseline_label="Brute Force / Held-Karp",
        sa_temp=250.0,
        sa_cooling=0.998,
        sa_steps=8000,
    )
    medium_spec = InstanceSpec(
        name="TSP Medium Instance (12 cities)",
        city_count=12,
        seed=21,
        baseline_label="Held-Karp DP",
        sa_temp=250.0,
        sa_cooling=0.998,
        sa_steps=16000,
    )
    large_spec = InstanceSpec(
        name="TSP Large Instance (18 cities, heuristic only)",
        city_count=18,
        seed=33,
        baseline_label="Best Heuristic",
        sa_temp=250.0,
        sa_cooling=0.998,
        sa_steps=20000,
    )

    small_bundle = run_small_instance(small_spec)
    medium_bundle = run_medium_instance(medium_spec)
    large_bundle = run_large_instance(large_spec)

    print_metric_guide()
    for bundle in [small_bundle, medium_bundle, large_bundle]:
        print_instance_report(bundle)

    print_city_summary("Medium instance city coordinates:", medium_bundle.cities)

    generated_files = generate_visual_demo(
        small_bundle,
        medium_bundle,
        large_bundle,
    )

    print("\nGenerated figures:")
    for file_path in generated_files:
        print(f"  {file_path}")


if __name__ == "__main__":
    run_demo()
