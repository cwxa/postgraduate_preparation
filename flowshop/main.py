import sys
import os
import random
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flowshop.algorithms import FlowShop2Machine, solve_johnson, evaluate_schedule
from flowshop.visualization import (
    plot_gantt,
    plot_comparison,
    plot_gantt_multi,
    plot_gantt_dynamic,
    plot_heuristics_comparison,
    plot_dynamic_comparison
)
from flowshop.experiments import (
    run_multiple_experiments,
    print_experiment_summary,
    run_multi_machine_experiment,
    run_multi_machine_batch,
    print_multi_machine_summary,
    run_dynamic_experiment,
    run_dynamic_batch,
    print_dynamic_summary
)
from flowshop.utils import generate_random_instance, set_random_seed
from flowshop.constants import OUTPUT_DIR, RANDOM_SEED, DEFAULT_TRIALS, DEFAULT_N_JOBS
from flowshop.heuristics import FlowShopMultiMachine, neh_heuristic
from flowshop.dynamic_scheduler import DynamicFlowShop, generate_dynamic_instance
from flowshop.logging_config import get_logger

logger = get_logger(__name__)

__all__ = [
    "FlowShop2Machine",
    "FlowShopMultiMachine",
    "DynamicFlowShop",
    "solve_johnson",
    "evaluate_schedule",
    "plot_gantt",
    "plot_gantt_multi",
    "plot_gantt_dynamic",
    "plot_comparison",
    "plot_heuristics_comparison",
    "plot_dynamic_comparison",
    "run_multiple_experiments",
    "run_multi_machine_experiment",
    "run_dynamic_experiment",
    "print_experiment_summary",
    "print_multi_machine_summary",
    "print_dynamic_summary",
    "generate_random_instance",
    "generate_dynamic_instance",
    "set_random_seed",
    "OUTPUT_DIR",
    "RANDOM_SEED",
    "DEFAULT_TRIALS",
    "DEFAULT_N_JOBS",
]


def single_run_demo() -> None:
    """
    执行单次演示实验

    流程:
    1. 设置随机种子
    2. 生成8个作业的随机实例
    3. 计算Johnson最优序列和随机序列的调度
    4. 打印对比结果
    5. 绘制并保存甘特图
    """
    start_time = time.time()
    logger.info("=" * 50)
    logger.info("[single_run_demo] ========== Single Demo Started ==========")
    logger.info("=" * 50)

    logger.info(f"[single_run_demo] Step 1: Set random seed = {RANDOM_SEED}")
    set_random_seed(RANDOM_SEED)

    logger.info(f"[single_run_demo] Step 2: Generate random instance, n_jobs = 8")
    jobs = generate_random_instance(8)
    logger.info(f"[single_run_demo] Generated instance: {jobs}")

    model = FlowShop2Machine(jobs)

    logger.info("[single_run_demo] Step 3a: Compute Johnson optimal sequence")
    johnson_seq = model.johnson()

    logger.info("[single_run_demo] Step 3b: Generate random sequence")
    rand_seq = list(range(len(jobs)))
    random.shuffle(rand_seq)

    logger.info("[single_run_demo] Step 4: Compute both schedules")
    schedule_j, makespan_j, idle_j = model.calculate_schedule(johnson_seq)
    schedule_r, makespan_r, idle_r = model.calculate_schedule(rand_seq)

    print("\n" + "=" * 40)
    print("           Single Run Demo Results")
    print("=" * 40)
    print(f"\n[Jobs] ({len(jobs)} jobs)")
    print(jobs)

    print(f"\n[Johnson Algorithm]")
    print(f"  Sequence: {johnson_seq}")
    print(f"  Makespan: {makespan_j}")
    print(f"  M2 Idle: {idle_j}")

    print(f"\n[Random Sequence]")
    print(f"  Sequence: {rand_seq}")
    print(f"  Makespan: {makespan_r}")
    print(f"  M2 Idle: {idle_r}")

    improvement = ((makespan_r - makespan_j) / makespan_r) * 100 if makespan_r > 0 else 0
    print(f"\n[Comparison] Johnson improvement: {improvement:.2f}%")
    print("=" * 40 + "\n")

    logger.info(f"[single_run_demo] Step 5a: Plot Johnson Gantt")
    plot_gantt(schedule_j, "Johnson Schedule Gantt Chart", "johnson_gantt.png")

    logger.info(f"[single_run_demo] Step 5b: Plot Random Gantt")
    plot_gantt(schedule_r, "Random Schedule Gantt Chart", "random_gantt.png")

    elapsed = time.time() - start_time
    logger.info(f"[single_run_demo] ========== Single Demo Done, elapsed: {elapsed:.2f}s ==========")


