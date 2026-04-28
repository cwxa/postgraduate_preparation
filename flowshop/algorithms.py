import time
from typing import List, Tuple, Optional
from flowshop.flowshop_types import Job, Sequence, Schedule, ScheduleResult
from flowshop.logging_config import get_logger

logger = get_logger(__name__)


class FlowShop2Machine:

    def __init__(self, jobs: List[Job]):
        """
        初始化2机FlowShop调度器

        参数:
            jobs: 作业列表，每个作业是二元组(p1, p2)，其中p1是M1加工时间，p2是M2加工时间
        """
        if not jobs:
            raise ValueError("jobs list cannot be empty")
        if not all(len(job) == 2 for job in jobs):
            raise ValueError("each job must have exactly 2 processing times (p1, p2)")

        self.jobs = jobs
        self.n = len(jobs)
        logger.info(f"FlowShop2Machine initialized, n_jobs: {self.n}")

    def johnson(self) -> Sequence:
        """
        Johnson算法：求解2机FlowShop问题的最优序列

        算法步骤:
        - L组 (p1 <= p2): 按p1升序排列，先加工
        - R组 (p1 > p2): 按p2降序排列，后加工

        返回:
            最优作业序列（作业索引列表）
        """
        start_time = time.time()
        logger.info(f"[Johnson] Starting, n_jobs: {self.n}")

        if len(self.jobs) != self.n:
            raise ValueError(f"Job count mismatch: expected {self.n}, got {len(self.jobs)}")

        jobs_with_idx = [(i, self.jobs[i][0], self.jobs[i][1]) for i in range(self.n)]
        left, right = [], []

        for idx, p1, p2 in jobs_with_idx:
            if p1 <= p2:
                left.append((idx, p1, p2))
            else:
                right.append((idx, p1, p2))

        logger.debug(f"[Johnson] Grouping done, L: {len(left)}, R: {len(right)}")

        left.sort(key=lambda x: x[1])
        right.sort(key=lambda x: x[2], reverse=True)

        result = [item[0] for item in left] + [item[0] for item in right]
        elapsed = time.time() - start_time

        logger.info(f"[Johnson] Done, sequence: {result}, elapsed: {elapsed*1000:.2f}ms")
        return result

    def calculate_schedule(self, sequence: Sequence) -> ScheduleResult:
        """
        根据给定序列计算调度方案

        参数:
            sequence: 作业索引序列

        返回:
            tuple: (schedule, makespan, idle_m2_total)
        """
        start_time = time.time()
        logger.info(f"[Schedule] Starting, seq_len: {len(sequence)}")

        if len(sequence) != self.n:
            raise ValueError(f"Sequence length mismatch: expected {self.n}, got {len(sequence)}")
        if set(sequence) != set(range(self.n)):
            raise ValueError("sequence must contain all job indices without duplication")

        time_m1 = 0
        time_m2 = 0
        schedule = {"M1": [], "M2": []}
        idle_m2_total = 0

        for job_id in sequence:
            p1, p2 = self.jobs[job_id]

            start_m1 = time_m1
            end_m1 = start_m1 + p1
            time_m1 = end_m1

            start_m2 = max(time_m2, end_m1)
            idle_delta = start_m2 - time_m2
            if idle_delta > 0:
                idle_m2_total += idle_delta
                logger.debug(f"[Schedule] M2 idle {idle_delta} units, waiting for job {job_id}")

            end_m2 = start_m2 + p2
            time_m2 = end_m2

            schedule["M1"].append((job_id, start_m1, p1))
            schedule["M2"].append((job_id, start_m2, p2))

            logger.debug(f"[Schedule] Job {job_id}: M1({start_m1}-{end_m1}), M2({start_m2}-{end_m2})")

        makespan = time_m2
        elapsed = time.time() - start_time

        logger.info(f"[Schedule] Done, makespan: {makespan}, M2 idle: {idle_m2_total}, elapsed: {elapsed*1000:.2f}ms")
        return schedule, makespan, idle_m2_total


def solve_johnson(jobs: List[Job]) -> Sequence:
    """
    求解2机FlowShop问题

    参数:
        jobs: 作业列表

    返回:
        最优序列
    """
    logger.info(f"[solve_johnson] Entry, n_jobs: {len(jobs)}")
    model = FlowShop2Machine(jobs)
    result = model.johnson()
    logger.info(f"[solve_johnson] Exit, seq_len: {len(result)}")
    return result


def evaluate_schedule(jobs: List[Job], sequence: Sequence) -> ScheduleResult:
    """
    评估给定序列的调度结果

    参数:
        jobs: 作业列表
        sequence: 加工序列

    返回:
        调度结果元组
    """
    logger.info(f"[evaluate_schedule] Entry, n_jobs: {len(jobs)}, seq_len: {len(sequence)}")
    model = FlowShop2Machine(jobs)
    result = model.calculate_schedule(sequence)
    logger.info(f"[evaluate_schedule] Exit, makespan: {result[1]}")
    return result