import time
import random
from math import exp
from typing import List, Tuple, Callable, Optional, Dict, Any
from flowshop.flowshop_types import JobM, Sequence
from flowshop.logging_config import get_logger

logger = get_logger(__name__)


class FlowShopMultiMachine:

    def __init__(self, jobs: List[JobM], num_machines: Optional[int] = None):
        """
        初始化多机FlowShop调度器

        参数:
            jobs: 作业列表，每个作业是各机器加工时间的元组
            num_machines: 机器数量（若为None则从作业长度推断）
        """
        if not jobs:
            raise ValueError("jobs list cannot be empty")
        if not all(len(job) >= 2 for job in jobs):
            raise ValueError("each job must have at least 2 processing times")

        self.jobs = jobs
        self.n = len(jobs)
        self.num_machines = num_machines if num_machines else len(jobs[0])
        logger.info(f"FlowShopMultiMachine initialized, n_jobs: {self.n}, m_machines: {self.num_machines}")

    def calculate_makespan(self, sequence: Sequence, validate: bool = False) -> int:
        """
        计算给定序列在m台机器上的makespan

        参数:
            sequence: 作业索引序列
            validate: 是否验证序列长度是否匹配作业数量

        返回:
            Makespan（最大完工时间）
        """
        if validate and len(sequence) != self.n:
            raise ValueError(f"Sequence length mismatch: expected {self.n}, got {len(sequence)}")

        if not sequence:
            return 0

        machine_times = [0] * self.num_machines

        for job_id in sequence:
            job = self.jobs[job_id]
            machine_times[0] += job[0]
            for m in range(1, self.num_machines):
                machine_times[m] = max(machine_times[m], machine_times[m-1]) + job[m]

        return machine_times[-1]

    def calculate_schedule(self, sequence: Sequence) -> Tuple[List[Tuple], int]:
        """
        计算给定序列的详细调度方案

        参数:
            sequence: 作业索引序列

        返回:
            tuple: (schedule_list, makespan)
                schedule_list: [(job_id, machine_idx, start, duration), ...]
        """
        machine_times = [0] * self.num_machines
        schedule_list = []

        for job_id in sequence:
            job = self.jobs[job_id]
            machine_times[0] += job[0]
            schedule_list.append((job_id, 0, machine_times[0] - job[0], job[0]))

            for m in range(1, self.num_machines):
                machine_times[m] = max(machine_times[m], machine_times[m-1]) + job[m]
                schedule_list.append((job_id, m, machine_times[m] - job[m], job[m]))

        return schedule_list, machine_times[-1]


def neh_heuristic(jobs: List[JobM]) -> Tuple[Sequence, int]:
    """
    NEH启发式算法（Nawaz-Enscore-Ham）：求解多机FlowShop问题

    算法步骤:
    1. 按总加工时间降序排列作业
    2. 取第一个作业作为初始序列
    3. 对每个剩余作业，尝试插入到所有可能位置，选择makespan最小的位置

    参数:
        jobs: 作业列表，每个作业是加工时间元组

    返回:
        tuple: (best_sequence, makespan)
    """
    start_time = time.time()
    logger.info(f"[NEH] Starting, n_jobs: {len(jobs)}")

    n = len(jobs)
    if n == 0:
        return [], 0
    if n == 1:
        return [0], jobs[0][0]

    job_totals = [(i, sum(jobs[i])) for i in range(n)]
    job_totals.sort(key=lambda x: x[1], reverse=True)

    partial_seq = [job_totals[0][0]]

    for idx in range(1, n):
        job_id = job_totals[idx][0]
        best_pos = 0
        best_makespan = float('inf')

        for pos in range(len(partial_seq) + 1):
            test_seq = partial_seq[:pos] + [job_id] + partial_seq[pos:]
            scheduler = FlowShopMultiMachine(jobs)
            mk = scheduler.calculate_makespan(test_seq)
            if mk < best_makespan:
                best_makespan = mk
                best_pos = pos

        partial_seq = partial_seq[:best_pos] + [job_id] + partial_seq[best_pos:]

    scheduler = FlowShopMultiMachine(jobs)
    makespan = scheduler.calculate_makespan(partial_seq)
    elapsed = time.time() - start_time

    logger.info(f"[NEH] Done, makespan: {makespan}, elapsed: {elapsed*1000:.2f}ms")
    return partial_seq, makespan


