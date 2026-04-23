import heapq
import math
import time
import tracemalloc
import matplotlib.pyplot as plt
import numpy as np

# 曼哈顿距离：与 4-neighbor 移动模式完全匹配
def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

# 欧几里得距离：直线距离，总是小于或等于实际网格步数
def euclidean(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Dijkstra：不提供任何预测，h 恒为 0
def dijkstra_h(p1, p2):
    return 0

# --- A* 算法 (带数据统计) ---
def a_star_with_metrics(grid, start, goal, h_func):
    # 开始监控内存和时间
    tracemalloc.start()
    start_time = time.perf_counter()
    
    rows, cols = grid.shape
    open_list = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    explored_nodes = []

    found = False
    while open_list:
        _, current = heapq.heappop(open_list)
        explored_nodes.append(current)

        if current == goal:
            found = True
            break

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and grid[neighbor] == 0:
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + h_func(neighbor, goal)
                    heapq.heappush(open_list, (f, neighbor))
    
    end_time = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    path = []
    if found:
        temp = goal
        while temp in came_from:
            path.append(temp)
            temp = came_from[temp]
            
    metrics = {
        "time_ms": (end_time - start_time) * 1000,
        "memory_kb": peak_mem / 1024,
        "nodes": len(explored_nodes)
    }
    return path, explored_nodes, metrics

# --- 地图构建与可视化 ---
def create_complex_map(size=50):
    grid = np.zeros((size, size))
    # 构建复杂的障碍墙
    grid[15:35, 25] = 1
    grid[15, 15:26] = 1
    grid[35, 15:26] = 1
    grid[5:15, 10] = 1
    grid[40:, 30] = 1
    return grid

def run_visual_comparison():
    size = 50
    grid = create_complex_map(size)
    start, goal = (25, 5), (25, 45)

    methods = [
        ("Manhattan", manhattan), 
        ("Euclidean", euclidean),
        ("Dijkstra", dijkstra_h)
    ]    
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    for i, (name, func) in enumerate(methods):
        path, explored, m = a_star_with_metrics(grid, start, goal, func)
        
        # 绘制地图和障碍
        axes[i].imshow(grid, cmap='binary', origin='upper', alpha=0.2)
        
        # 绘制搜索范围 (使用热力图色阶显示搜索顺序)
        if explored:
            ex, ey = zip(*explored)
            sc = axes[i].scatter(ey, ex, c=range(len(explored)), cmap='viridis', s=3, alpha=0.5)
        
        # 绘制最终路径
        if path:
            py, px = zip(*path)
            axes[i].plot(px, py, color='red', linewidth=2.5, label='Shortest Path')

        # 标注起点终点
        axes[i].plot(start[1], start[0], 'go', label='Start')
        axes[i].plot(goal[1], goal[0], 'rx', label='Goal')
        
        # 在子图标题中展示 Benchmark 数据
        title_str = (f"Method: {name}\n"
                     f"Nodes Explored: {m['nodes']}\n"
                     f"Time: {m['time_ms']:.2f} ms\n"
                     f"Peak Memory: {m['memory_kb']:.2f} KB")
        axes[i].set_title(title_str, fontsize=12, fontweight='bold')
        axes[i].legend(loc='lower right')

    plt.suptitle("A* Algorithm Performance Comparison: Manhattan vs Euclidean", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    run_visual_comparison()