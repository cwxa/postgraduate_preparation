"""
数据类型定义模块

包含TSP实验中使用的核心数据类：
- InstanceSpec: 实验实例配置
- AlgorithmResult: 单个算法的结果
- ExperimentBundle: 一次实验的完整数据集合
"""

from dataclasses import dataclass, field

from constants import EPSILON


@dataclass(frozen=True)
class InstanceSpec:
    """
    描述一次实验实例的配置
    
    Attributes:
        name: 实例名称
        city_count: 城市数量
        seed: 随机种子（用于生成城市坐标）
        baseline_label: 基准算法标签
        sa_temp: 模拟退火初始温度
        sa_cooling: 模拟退火降温速率
        sa_steps: 模拟退火最大迭代步数
    """
    
    name: str
    city_count: int
    seed: int
    baseline_label: str
    sa_temp: float
    sa_cooling: float
    sa_steps: int


@dataclass
class AlgorithmResult:
    """
    保存单个算法的结果，避免到处传字典
    
    Attributes:
        name: 算法名称
        tour: 路径序列（城市索引列表，起点和终点都是0）
        cost: 路径总代价
        time_ms: 运行时间（毫秒）
        history: 算法迭代历史（用于模拟退火的收敛曲线）
    """
    
    name: str
    tour: list[int]
    cost: float
    time_ms: float
    history: list[tuple[int, float, float]] = field(default_factory=list)

    def gap_pct(self, baseline_cost: float) -> float:
        """
        计算相对基准解的误差率（百分比）
        
        Args:
            baseline_cost: 基准解的代价
        
        Returns:
            误差率百分比，公式: (cost - baseline) / baseline * 100%
        """
        if abs(baseline_cost) < EPSILON:
            return 0.0
        return ((self.cost - baseline_cost) / baseline_cost) * 100

    def route_preview(self, max_visible: int = 7) -> str:
        """
        把较长路径压缩成终端友好的预览格式
        
        Args:
            max_visible: 最大显示的城市数量（默认7个）
        
        Returns:
            压缩后的路径预览字符串，如 "0->1->2->...->5->6->0"
        """
        if len(self.tour) <= max_visible:
            return "->".join(map(str, self.tour))

        head_count = max_visible // 2
        tail_count = max_visible - head_count
        head = "->".join(map(str, self.tour[:head_count]))
        tail = "->".join(map(str, self.tour[-tail_count:]))
        return f"{head}->...->{tail}"


@dataclass
class ExperimentBundle:
    """
    把一次实例实验的所有数据收拢到一起，方便打印和画图
    
    Attributes:
        spec: 实验配置
        cities: 城市坐标列表
        baseline_cost: 基准解代价
        results: 所有算法的结果列表
        by_name: 按名称索引的结果字典
    """
    
    spec: InstanceSpec
    cities: list[tuple[int, int]]
    baseline_cost: float
    results: list[AlgorithmResult]
    by_name: dict[str, AlgorithmResult]
