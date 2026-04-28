import random
from typing import List
from flowshop.flowshop_types import Job
from flowshop.constants import DEFAULT_LOW, DEFAULT_HIGH
from flowshop.logging_config import get_logger

logger = get_logger(__name__)


def generate_random_instance(
    n: int,
    low: int = DEFAULT_LOW,
    high: int = DEFAULT_HIGH
) -> List[Job]:
    """
    生成随机FlowShop实例

    参数:
        n: 作业数量
        low: 最小加工时间（包含）
        high: 最大加工时间（包含）

    返回:
        作业列表，每个作业为二元组(p1, p2)
    """
    logger.debug(f"[generate_random_instance] Entry, n={n}, low={low}, high={high}")

    if n <= 0:
        raise ValueError(f"n must be > 0, got: {n}")
    if low > high:
        raise ValueError(f"low({low}) cannot be > high({high})")

    jobs = [(random.randint(low, high), random.randint(low, high)) for _ in range(n)]

    logger.debug(f"[generate_random_instance] Done, generated {len(jobs)} jobs")
    return jobs


def set_random_seed(seed: int) -> None:
    """
    设置随机种子

    参数:
        seed: 随机种子值
    """
    logger.debug(f"[set_random_seed] Setting seed: {seed}")
    random.seed(seed)
    logger.debug("[set_random_seed] Seed set")