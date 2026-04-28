import time
import random
from typing import List, Tuple, Optional, Dict, Any
from flowshop.flowshop_types import Job, Sequence
from flowshop.algorithms import FlowShop2Machine
from flowshop.utils import generate_random_instance
from flowshop.constants import DEFAULT_TRIALS, DEFAULT_N_JOBS
from flowshop.heuristics import (
    solve_multi_heuristic,
    FlowShopMultiMachine,
    simulated_annealing_mfs,
    genetic_algorithm_mfs,
    tabu_search_mfs,
    neh_heuristic
)
from flowshop.dynamic_scheduler import (
    DynamicFlowShop,
    generate_dynamic_instance,
    compare_dispatch_rules
)
from flowshop.logging_config import get_logger

logger = get_logger(__name__)


def run_single_experiment(jobs: List[Job], seed: Optional[int] = None) -> Tuple[int, int, int, int]:
    """
    运行单次实验，比较Johnson算法和随机序列

    参数:
        jobs: 作业列表
        seed: 随机种子（用于可重复的随机序列）

    返回:
        tuple: (johnson_makespan, random_makespan, johnson_idle, random_idle)
    """
    start_time = time.time()
    n = len(jobs)
    logger.debug(f"[run_single_experiment] Entry, n_jobs: {n}")

    model = FlowShop2Machine(jobs)

    seq_j = model.johnson()
    _, mk_j, idle_j = model.calculate_schedule(seq_j)

    seq_r = list(range(n))
    if seed is not None:
        random.seed(seed)
    random.shuffle(seq_r)
    _, mk_r, idle_r = model.calculate_schedule(seq_r)

    elapsed = time.time() - start_time
    logger.debug(f"[run_single_experiment] Done, Johnson: {mk_j}, Random: {mk_r}, elapsed: {elapsed*1000:.2f}ms")

    return mk_j, mk_r, idle_j, idle_r


def run_multiple_experiments(
    trials: int = DEFAULT_TRIALS,
    n: int = DEFAULT_N_JOBS,
    show_progress: bool = True
) -> Tuple[List[int], List[int]]:
    """
    运行多次对比实验

    参数:
        trials: 实验次数
        n: 每次实验的作业数量
        show_progress: 是否显示进度

    返回:
        tuple: (johnson_results, random_results)
    """
    start_time = time.time()
    logger.info(f"[run_multiple_experiments] Entry, trials: {trials}, n_jobs: {n}")

    if trials <= 0:
        raise ValueError(f"trials must be > 0, got: {trials}")
    if n <= 0:
        raise ValueError(f"n must be > 0, got: {n}")

    johnson_results: List[int] = []
    random_results: List[int] = []

    for i in range(trials):
        trial_start = time.time()

        jobs = generate_random_instance(n)
        mk_j, mk_r, _, _ = run_single_experiment(jobs, seed=i)

        johnson_results.append(mk_j)
        random_results.append(mk_r)

        trial_elapsed = time.time() - trial_start

        if show_progress and (i + 1) % 20 == 0:
            logger.info(f"[PROGRESS] Completed {i+1}/{trials} trials, "
                        f"current Johnson avg: {sum(johnson_results)/len(johnson_results):.2f}, "
                        f"trial time: {trial_elapsed*1000:.1f}ms")

    total_elapsed = time.time() - start_time
    avg_j = sum(johnson_results) / len(johnson_results)
    avg_r = sum(random_results) / len(random_results)

    logger.info(f"[run_multiple_experiments] Done, total time: {total_elapsed:.2f}s, "
                f"Johnson avg: {avg_j:.2f}, Random avg: {avg_r:.2f}")

    return johnson_results, random_results


def print_experiment_summary(
    johnson_results: List[int],
    random_results: List[int],
    indent: str = ""
) -> None:
    """
    打印实验摘要

    参数:
        johnson_results: Johnson算法的makespan列表
        random_results: 随机序列的makespan列表
        indent: 缩进字符串
    """
    start_time = time.time()
    logger.info(f"[print_experiment_summary] Entry, n_results: {len(johnson_results)}")

    if len(johnson_results) != len(random_results):
        raise ValueError("Result lists must have same length")

    n = len(johnson_results)
    avg_j = sum(johnson_results) / n
    avg_r = sum(random_results) / n

    min_j = min(johnson_results)
    max_j = max(johnson_results)
    min_r = min(random_results)
    max_r = max(random_results)

    improvement = ((avg_r - avg_j) / avg_r) * 100 if avg_r > 0 else 0

    print(f"\n{indent}================ RESULT ================")
    print(f"{indent}Trials: {n}")
    print(f"{indent}")
    print(f"{indent}Johnson Algorithm:")
    print(f"{indent}  Avg Makespan: {avg_j:.2f}")
    print(f"{indent}  Min Makespan: {min_j}")
    print(f"{indent}  Max Makespan: {max_j}")
    print(f"{indent}")
    print(f"{indent}Random Sequence:")
    print(f"{indent}  Avg Makespan: {avg_r:.2f}")
    print(f"{indent}  Min Makespan: {min_r}")
    print(f"{indent}  Max Makespan: {max_r}")
    print(f"{indent}")
    print(f"{indent}Johnson improvement: {improvement:.2f}%")
    print(f"{indent}========================================\n")

    elapsed = time.time() - start_time
    logger.info(f"[print_experiment_summary] Done, elapsed: {elapsed*1000:.2f}ms")


