import time
import random
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from flowshop.flowshop_types import JobM, Sequence
from flowshop.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DynamicJob:
    job_id: int
    processing_times: Tuple[int, ...]
    arrival_time: float = 0.0
    priority: int = 0
    due_date: Optional[int] = None


@dataclass
class ScheduledEvent:
    job_id: int
    machine: int
    start_time: float
    end_time: float
    processing_time: int


@dataclass
class MachineState:
    machine_id: int
    available_at: float = 0.0
    current_job: Optional[int] = None


class DynamicFlowShop:

    def __init__(
        self,
        num_machines: int,
        jobs: List[DynamicJob],
        variation_rate: float = 0.0
    ):
        """
        初始化动态流水车间模拟器

        参数:
            num_machines: 机器数量
            jobs: DynamicJob对象列表
            variation_rate: 加工时间变异率（0.0到1.0）
        """
        self.num_machines = num_machines
        self.jobs = {job.job_id: job for job in jobs}
        self.variation_rate = variation_rate
        self.base_processing_times = {job.job_id: job.processing_times for job in jobs}

        logger.info(f"DynamicFlowShop initialized, n_jobs: {len(jobs)}, m_machines: {num_machines}, variation: {variation_rate}")

    def get_actual_processing_time(self, job_id: int, machine: int) -> int:
        """获取实际加工时间（考虑变异）"""
        base_time = self.base_processing_times[job_id][machine]

        if self.variation_rate > 0 and random.random() < self.variation_rate:
            variation = int(base_time * self.variation_rate)
            actual_time = max(1, base_time + random.randint(-variation, variation))
            return actual_time

        return base_time

    def simulate(
        self,
        dispatch_rule: str = "FIFO",
        reschedule_on_arrival: bool = False,
        reschedule_on_failure: bool = False,
        failure_rate: float = 0.0
    ) -> Tuple[List[ScheduledEvent], float, float]:
        """
        使用指定调度规则模拟动态流水车间

        调度规则:
        - FIFO: 先到先服务
        - SPT: 最短加工时间优先
        - EDD: 最早交货期优先
        - PRIORITY: 最高优先级优先

        参数:
            dispatch_rule: 作业选择规则
            reschedule_on_arrival: 新作业到达时是否重调度
            reschedule_on_failure: 机器故障时是否重调度
            failure_rate: 每单位时间机器故障概率

        返回:
            tuple: (scheduled_events, makespan, avg_tardiness)
        """
        start_time = time.time()
        logger.info(f"[DynamicSim] Starting, rule: {dispatch_rule}, reschedule: {reschedule_on_arrival}")

        events: List[ScheduledEvent] = []
        machines = [MachineState(i) for i in range(self.num_machines)]
        unscheduled_jobs = set(self.jobs.keys())
        arrived_jobs: List[DynamicJob] = []
        current_time = 0.0

        job_list = list(self.jobs.values())
        arrival_index = 0

        while unscheduled_jobs or arrived_jobs:
            while arrival_index < len(job_list) and job_list[arrival_index].arrival_time <= current_time:
                arrived_jobs.append(job_list[arrival_index])
                logger.debug(f"[DynamicSim] Job {arrival_index} arrived at {current_time}")
                arrival_index += 1

            available_jobs = [j for j in arrived_jobs if j.job_id in unscheduled_jobs]

            if not available_jobs:
                next_arrival = job_list[arrival_index].arrival_time if arrival_index < len(job_list) else float('inf')
                next_machine_free = min(m.available_at for m in machines)
                if next_arrival <= current_time and next_machine_free <= current_time:
                    current_time = max(next_arrival, next_machine_free)
                elif next_arrival > current_time:
                    current_time = next_arrival
                else:
                    current_time = next_machine_free

                while arrival_index < len(job_list) and job_list[arrival_index].arrival_time <= current_time:
                    arrived_jobs.append(job_list[arrival_index])
                    logger.debug(f"[DynamicSim] Job {arrival_index} arrived at {current_time}")
                    arrival_index += 1

                available_jobs = [j for j in arrived_jobs if j.job_id in unscheduled_jobs]

            if not available_jobs:
                break

            if dispatch_rule == "FIFO":
                available_jobs.sort(key=lambda j: j.arrival_time)
            elif dispatch_rule == "SPT":
                available_jobs.sort(key=lambda j: sum(j.processing_times))
            elif dispatch_rule == "EDD":
                available_jobs.sort(key=lambda j: j.due_date if j.due_date else float('inf'))
            elif dispatch_rule == "PRIORITY":
                available_jobs.sort(key=lambda j: -j.priority)
            else:
                available_jobs.sort(key=lambda j: j.arrival_time)

            selected_job = available_jobs[0]

            machine_end_times = []
            for m in range(self.num_machines):
                actual_time = self.get_actual_processing_time(selected_job.job_id, m)
                if m == 0:
                    start = max(current_time, machines[m].available_at)
                else:
                    start = max(machine_end_times[m-1], machines[m].available_at)
                end = start + actual_time
                machine_end_times.append(end)

                machines[m].available_at = end
                machines[m].current_job = selected_job.job_id

                event = ScheduledEvent(
                    job_id=selected_job.job_id,
                    machine=m,
                    start_time=start,
                    end_time=end,
                    processing_time=actual_time
                )
                events.append(event)

                if failure_rate > 0 and random.random() < failure_rate:
                    logger.debug(f"[DynamicSim] Machine {m} failed during job {selected_job.job_id}")
                    if reschedule_on_failure:
                        pass

            unscheduled_jobs.discard(selected_job.job_id)
            arrived_jobs.remove(selected_job)

            current_time = min(m.available_at for m in machines)

        makespan = max(e.end_time for e in events) if events else 0.0

        total_tardiness = 0.0
        for job in self.jobs.values():
            if job.due_date:
                job_events = [e.end_time for e in events if e.job_id == job.job_id]
                job_end = max(job_events) if job_events else 0.0
                tardiness = max(0, job_end - job.due_date)
                total_tardiness += tardiness

        avg_tardiness = total_tardiness / len(self.jobs) if self.jobs else 0.0

        elapsed = time.time() - start_time
        logger.info(f"[DynamicSim] Done, makespan: {makespan}, avg_tardiness: {avg_tardiness:.2f}, elapsed: {elapsed*1000:.2f}ms")

        return events, makespan, avg_tardiness

    def simulate_robust(
        self,
        method: str = "conservative",
        num_simulations: int = 100
    ) -> Dict[str, Any]:
        """
        运行鲁棒性仿真（考虑不确定加工时间）

        参数:
            method: 'conservative'（使用平均值）, 'optimistic'（使用最小值）, 'stochastic'（随机）
            num_simulations: 仿真次数

        返回:
            统计结果字典
        """
        start_time = time.time()
        logger.info(f"[RobustSim] Starting, method: {method}, n_sim: {num_simulations}")

        results = {
            'makespans': [],
            'avg_tardiness': [],
            'success_rate': []
        }

        original_variation = self.variation_rate
        self.variation_rate = 0.3

        for i in range(num_simulations):
            events, makespan, avg_tard = self.simulate()
            results['makespans'].append(makespan)
            results['avg_tardiness'].append(avg_tard)

        self.variation_rate = original_variation

        stats = {
            'mean_makespan': sum(results['makespans']) / len(results['makespans']),
            'min_makespan': min(results['makespans']),
            'max_makespan': max(results['makespans']),
            'std_makespan': (sum((x - stats['mean_makespan'])**2 for x in results['makespans']) / len(results['makespans'])) ** 0.5,
            'mean_tardiness': sum(results['avg_tardiness']) / len(results['avg_tardiness']),
        }

        elapsed = time.time() - start_time
        logger.info(f"[RobustSim] Done, mean_makespan: {stats['mean_makespan']:.2f}, elapsed: {elapsed*1000:.2f}ms")

        return stats


