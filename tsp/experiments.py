"""
实验运行模块

包含实验执行的核心逻辑，包括：
- 统一的求解器包装
- 不同规模实例的运行函数
- 完整的演示流程
"""

import time
from typing import Callable

from algorithms import (
    brute_force_tsp,
    held_karp_tsp,
    nearest_neighbor_tsp,
    simulated_annealing_tsp,
    two_opt_tsp,
)
from constants import EPSILON
from reporting import print_city_summary, print_instance_report, print_metric_guide
from tsp_types import AlgorithmResult, ExperimentBundle, InstanceSpec
from utils import build_distance_matrix, build_result_map, generate_cities, validate_results
from visualization import generate_visual_demo


def run_solver(
    name: str,
    solver: Callable,
    dist: list[list[float]],
    *args,
    **kwargs,
) -> AlgorithmResult:
    """
    统一记录求解耗时，并兼容是否返回 history
    
    Args:
        name: 算法名称
        solver: 求解函数
        dist: 距离矩阵
        *args: 传递给求解器的位置参数
        **kwargs: 传递给求解器的关键字参数
    
    Returns:
        算法结果对象，包含路径、代价、时间和历史记录
    """
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


def run_small_instance(spec: InstanceSpec) -> ExperimentBundle:
    """
    运行小规模实例，包含精确解和启发式解
    
    小规模实例（如9个城市）可以运行暴力枚举和Held-Karp等精确算法，
    用于验证启发式算法的性能。
    
    Args:
        spec: 实例配置
    
    Returns:
        实验结果集合
    """
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
    """
    运行中规模实例，保留Held-Karp最优解做对照
    
    中规模实例（如12个城市）可以运行Held-Karp算法，
    但暴力枚举已经太慢。
    
    Args:
        spec: 实例配置
    
    Returns:
        实验结果集合
    """
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
    """
    运行大规模实例，只保留启发式算法
    
    大规模实例（如18个城市）无法在合理时间内运行精确算法，
    只能使用启发式算法。基准解使用所有启发式算法中的最佳结果。
    
    Args:
        spec: 实例配置
    
    Returns:
        实验结果集合
    """
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
    """
    运行整套实验、打印总结，并生成可视化图片
    
    执行流程：
    1. 定义三个不同规模的实例配置
    2. 分别运行三个实例
    3. 打印指标说明和实验结果
    4. 打印城市坐标
    5. 生成所有可视化图片
    """
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