def run_multi_machine_experiment(
    n_jobs: int = 10,
    n_machines: int = 4,
    methods: Optional[List[str]] = None
) -> Dict[str, Tuple[List[int], float]]:
    """
    运行多机器FlowShop实验

    参数:
        n_jobs: 作业数量
        n_machines: 机器数量
        methods: 要测试的方法列表

    返回:
        Dict: 方法名到(makespan_list, runtime)的映射
    """
    start_time = time.time()
    logger.info(f"[run_multi_machine_experiment] Entry, n_jobs: {n_jobs}, n_machines: {n_machines}")

    if methods is None:
        methods = ['neh', 'sa', 'ga', 'ts', 'neh+2opt']

    jobs = generate_random_instance(n_jobs, low=5, high=20)
    jobs_multi = [tuple(job) + (0,) * (n_machines - 2) if len(job) < n_machines else job for job in jobs]
    if n_machines > 2:
        jobs_multi = []
        for job in jobs:
            ext_job = list(job)
            while len(ext_job) < n_machines:
                ext_job.append(random.randint(5, 20))
            jobs_multi.append(tuple(ext_job))

    results: Dict[str, Tuple[List[int], float]] = {}

    for method in methods:
        method_start = time.time()
        logger.info(f"[run_multi_machine_experiment] Testing method: {method}")

        if method == 'neh':
            seq, mk = neh_heuristic(jobs_multi)
            results[method] = ([mk], (time.time() - method_start) * 1000)
        elif method == 'neh+2opt':
            from flowshop.heuristics import two_opt_improve
            seq, mk = neh_heuristic(jobs_multi)
            seq, mk = two_opt_improve(seq, jobs_multi)
            results[method] = ([mk], (time.time() - method_start) * 1000)
        elif method == 'sa':
            seq, mk = simulated_annealing_mfs(jobs_multi)
            results[method] = ([mk], (time.time() - method_start) * 1000)
        elif method == 'ga':
            seq, mk = genetic_algorithm_mfs(jobs_multi)
            results[method] = ([mk], (time.time() - method_start) * 1000)
        elif method == 'ts':
            seq, mk = tabu_search_mfs(jobs_multi)
            results[method] = ([mk], (time.time() - method_start) * 1000)
        else:
            logger.warning(f"[run_multi_machine_experiment] Unknown method: {method}")

    total_elapsed = time.time() - start_time
    logger.info(f"[run_multi_machine_experiment] Done, total time: {total_elapsed:.2f}s")

    return results


def run_multi_machine_batch(
    trials: int = 20,
    n_jobs: int = 15,
    n_machines: int = 4,
    methods: Optional[List[str]] = None
) -> Dict[str, Dict[str, float]]:
    """
    运行多机器FlowShop批量实验

    参数:
        trials: 实验次数
        n_jobs: 每次实验的作业数量
        n_machines: 机器数量
        methods: 要测试的方法列表

    返回:
        聚合统计结果字典
    """
    start_time = time.time()
    logger.info(f"[run_multi_machine_batch] Entry, trials: {trials}, n_jobs: {n_jobs}, n_machines: {n_machines}")

    if methods is None:
        methods = ['neh', 'sa', 'ga', 'ts']

    all_results: Dict[str, List[int]] = {m: [] for m in methods}

    for trial in range(trials):
        jobs = generate_random_instance(n_jobs, low=5, high=20)
        jobs_multi = []
        for job in jobs:
            ext_job = list(job)
            while len(ext_job) < n_machines:
                ext_job.append(random.randint(5, 20))
            jobs_multi.append(tuple(ext_job))

        for method in methods:
            if method == 'neh':
                _, mk = neh_heuristic(jobs_multi)
                all_results[method].append(mk)
            elif method == 'sa':
                _, mk = simulated_annealing_mfs(jobs_multi)
                all_results[method].append(mk)
            elif method == 'ga':
                _, mk = genetic_algorithm_mfs(jobs_multi)
                all_results[method].append(mk)
            elif method == 'ts':
                _, mk = tabu_search_mfs(jobs_multi)
                all_results[method].append(mk)

        if (trial + 1) % 10 == 0:
            logger.info(f"[PROGRESS] Completed {trial+1}/{trials} trials")

    summary: Dict[str, Dict[str, float]] = {}
    for method, makespans in all_results.items():
        summary[method] = {
            'avg': sum(makespans) / len(makespans),
            'min': min(makespans),
            'max': max(makespans),
            'count': len(makespans)
        }

    total_elapsed = time.time() - start_time
    logger.info(f"[run_multi_machine_batch] Done, total time: {total_elapsed:.2f}s")

    return summary