def generate_dynamic_instance(
    n_jobs: int,
    n_machines: int,
    arrival_rate: float = 0.5,
    priority_range: Tuple[int, int] = (1, 5),
    due_date_factor: float = 1.5,
    low: int = 1,
    high: int = 20
) -> List[DynamicJob]:
    """
    生成动态流水车间实例

    参数:
        n_jobs: 作业数量
        n_machines: 机器数量
        arrival_rate: 作业平均到达间隔（0-1，越小到达越快）
        priority_range: 优先级范围（min, max）
        due_date_factor: 交货期计算系数
        low: 最小加工时间
        high: 最大加工时间

    返回:
        DynamicJob对象列表
    """
    jobs = []
    current_time = 0.0

    for i in range(n_jobs):
        processing_times = tuple(random.randint(low, high) for _ in range(n_machines))
        total_time = sum(processing_times)

        if arrival_rate > 0:
            inter_arrival = random.expovariate(arrival_rate)
        else:
            inter_arrival = 0

        current_time += inter_arrival
        priority = random.randint(*priority_range)
        due_date = int(current_time + total_time * due_date_factor)

        job = DynamicJob(
            job_id=i,
            processing_times=processing_times,
            arrival_time=current_time,
            priority=priority,
            due_date=due_date
        )
        jobs.append(job)

    logger.debug(f"[generate_dynamic_instance] Generated {n_jobs} jobs, max_arrival: {current_time}")
    return jobs


def compare_dispatch_rules(
    jobs: List[DynamicJob],
    num_machines: int,
    rules: Optional[List[str]] = None
) -> Dict[str, Tuple[float, float]]:
    """
    比较不同调度规则的性能

    参数:
        jobs: 动态作业列表
        num_machines: 机器数量
        rules: 要比较的调度规则列表

    返回:
        Dict: 规则名到(makespan, avg_tardiness)的映射
    """
    if rules is None:
        rules = ["FIFO", "SPT", "EDD", "PRIORITY"]

    results = {}
    logger.info(f"[compare_rules] Starting, rules: {rules}")

    for rule in rules:
        shop = DynamicFlowShop(num_machines, jobs)
        _, makespan, avg_tard = shop.simulate(dispatch_rule=rule)
        results[rule] = (makespan, avg_tard)
        logger.info(f"[compare_rules] {rule}: makespan={makespan:.2f}, tardiness={avg_tard:.2f}")

    best_rule = min(results.items(), key=lambda x: x[1][0])
    logger.info(f"[compare_rules] Best rule: {best_rule[0]} with makespan {best_rule[1][0]:.2f}")

    return results