def multi_machine_demo() -> None:
    """
    执行多机FlowShop演示

    流程:
    1. 生成随机4机实例
    2. 测试多种启发式算法
    3. 绘制对比图
    """
    start_time = time.time()
    logger.info("=" * 50)
    logger.info("[multi_machine_demo] ========== Multi-Machine Demo Started ==========")
    logger.info("=" * 50)

    n_jobs = 10
    n_machines = 4

    logger.info(f"[multi_machine_demo] Step 1: Generate random instance, n_jobs={n_jobs}, n_machines={n_machines}")
    jobs = generate_random_instance(n_jobs, low=5, high=20)
    jobs_multi = []
    for job in jobs:
        ext_job = list(job)
        while len(ext_job) < n_machines:
            ext_job.append(random.randint(5, 20))
        jobs_multi.append(tuple(ext_job))
    logger.info(f"[multi_machine_demo] Generated {len(jobs_multi)} jobs with {n_machines} machines")

    logger.info("[multi_machine_demo] Step 2: Test multiple heuristics")
    results = run_multi_machine_experiment(n_jobs=n_jobs, n_machines=n_machines)

    print("\n" + "=" * 50)
    print("       Multi-Machine Flow Shop Results")
    print("=" * 50)
    print(f"\n[Jobs] {n_jobs} jobs, {n_machines} machines")
    print(f"[Instance] {jobs_multi[:3]}... (showing first 3)")

    print(f"\n[Heuristics Comparison]")
    for method, (makespans, runtime) in results.items():
        print(f"  {method.upper()}: Makespan={makespans[0]}, Runtime={runtime:.2f}ms")

    best = min(results.items(), key=lambda x: x[1][0][0])
    print(f"\n[Best] {best[0].upper()} with makespan {best[1][0][0]}")
    print("=" * 50 + "\n")

    logger.info("[multi_machine_demo] Step 3: Plot comparison")
    plot_heuristics_comparison(results, "multi_machine_heuristics.png", "Multi-Machine Heuristics Comparison")

    scheduler = FlowShopMultiMachine(jobs_multi)
    best_seq = min(results.items(), key=lambda x: x[1][0][0])[0]
    if best_seq == 'neh':
        seq, _ = neh_heuristic(jobs_multi)
    else:
        seq = list(range(n_jobs))
        random.shuffle(seq)

    schedule_list, makespan = scheduler.calculate_schedule(seq)
    job_ids = list(range(n_jobs))
    plot_gantt_multi(schedule_list, f"Multi-Machine Schedule (Best: {best_seq.upper()})", "multi_machine_gantt.png",
                     num_machines=n_machines, job_ids=job_ids)

    elapsed = time.time() - start_time
    logger.info(f"[multi_machine_demo] ========== Multi-Machine Demo Done, elapsed: {elapsed:.2f}s ==========")


