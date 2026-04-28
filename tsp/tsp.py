"""
TSP（旅行商问题）算法演示程序主入口

本程序实现了多种TSP求解算法，包括：
- 暴力枚举算法（小规模精确解）
- 最近邻贪心算法（快速启发式）
- Held-Karp动态规划算法（中规模精确解）
- 2-opt局部优化算法
- 模拟退火算法（大规模启发式）

运行方式：python tsp.py
"""

from experiments import run_demo

if __name__ == "__main__":
    run_demo()
