"""
TSP算法实现模块

包含多种TSP求解算法：
- 暴力枚举算法 (Brute Force)
- 最近邻贪心算法 (Nearest Neighbor)
- Held-Karp 动态规划算法
- 2-opt 局部优化算法
- 模拟退火算法 (Simulated Annealing)
"""

import math
import random
from itertools import combinations, permutations

from constants import EPSILON, HISTORY_INTERVAL
from utils import tour_cost


def brute_force_tsp(dist: list[list[float]]) -> tuple[list[int], float]:
    """
    暴力枚举所有访问顺序，作为小规模实例的最优参考
    
    算法复杂度: O(n!)，仅适用于 n <= 10 的小规模问题
    
    Args:
        dist: 距离矩阵
    
    Returns:
        (最优路径, 最优代价)
    """
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
    """
    最近邻贪心算法：每次都走向最近的未访问城市
    
    算法复杂度: O(n^2)，快速但不一定得到最优解
    
    Args:
        dist: 距离矩阵
        start: 起始城市索引（默认为0）
    
    Returns:
        (路径, 代价)
    """
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
    """
    Held-Karp 动态规划算法：中小规模TSP的经典精确算法
    
    使用状态压缩动态规划，状态表示为 (mask, u)，其中mask是访问过的城市集合，
    u是当前所在城市。
    
    算法复杂度: O(n^2 * 2^n)，适用于 n <= 15 的问题
    
    Args:
        dist: 距离矩阵
    
    Returns:
        (最优路径, 最优代价)
    """
    n = len(dist)
    if n <= 1:
        return [0, 0], 0.0

    # dp[(mask, city)] = (最小代价, 前驱城市)
    dp: dict[tuple[int, int], tuple[float, int]] = {}
    for city in range(1, n):
        mask = 1 << city
        dp[(mask, city)] = (dist[0][city], 0)

    # 按子集大小递增处理
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

    # 计算回到起点的最小代价
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

    # 回溯构建路径
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
    """
    执行一次 2-opt 交换
    
    2-opt 操作通过反转路径中 i 到 k 的部分来改进路径。
    
    Args:
        tour: 当前路径
        i: 交换起点
        k: 交换终点
    
    Returns:
        交换后的新路径
    """
    return tour[:i] + list(reversed(tour[i : k + 1])) + tour[k + 1 :]


def two_opt_delta(dist: list[list[float]], tour: list[int], i: int, k: int) -> float:
    """
    增量计算 2-opt 交换的代价变化
    
    原路径: ... -> a -> b -> ... -> c -> d -> ...
    新路径: ... -> a -> c -> ... -> b -> d -> ...
    
    Args:
        dist: 距离矩阵
        tour: 当前路径
        i: 交换起点
        k: 交换终点
    
    Returns:
        代价变化量（负值表示改进）
    """
    a, b = tour[i - 1], tour[i]
    c, d = tour[k], tour[k + 1]
    old_edges = dist[a][b] + dist[c][d]
    new_edges = dist[a][c] + dist[b][d]
    return new_edges - old_edges


def two_opt_tsp(
    dist: list[list[float]], initial_tour: list[int]
) -> tuple[list[int], float]:
    """
    使用 best-improvement 版本的 2-opt 做局部优化
    
    算法会搜索所有可能的 2-opt 交换，选择能最大程度改进路径的交换，
    直到无法进一步改进为止。
    
    Args:
        dist: 距离矩阵
        initial_tour: 初始路径
    
    Returns:
        (优化后的路径, 代价)
    """
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
    """
    为模拟退火随机采样一个 2-opt 邻域动作
    
    Args:
        tour: 当前路径
        rng: 随机数生成器
    
    Returns:
        随机选择的交换位置 (i, k)
    """
    return tuple(sorted(rng.sample(range(1, len(tour) - 1), 2)))


def simulated_annealing_tsp(
    dist: list[list[float]],
    initial_tour: list[int] | None = None,
    initial_temp: float = 300.0,
    cooling_rate: float = 0.995,
    max_steps: int = 5000,
    seed: int = 42,
) -> tuple[list[int], float, list[tuple[int, float, float]]]:
    """
    模拟退火算法：用 2-opt 邻域在大规模搜索空间中跳出局部最优
    
    模拟退火是一种概率优化算法，通过模拟金属退火过程来搜索最优解。
    在高温时允许接受较差的解以探索搜索空间，随着温度降低，接受较差解的概率减小。
    
    Args:
        dist: 距离矩阵
        initial_tour: 初始路径（默认使用最近邻算法生成）
        initial_temp: 初始温度
        cooling_rate: 降温速率（每步乘以该系数）
        max_steps: 最大迭代步数
        seed: 随机种子
    
    Returns:
        (最优路径, 最优代价, 历史记录)
        历史记录格式: [(步数, 当前最优代价, 当前温度), ...]
    """
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

        # 温度较高时允许一定概率接受更差解，用来跳出局部最优
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
