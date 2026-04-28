import os
from typing import List, Optional, Dict, Any, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from flowshop.flowshop_types import Schedule
from flowshop.logging_config import get_logger

logger = get_logger(__name__)


def plot_gantt(
    schedule: Schedule,
    title: str,
    filename: str,
    machine_names: Optional[List[str]] = None,
    show_grid: bool = True
) -> str:
    """
    绘制2机FlowShop甘特图

    参数:
        schedule: 包含M1和M2任务列表的调度结果
        title: 图表标题
        filename: 保存文件名
        machine_names: 机器名称列表，默认为["Machine 1", "Machine 2"]
        show_grid: 是否显示网格

    返回:
        保存路径
    """
    start_time = None
    try:
        import time
        start_time = time.time()
        logger.info(f"[plot_gantt] Entry, title: '{title}', file: {filename}")

        if "M1" not in schedule or "M2" not in schedule:
            raise ValueError("schedule must contain 'M1' and 'M2' keys")

        if machine_names is None:
            machine_names = ["Machine 1", "Machine 2"]

        if len(machine_names) != 2:
            raise ValueError("machine_names must have exactly 2 names")

        fig, ax = plt.subplots(figsize=(12, 4))

        colors = plt.cm.Set3(range(len(schedule["M1"]) + len(schedule["M2"])))
        color_idx = 0

        for machine_index, machine_key in enumerate(["M1", "M2"]):
            for job_id, start, duration in schedule[machine_key]:
                color = colors[color_idx % len(colors)]
                ax.barh(
                    machine_index,
                    duration,
                    left=start,
                    height=0.6,
                    color=color,
                    edgecolor='black',
                    linewidth=0.5
                )
                ax.text(
                    start + duration / 2,
                    machine_index,
                    f"J{job_id}",
                    ha='center',
                    va='center',
                    fontsize=8,
                    fontweight='bold'
                )
                color_idx += 1

        ax.set_yticks([0, 1])
        ax.set_yticklabels(machine_names)
        ax.set_xlabel("Time", fontsize=10)
        ax.set_ylabel("Machine", fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')

        if show_grid:
            ax.grid(axis='x', linestyle='--', alpha=0.7)

        ax.set_xlim(left=0)
        ax.set_ylim(-0.5, 1.5)

        plt.tight_layout()

        save_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "flowshop",
            "figures",
            filename
        )
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

        elapsed = time.time() - start_time
        logger.info(f"[plot_gantt] Done, saved: {save_path}, elapsed: {elapsed*1000:.2f}ms")

        plt.close()
        return save_path

    except Exception as e:
        logger.error(f"[plot_gantt] Failed: {str(e)}")
        raise


def plot_gantt_multi(
    schedule_list: List[Tuple],
    title: str,
    filename: str,
    num_machines: int,
    job_ids: Optional[List[int]] = None,
    show_grid: bool = True
) -> str:
    """
    绘制多机FlowShop甘特图

    参数:
        schedule_list: 调度列表，元素为(job_id, machine_idx, start, duration)
        title: 图表标题
        filename: 保存文件名
        num_machines: 机器数量
        job_ids: 作业ID列表（用于颜色映射）
        show_grid: 是否显示网格

    返回:
        保存路径
    """
    start_time = None
    try:
        import time
        start_time = time.time()
        logger.info(f"[plot_gantt_multi] Entry, title: '{title}', machines: {num_machines}")

        if not schedule_list:
            raise ValueError("schedule_list is empty")

        if job_ids is None:
            job_ids = list(set([s[0] for s in schedule_list]))

        color_map = {jid: plt.cm.tab20(i % 20) for i, jid in enumerate(job_ids)}

        fig, ax = plt.subplots(figsize=(14, 6))

        for job_id, machine, start, duration in schedule_list:
            ax.barh(
                machine,
                duration,
                left=start,
                height=0.6,
                color=color_map[job_id],
                edgecolor='black',
                linewidth=0.5
            )
            ax.text(
                start + duration / 2,
                machine,
                f"J{job_id}",
                ha='center',
                va='center',
                fontsize=7,
                fontweight='bold'
            )

        machine_labels = [f"M{m+1}" for m in range(num_machines)]
        ax.set_yticks(range(num_machines))
        ax.set_yticklabels(machine_labels)
        ax.set_xlabel("Time", fontsize=10)
        ax.set_ylabel("Machine", fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')

        if show_grid:
            ax.grid(axis='x', linestyle='--', alpha=0.7)

        max_time = max(s[2] + s[3] for s in schedule_list) if schedule_list else 100
        ax.set_xlim(left=0, right=max_time * 1.05)
        ax.set_ylim(-0.5, num_machines - 0.5)

        legend_patches = [mpatches.Patch(color=color_map[jid], label=f"J{jid}") for jid in sorted(job_ids)]
        ax.legend(handles=legend_patches, loc='upper right', ncol=min(10, len(job_ids)), fontsize=7)

        plt.tight_layout()

        save_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "flowshop",
            "figures",
            filename
        )
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

        elapsed = time.time() - start_time
        logger.info(f"[plot_gantt_multi] Done, saved: {save_path}, elapsed: {elapsed*1000:.2f}ms")

        plt.close()
        return save_path

    except Exception as e:
        logger.error(f"[plot_gantt_multi] Failed: {str(e)}")
        raise


