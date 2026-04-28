"""
工具函数模块

包含TSP问题中常用的辅助函数，包括：
- 距离计算
- 距离矩阵构建
- 路径代价计算
- 城市生成
- 结果验证
"""

import math
import random
from typing import Iterable

from tsp_types import AlgorithmResult


def euclidean_distance(city_a: tuple[int, int], city_b: tuple[int, int]) -> float:
    """
    计算两个城市之间的欧氏距离
    
    Args:
        city_a: 第一个城市的坐标 (x, y)
        city_b: 第二个城市的坐标 (x, y)
    
    Returns:
        两点之间的欧氏距离
    """
    return math.hypot(city_a[0] - city_b[0], city_a[1] - city_b[1])


def build_distance_matrix(cities: list[tuple[int, int]]) -> list[list[float]]:
    """
    根据城市坐标构建对称距离矩阵
    
    Args:
        cities: 城市坐标列表
    
    Returns:
        n x n 的对称距离矩阵，dist[i][j] 表示城市i到城市j的距离
    """
    n = len(cities)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            distance = euclidean_distance(cities[i], cities[j])
            dist[i][j] = distance
            dist[j][i] = distance
    return dist


def tour_cost(dist: list[list[float]], tour: list[int]) -> float:
    """
    计算一条完整回路的总代价
    
    Args:
        dist: 距离矩阵
        tour: 路径序列，包含城市索引，起点和终点都是0
    
    Returns:
        路径总长度
    """
    return sum(dist[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))


def format_time_ms(value: float) -> str:
    """
    根据数值量级格式化时间显示（毫秒）
    
    Args:
        value: 时间值（毫秒）
    
    Returns:
        格式化后的时间字符串
    """
    if value < 1:
        return f"{value:.3f}"
    if value < 100:
        return f"{value:.2f}"
    return f"{value:.1f}"


def is_valid_tour(tour: list[int], city_count: int) -> bool:
    """
    检查回路是否合法
    
    合法回路的条件：
    1. 长度为 city_count + 1（包含返回起点）
    2. 起点和终点都是0
    3. 所有城市恰好访问一次
    
    Args:
        tour: 路径序列
        city_count: 城市总数
    
    Returns:
        True 如果路径合法，否则 False
    """
    return (
        len(tour) == city_count + 1
        and tour[0] == 0
        and tour[-1] == 0
        and set(tour[:-1]) == set(range(city_count))
    )


def validate_results(results: Iterable[AlgorithmResult], city_count: int) -> None:
    """
    集中校验所有算法结果的回路合法性
    
    Args:
        results: 算法结果列表
        city_count: 城市总数
    
    Raises:
        AssertionError: 如果发现非法路径
    """
    for result in results:
        assert is_valid_tour(result.tour, city_count), f"Invalid tour: {result.name}"


def generate_cities(count: int, seed: int = 42) -> list[tuple[int, int]]:
    """
    生成指定数量的随机城市坐标（固定种子保证可复现）
    
    Args:
        count: 城市数量
        seed: 随机种子
    
    Returns:
        城市坐标列表，每个城市坐标范围在 [0, 100] x [0, 100]
    """
    random.seed(seed)
    return [(random.randint(0, 100), random.randint(0, 100)) for _ in range(count)]


def build_result_map(results: list[AlgorithmResult]) -> dict[str, AlgorithmResult]:
    """
    将结果列表转换为按名称索引的字典，方便后续查询
    
    Args:
        results: 算法结果列表
    
    Returns:
        以算法名称为键的结果字典
    """
    return {result.name: result for result in results}
