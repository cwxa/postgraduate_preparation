import copy

def floyd_warshall(graph):
    """
    Floyd-Warshall 算法实现
    graph: 邻接矩阵，float('inf') 表示不连通
    """
    # 初始化距离矩阵
    dist = copy.deepcopy(graph)
    n = len(dist)
    
    print("Initial distance matrix:")
    print_matrix(dist)
    
    # 动态规划过程：k 为当前允许经过的中间节点
    for k in range(n):
        print(f"\n--- Iteration {k+1}: Adding node {k} as intermediate ---")
        for i in range(n):
            for j in range(n):
                # 如果经过节点 k 的路径比当前记录的路径更短，则更新
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
        
        print_matrix(dist)
    
    return dist

def print_matrix(matrix):
    """
    美化输出矩阵
    """
    for row in matrix:
        formatted_row = [f"{x:>4}" if x != float('inf') else " INF" for x in row]
        print(" ".join(formatted_row))

if __name__ == "__main__":
    # 定义无穷大
    INF = float('inf')
    
    # 示例图的邻接矩阵 (0-3 四个节点)
    # 0 -> 2 (3), 0 -> 1 (5)
    # 1 -> 2 (2), 1 -> 0 (8)
    # 2 -> 0 (5), 2 -> 3 (1)
    # 3 -> 0 (2)
    example_graph = [
        [0,   5,   3,   INF],
        [8,   0,   2,   INF],
        [5,   INF, 0,   1],
        [2,   INF, INF, 0]
    ]
    
    final_distances = floyd_warshall(example_graph)
    
    print("\nFinal Shortest Path Matrix:")
    print_matrix(final_distances)