def plot_gantt_dynamic(
    events: List[Tuple],
    title: str,
    filename: str,
    num_machines: int,
    show_legend: bool = True
) -> str:
    """
    绘制动态FlowShop仿真甘特图

    参数:
        events: 事件列表，元素为(job_id, machine, start_time, end_time, processing_time)
        title: 图表标题
        filename: 保存文件名
        num_machines: 机器数量
        show_legend: 是否显示图例

    返回:
        保存路径
    """
    start_time = None
    try:
        import time
        start_time = time.time()
        logger.info(f"[plot_gantt_dynamic] Entry, title: '{title}', machines: {num_machines}")

        if not events:
            raise ValueError("events list is empty")

        fig, ax = plt.subplots(figsize=(14, 6))

        job_ids = list(set([e[0] for e in events]))
        color_map = {jid: plt.cm.tab20(i % 20) for i, jid in enumerate(sorted(job_ids))}

        for event in events:
            if len(event) == 5:
                job_id, machine, start, end, _ = event
            else:
                job_id, machine, start, end = event
                _ = None

            duration = end - start
            ax.barh(
                machine,
                duration,
                left=start,
                height=0.6,
                color=color_map[job_id],
                edgecolor='black',
                linewidth=0.5
            )
            if duration > 5:
                ax.text(
                    start + duration / 2,
                    machine,
                    f"J{job_id}",
                    ha='center',
                    va='center',
                    fontsize=7,
                    fontweight='bold'
                )

        machine_labels = [f"M{m+1}" for m in range(num_machines)]
        ax.set_yticks(range(num_machines))
        ax.set_yticklabels(machine_labels)
        ax.set_xlabel("Time", fontsize=10)
        ax.set_ylabel("Machine", fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold')

        ax.grid(axis='x', linestyle='--', alpha=0.7)

        max_time = max(e[3] for e in events) if events else 100
        ax.set_xlim(left=0, right=max_time * 1.05)
        ax.set_ylim(-0.5, num_machines - 0.5)

        if show_legend:
            legend_patches = [mpatches.Patch(color=color_map[jid], label=f"J{jid}") for jid in sorted(job_ids)]
            ax.legend(handles=legend_patches, loc='upper right', ncol=min(10, len(job_ids)), fontsize=7)

        plt.tight_layout()

        save_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "flowshop",
            "figures",
            filename
        )
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

        elapsed = time.time() - start_time
        logger.info(f"[plot_gantt_dynamic] Done, saved: {save_path}, elapsed: {elapsed*1000:.2f}ms")

        plt.close()
        return save_path

    except Exception as e:
        logger.error(f"[plot_gantt_dynamic] Failed: {str(e)}")
        raise


def plot_comparison(
    johnson_results: List[int],
    random_results: List[int],
    filename: str = "johnson_vs_random.png",
    title: str = "Johnson vs Random Makespan Comparison"
) -> str:
    """
    绘制Johnson算法与随机序列的Makespan对比图

    参数:
        johnson_results: Johnson算法的Makespan列表
        random_results: 随机序列的Makespan列表
        filename: 保存文件名
        title: 图表标题

    返回:
        保存路径
    """
    start_time = None
    try:
        import time
        start_time = time.time()
        logger.info(f"[plot_comparison] Entry, trials: {len(johnson_results)}")

        if len(johnson_results) != len(random_results):
            raise ValueError(
                f"Result list length mismatch: Johnson={len(johnson_results)}, Random={len(random_results)}"
            )

        avg_j = sum(johnson_results) / len(johnson_results)
        avg_r = sum(random_results) / len(random_results)
        improvement = ((avg_r - avg_j) / avg_r) * 100 if avg_r > 0 else 0

        fig, ax = plt.subplots(figsize=(14, 5))

        x = range(len(johnson_results))
        ax.plot(x, johnson_results, label=f"Johnson (avg={avg_j:.2f})", alpha=0.8, linewidth=1.5)
        ax.plot(x, random_results, label=f"Random (avg={avg_r:.2f})", alpha=0.8, linewidth=1.5)

        ax.axhline(y=avg_j, color='blue', linestyle='--', alpha=0.5, linewidth=1)
        ax.axhline(y=avg_r, color='orange', linestyle='--', alpha=0.5, linewidth=1)

        ax.set_xlabel("Trial", fontsize=10)
        ax.set_ylabel("Makespan", fontsize=10)
        ax.set_title(f"{title}\n(Johnson Improvement: {improvement:.2f}%)", fontsize=12, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(axis='both', linestyle='--', alpha=0.7)

        plt.tight_layout()

        save_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "flowshop",
            "figures",
            filename
        )
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

        elapsed = time.time() - start_time
        logger.info(f"[plot_comparison] Done, Johnson avg: {avg_j:.2f}, Random avg: {avg_r:.2f}, "
                    f"improvement: {improvement:.2f}%, elapsed: {elapsed*1000:.2f}ms")

        plt.close()
        return save_path

    except Exception as e:
        logger.error(f"[plot_comparison] Failed: {str(e)}")
        raise