def dynamic_demo() -> None:
    """
    执行动态FlowShop演示

    流程:
    1. 生成带有到达时间的动态实例
    2. 测试调度规则
    3. 绘制对比图
    """
    start_time = time.time()
    logger.info("=" * 50)
    logger.info("[dynamic_demo] ========== Dynamic Flow Shop Demo Started ==========")
    logger.info("=" * 50)

    n_jobs = 20
    n_machines = 3
    arrival_rate = 0.3

    logger.info(f"[dynamic_demo] Step 1: Generate dynamic instance, n_jobs={n_jobs}, n_machines={n_machines}")
    jobs = generate_dynamic_instance(
        n_jobs=n_jobs,
        n_machines=n_machines,
        arrival_rate=arrival_rate,
        priority_range=(1, 5),
        due_date_factor=1.5,
        low=2,
        high=15
    )
    logger.info(f"[dynamic_demo] Generated {len(jobs)} jobs with varying arrival times")

    logger.info("[dynamic_demo] Step 2: Compare dispatch rules")
    results = run_dynamic_experiment(n_jobs=n_jobs, n_machines=n_machines, arrival_rate=arrival_rate)

    print("\n" + "=" * 50)
    print("       Dynamic Flow Shop Results")
    print("=" * 50)
    print(f"\n[Jobs] {n_jobs} jobs, {n_machines} machines, arrival_rate={arrival_rate}")

    print(f"\n[Dispatch Rules Comparison]")
    for rule, (makespan, tardiness) in results.items():
        print(f"  {rule}: Makespan={makespan:.2f}, Avg Tardiness={tardiness:.2f}")

    best = min(results.items(), key=lambda x: x[1][0])
    print(f"\n[Best Rule] {best[0]} with makespan {best[1][0]:.2f}")
    print("=" * 50 + "\n")

    logger.info("[dynamic_demo] Step 3: Plot comparison")
    plot_dynamic_comparison(results, "dynamic_dispatch_comparison.png", "Dynamic Dispatch Rules Comparison")

    logger.info("[dynamic_demo] Step 4: Plot Gantt for FIFO rule")
    shop = DynamicFlowShop(n_machines, jobs)
    events, makespan, avg_tard = shop.simulate(dispatch_rule="FIFO")
    event_tuples = [(e.job_id, e.machine, e.start_time, e.end_time, e.processing_time) for e in events]
    plot_gantt_dynamic(event_tuples, "Dynamic Flow Shop - FIFO Rule", "dynamic_fifo_gantt.png", n_machines)

    elapsed = time.time() - start_time
    logger.info(f"[dynamic_demo] ========== Dynamic Demo Done, elapsed: {elapsed:.2f}s ==========")


def main() -> None:
    """
    主函数，执行完整实验流程

    流程:
    1. 执行2机FlowShop演示
    2. 执行多机FlowShop演示
    3. 执行动态FlowShop演示
    4. 运行批量实验
    5. 打印最终摘要
    """
    total_start = time.time()
    logger.info("")
    logger.info("=" * 70)
    logger.info("           FlowShop Project - Extended Research Directions")
    logger.info("=" * 70)
    logger.info("")

    logger.info("[main] Part 1: 2-Machine Flow Shop (Johnson Algorithm)")
    logger.info("-" * 50)
    single_run_demo()

    logger.info("")
    logger.info("[main] Part 2: Multi-Machine Flow Shop (m-machine Heuristics)")
    logger.info("-" * 50)
    multi_machine_demo()

    logger.info("")
    logger.info("[main] Part 3: Dynamic Flow Shop (Uncertain Environment)")
    logger.info("-" * 50)
    dynamic_demo()

    logger.info("")
    logger.info("[main] Part 4: Multi-Machine Batch Experiments")
    logger.info("-" * 50)
    mm_summary = run_multi_machine_batch(trials=20, n_jobs=15, n_machines=4)
    print_multi_machine_summary(mm_summary)

    logger.info("")
    logger.info("[main] Part 5: Dynamic Flow Shop Batch Experiments")
    logger.info("-" * 50)
    dyn_summary = run_dynamic_batch(trials=10, n_jobs=20, n_machines=3)
    print_dynamic_summary(dyn_summary)

    logger.info("")
    logger.info("[main] Part 6: Output File List")
    logger.info("-" * 50)
    print("\n================ GENERATED FILES =================")
    print(f"- {OUTPUT_DIR}/johnson_gantt.png")
    print(f"- {OUTPUT_DIR}/random_gantt.png")
    print(f"- {OUTPUT_DIR}/johnson_vs_random.png")
    print(f"- {OUTPUT_DIR}/multi_machine_heuristics.png")
    print(f"- {OUTPUT_DIR}/multi_machine_gantt.png")
    print(f"- {OUTPUT_DIR}/dynamic_dispatch_comparison.png")
    print(f"- {OUTPUT_DIR}/dynamic_fifo_gantt.png")
    print("================================================\n")

    total_elapsed = time.time() - total_start
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"      All Experiments Done! Total time: {total_elapsed:.2f}s")
    logger.info("=" * 70)
    logger.info("")


if __name__ == "__main__":
    main()