def print_multi_machine_summary(summary: Dict[str, Dict[str, float]]) -> None:
    """
    打印多机器实验摘要

    参数:
        summary: 摘要统计字典
    """
    logger.info("[print_multi_machine_summary] Entry")

    print("\n========== Multi-Machine Flow Shop Results ==========")
    print(f"Methods tested: {list(summary.keys())}")
    print("")

    for method, stats in summary.items():
        print(f"{method.upper()} Method:")
        print(f"  Avg Makespan: {stats['avg']:.2f}")
        print(f"  Min Makespan: {stats['min']}")
        print(f"  Max Makespan: {stats['max']}")
        print("")

    best_method = min(summary.items(), key=lambda x: x[1]['avg'])
    print(f"Best Method: {best_method[0].upper()} with avg makespan {best_method[1]['avg']:.2f}")
    print("=" * 51)

    logger.info("[print_multi_machine_summary] Done")


def run_dynamic_experiment(
    n_jobs: int = 20,
    n_machines: int = 3,
    arrival_rate: float = 0.3,
    rules: Optional[List[str]] = None
) -> Dict[str, Tuple[float, float]]:
    """
    运行动态FlowShop实验

    参数:
        n_jobs: 作业数量
        n_machines: 机器数量
        arrival_rate: 作业到达率
        rules: 要比较的调度规则

    返回:
        Dict: 规则名到(makespan, avg_tardiness)的映射
    """
    start_time = time.time()
    logger.info(f"[run_dynamic_experiment] Entry, n_jobs: {n_jobs}, n_machines: {n_machines}, rate: {arrival_rate}")

    if rules is None:
        rules = ["FIFO", "SPT", "EDD", "PRIORITY"]

    jobs = generate_dynamic_instance(
        n_jobs=n_jobs,
        n_machines=n_machines,
        arrival_rate=arrival_rate,
        priority_range=(1, 5),
        due_date_factor=1.5,
        low=2,
        high=15
    )

    results = compare_dispatch_rules(jobs, n_machines, rules)

    total_elapsed = time.time() - start_time
    logger.info(f"[run_dynamic_experiment] Done, total time: {total_elapsed:.2f}s")

    return results


def run_dynamic_batch(
    trials: int = 10,
    n_jobs: int = 20,
    n_machines: int = 3,
    arrival_rate: float = 0.3,
    rules: Optional[List[str]] = None
) -> Dict[str, Dict[str, float]]:
    """
    运行动态FlowShop批量实验

    参数:
        trials: 实验次数
        n_jobs: 每次实验的作业数量
        n_machines: 机器数量
        arrival_rate: 作业到达率
        rules: 要比较的调度规则

    返回:
        聚合统计结果
    """
    start_time = time.time()
    logger.info(f"[run_dynamic_batch] Entry, trials: {trials}, n_jobs: {n_jobs}, n_machines: {n_machines}")

    if rules is None:
        rules = ["FIFO", "SPT", "EDD", "PRIORITY"]

    all_results: Dict[str, List[float]] = {r: [] for r in rules}

    for trial in range(trials):
        jobs = generate_dynamic_instance(
            n_jobs=n_jobs,
            n_machines=n_machines,
            arrival_rate=arrival_rate,
            priority_range=(1, 5),
            due_date_factor=1.5,
            low=2,
            high=15
        )

        results = compare_dispatch_rules(jobs, n_machines, rules)

        for rule in rules:
            all_results[rule].append(results[rule][0])

        if (trial + 1) % 5 == 0:
            logger.info(f"[PROGRESS] Completed {trial+1}/{trials} trials")

    summary: Dict[str, Dict[str, float]] = {}
    for rule, makespans in all_results.items():
        summary[rule] = {
            'avg': sum(makespans) / len(makespans),
            'min': min(makespans),
            'max': max(makespans),
            'count': len(makespans)
        }

    total_elapsed = time.time() - start_time
    logger.info(f"[run_dynamic_batch] Done, total time: {total_elapsed:.2f}s")

    return summary


def print_dynamic_summary(results: Dict[str, Dict[str, float]]) -> None:
    """
    打印动态FlowShop实验摘要

    参数:
        results: 结果字典，映射规则到包含avg/min/max/count的字典
    """
    logger.info("[print_dynamic_summary] Entry")

    print("\n========== Dynamic Flow Shop Results ==========")
    print(f"Dispatch Rules tested: {list(results.keys())}")
    print("")

    for rule, stats in results.items():
        print(f"{rule} Rule:")
        print(f"  Avg Makespan: {stats['avg']:.2f}")
        print(f"  Min Makespan: {stats['min']:.2f}")
        print(f"  Max Makespan: {stats['max']:.2f}")
        print("")

    best_rule = min(results.items(), key=lambda x: x[1]['avg'])
    print(f"Best Rule (by avg makespan): {best_rule[0]} with avg makespan {best_rule[1]['avg']:.2f}")
    print("=" * 48)

    logger.info("[print_dynamic_summary] Done")