def plot_heuristics_comparison(
    results: Dict[str, Tuple[int, float]],
    filename: str = "heuristics_comparison.png",
    title: str = "Heuristics Comparison"
) -> str:
    """
    绘制多机FlowShop多种启发式算法对比图

    参数:
        results: 字典，键为方法名，值为(makespan, runtime)元组
        filename: 保存文件名
        title: 图表标题

    返回:
        保存路径
    """
    start_time = None
    try:
        import time
        start_time = time.time()
        logger.info(f"[plot_heuristics_comparison] Entry, methods: {list(results.keys())}")

        methods = list(results.keys())
        makespans = [results[m][0][0] if isinstance(results[m][0], list) else results[m][0] for m in methods]
        runtimes = [results[m][1] for m in methods]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        colors = plt.cm.Set2(range(len(methods)))
        bars1 = ax1.bar(methods, makespans, color=colors, edgecolor='black')
        ax1.set_xlabel("Method", fontsize=10)
        ax1.set_ylabel("Makespan", fontsize=10)
        ax1.set_title("Makespan by Method", fontsize=11, fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)

        for bar, mk in zip(bars1, makespans):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{mk:.0f}', ha='center', va='bottom', fontsize=9)

        bars2 = ax2.bar(methods, runtimes, color=colors, edgecolor='black')
        ax2.set_xlabel("Method", fontsize=10)
        ax2.set_ylabel("Runtime (ms)", fontsize=10)
        ax2.set_title("Runtime by Method", fontsize=11, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)

        for bar, rt in zip(bars2, runtimes):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{rt:.1f}', ha='center', va='bottom', fontsize=9)

        fig.suptitle(title, fontsize=12, fontweight='bold')
        plt.tight_layout()

        save_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "flowshop",
            "figures",
            filename
        )
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

        elapsed = time.time() - start_time
        logger.info(f"[plot_heuristics_comparison] Done, saved: {save_path}, elapsed: {elapsed*1000:.2f}ms")

        plt.close()
        return save_path

    except Exception as e:
        logger.error(f"[plot_heuristics_comparison] Failed: {str(e)}")
        raise


def plot_dynamic_comparison(
    results: Dict[str, Tuple[float, float]],
    filename: str = "dynamic_comparison.png",
    title: str = "Dispatch Rules Comparison"
) -> str:
    """
    绘制动态FlowShop调度规则对比图

    参数:
        results: 字典，键为规则名，值为(makespan, avg_tardiness)元组
        filename: 保存文件名
        title: 图表标题

    返回:
        保存路径
    """
    start_time = None
    try:
        import time
        start_time = time.time()
        logger.info(f"[plot_dynamic_comparison] Entry, rules: {list(results.keys())}")

        rules = list(results.keys())
        makespans = [results[r][0] for r in rules]
        tardiness = [results[r][1] for r in rules]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        colors = plt.cm.Paired(range(len(rules)))
        bars1 = ax1.bar(rules, makespans, color=colors, edgecolor='black')
        ax1.set_xlabel("Dispatch Rule", fontsize=10)
        ax1.set_ylabel("Makespan", fontsize=10)
        ax1.set_title("Makespan by Rule", fontsize=11, fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)

        for bar, mk in zip(bars1, makespans):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{mk:.1f}', ha='center', va='bottom', fontsize=9)

        bars2 = ax2.bar(rules, tardiness, color=colors, edgecolor='black')
        ax2.set_xlabel("Dispatch Rule", fontsize=10)
        ax2.set_ylabel("Avg Tardiness", fontsize=10)
        ax2.set_title("Tardiness by Rule", fontsize=11, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)

        for bar, td in zip(bars2, tardiness):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{td:.1f}', ha='center', va='bottom', fontsize=9)

        fig.suptitle(title, fontsize=12, fontweight='bold')
        plt.tight_layout()

        save_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "flowshop",
            "figures",
            filename
        )
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

        elapsed = time.time() - start_time
        logger.info(f"[plot_dynamic_comparison] Done, saved: {save_path}, elapsed: {elapsed*1000:.2f}ms")

        plt.close()
        return save_path

    except Exception as e:
        logger.error(f"[plot_dynamic_comparison] Failed: {str(e)}")
        raise