def two_opt_improve(sequence: Sequence, jobs: List[JobM], max_iter: int = 100) -> Tuple[Sequence, int]:
    """
    2-opt局部搜索改进算法

    参数:
        sequence: 初始序列
        jobs: 作业列表
        max_iter: 最大迭代次数

    返回:
        tuple: (improved_sequence, makespan)
    """
    current_seq = sequence[:]
    scheduler = FlowShopMultiMachine(jobs)
    current_mk = scheduler.calculate_makespan(current_seq)

    improved = True
    iteration = 0

    while improved and iteration < max_iter:
        improved = False
        iteration += 1

        for i in range(len(current_seq) - 1):
            for j in range(i + 2, len(current_seq)):
                new_seq = current_seq[:i+1] + current_seq[i+1:j+1][::-1] + current_seq[j+1:]
                new_mk = scheduler.calculate_makespan(new_seq)

                if new_mk < current_mk:
                    current_seq = new_seq
                    current_mk = new_mk
                    improved = True
                    break
            if improved:
                break

    return current_seq, current_mk


def simulated_annealing_mfs(
    jobs: List[JobM],
    initial_temp: float = 1000.0,
    cooling_rate: float = 0.995,
    max_iter: int = 500,
    neighbor_fn: Optional[Callable] = None
) -> Tuple[Sequence, int]:
    """
    模拟退火算法（Simulated Annealing）：求解多机FlowShop问题

    参数:
        jobs: 作业列表
        initial_temp: 初始温度
        cooling_rate: 冷却速率（0 < rate < 1）
        max_iter: 每个温度下的最大迭代次数
        neighbor_fn: 邻域生成函数

    返回:
        tuple: (best_sequence, makespan)
    """
    start_time = time.time()
    logger.info(f"[SA_MFS] Starting, n_jobs: {len(jobs)}")

    n = len(jobs)
    scheduler = FlowShopMultiMachine(jobs)

    if neighbor_fn is None:
        def neighbor_fn(seq):
            new_seq = seq[:]
            i, j = random.sample(range(len(new_seq)), 2)
            new_seq[i], new_seq[j] = new_seq[j], new_seq[i]
            return new_seq

    current_seq = list(range(n))
    random.shuffle(current_seq)
    current_mk = scheduler.calculate_makespan(current_seq)

    best_seq = current_seq[:]
    best_mk = current_mk

    temp = initial_temp

    while temp > 0.1:
        for _ in range(max_iter):
            new_seq = neighbor_fn(current_seq)
            new_mk = scheduler.calculate_makespan(new_seq)

            delta = new_mk - current_mk

            if delta < 0 or random.random() < exp(-delta / temp):
                current_seq = new_seq
                current_mk = new_mk

                if current_mk < best_mk:
                    best_seq = current_seq[:]
                    best_mk = current_mk

        temp *= cooling_rate

    elapsed = time.time() - start_time
    logger.info(f"[SA_MFS] Done, makespan: {best_mk}, elapsed: {elapsed*1000:.2f}ms")
    return best_seq, best_mk


def genetic_algorithm_mfs(
    jobs: List[JobM],
    pop_size: int = 50,
    generations: int = 100,
    mutation_rate: float = 0.1,
    crossover_rate: float = 0.8,
    elite_ratio: float = 0.1
) -> Tuple[Sequence, int]:
    """
    遗传算法（Genetic Algorithm）：求解多机FlowShop问题

    参数:
        jobs: 作业列表
        pop_size: 种群大小
        generations: 进化代数
        mutation_rate: 变异概率
        crossover_rate: 交叉概率
        elite_ratio: 精英保留比例

    返回:
        tuple: (best_sequence, makespan)
    """
    start_time = time.time()
    logger.info(f"[GA_MFS] Starting, n_jobs: {len(jobs)}, pop: {pop_size}, gens: {generations}")

    n = len(jobs)
    scheduler = FlowShopMultiMachine(jobs)

    def fitness(seq):
        return scheduler.calculate_makespan(seq)

    def crossover(parent1, parent2):
        if random.random() > crossover_rate:
            return parent1[:], parent2[:]

        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))

        child1 = [None] * size
        child2 = [None] * size

        child1[start:end+1] = parent1[start:end+1]
        child2[start:end+1] = parent2[start:end+1]

        remaining1 = [x for x in parent2 if x not in child1]
        remaining2 = [x for x in parent1 if x not in child2]

        idx1 = idx2 = 0
        for i in range(size):
            if child1[i] is None and idx1 < len(remaining1):
                child1[i] = remaining1[idx1]
                idx1 += 1
            if child2[i] is None and idx2 < len(remaining2):
                child2[i] = remaining2[idx2]
                idx2 += 1

        return child1, child2

    def mutate(seq):
        if random.random() < mutation_rate:
            new_seq = seq[:]
            i, j = random.sample(range(len(new_seq)), 2)
            new_seq[i], new_seq[j] = new_seq[j], new_seq[i]
        return seq

    population = [list(range(n))]
    for _ in range(pop_size - 1):
        ind = list(range(n))
        random.shuffle(ind)
        population.append(ind)

    population = [(ind, fitness(ind)) for ind in population]
    population.sort(key=lambda x: x[1])

    elite_size = int(pop_size * elite_ratio)

    for gen in range(generations):
        new_population = [ind for ind, _ in population[:elite_size]]

        while len(new_population) < pop_size:
            parent1, parent2 = random.sample([ind for ind, _ in population], 2)
            child1, child2 = crossover(parent1, parent2)
            new_population.append(mutate(child1))
            if len(new_population) < pop_size:
                new_population.append(mutate(child2))

        population = [(ind, fitness(ind)) for ind in new_population]
        population.sort(key=lambda x: x[1])

        if (gen + 1) % 20 == 0:
            logger.debug(f"[GA_MFS] Gen {gen+1}, best makespan: {population[0][1]}")

    best_seq, best_mk = population[0]
    elapsed = time.time() - start_time
    logger.info(f"[GA_MFS] Done, makespan: {best_mk}, elapsed: {elapsed*1000:.2f}ms")

    return best_seq, best_mk


def tabu_search_mfs(
    jobs: List[JobM],
    tabu_tenure: int = 10,
    max_iter: int = 200,
    neighbor_size: int = 10
) -> Tuple[Sequence, int]:
    """
    禁忌搜索（Tabu Search）：求解多机FlowShop问题

    参数:
        jobs: 作业列表
        tabu_tenure: 禁忌列表长度
        max_iter: 最大迭代次数
        neighbor_size: 每次迭代评估的邻域数量

    返回:
        tuple: (best_sequence, makespan)
    """
    start_time = time.time()
    logger.info(f"[TS_MFS] Starting, n_jobs: {len(jobs)}, tenure: {tabu_tenure}")

    n = len(jobs)
    scheduler = FlowShopMultiMachine(jobs)

    current_seq = list(range(n))
    random.shuffle(current_seq)
    current_mk = scheduler.calculate_makespan(current_seq)

    best_seq = current_seq[:]
    best_mk = current_mk

    tabu_list: List[Tuple[int, int]] = []
    aspiration_criteria: Dict[int, int] = {}

    for _ in range(max_iter):
        neighbors = []
        for _ in range(neighbor_size):
            i, j = random.sample(range(n), 2)
            new_seq = current_seq[:]
            new_seq[i], new_seq[j] = new_seq[j], new_seq[i]
            move = (min(i, j), max(i, j))
            neighbors.append((new_seq, move))

        neighbors.sort(key=lambda x: scheduler.calculate_makespan(x[0]))

        for candidate_seq, move in neighbors:
            candidate_mk = scheduler.calculate_makespan(candidate_seq)

            is_tabu = move in tabu_list and candidate_mk > aspiration_criteria.get(candidate_mk, float('inf'))

            if not is_tabu or candidate_mk < best_mk:
                current_seq = candidate_seq
                current_mk = candidate_mk

                if current_mk < best_mk:
                    best_seq = current_seq[:]
                    best_mk = current_mk
                    aspiration_criteria[best_mk] = best_mk

                tabu_list.append(move)
                if len(tabu_list) > tabu_tenure:
                    tabu_list.pop(0)
                break

    elapsed = time.time() - start_time
    logger.info(f"[TS_MFS] Done, makespan: {best_mk}, elapsed: {elapsed*1000:.2f}ms")
    return best_seq, best_mk


def solve_multi_heuristic(
    jobs: List[JobM],
    methods: Optional[List[str]] = None
) -> Dict[str, Tuple[Sequence, int]]:
    """
    使用多种启发式算法求解多机FlowShop问题

    参数:
        jobs: 作业列表
        methods: 使用的方法列表 ('neh', 'sa', 'ga', 'ts', 'neh+2opt')

    返回:
        Dict: 方法名到(序列, makespan)的映射
    """
    if methods is None:
        methods = ['neh', 'sa', 'ga', 'ts']

    results = {}
    logger.info(f"[solve_multi] Starting, methods: {methods}")

    for method in methods:
        if method == 'neh':
            seq, mk = neh_heuristic(jobs)
            results[method] = (seq, mk)
        elif method == 'neh+2opt':
            seq, mk = neh_heuristic(jobs)
            seq, mk = two_opt_improve(seq, jobs)
            results[method] = (seq, mk)
        elif method == 'sa':
            seq, mk = simulated_annealing_mfs(jobs)
            results[method] = (seq, mk)
        elif method == 'ga':
            seq, mk = genetic_algorithm_mfs(jobs)
            results[method] = (seq, mk)
        elif method == 'ts':
            seq, mk = tabu_search_mfs(jobs)
            results[method] = (seq, mk)
        else:
            logger.warning(f"[solve_multi] Unknown method: {method}")

    logger.info(f"[solve_multi] Done, results: {[(k, v[1]) for k, v in results.items()]}")
    return results