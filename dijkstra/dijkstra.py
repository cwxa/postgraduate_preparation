import heapq
import networkx as nx
import matplotlib.pyplot as plt

def dijkstra(graph, start):
    """
    实现 Dijkstra 算法
    :param graph: 邻接表字典 {u: {v: weight}}
    :param start: 起始节点
    :return: distances (最短距离字典), predecessors (路径前驱字典)
    """
    # 初始化：所有节点距离设为无穷大，起点距离为 0
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    
    # 优先队列 (距离, 节点)
    priority_queue = [(0, start)]
    
    # 记录前驱节点，用于重建最短路径
    predecessors = {node: None for node in graph}

    while priority_queue:
        # 获取当前已知距离最小的节点
        current_distance, current_node = heapq.heappop(priority_queue)

        # 节点的距离已被更新过，跳过旧的记录
        if current_distance > distances[current_node]:
            continue

        # 遍历邻居节点并进行松弛操作
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            # 找到更短路径时更新
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
                
    return distances, predecessors

def run_test_and_visualize():
    # 1. 定义简单带权图
    graph = {
        'A': {'B': 4, 'C': 2},
        'B': {'C': 1, 'D': 2, 'E': 3},
        'C': {'B': 1, 'D': 4, 'E': 5},
        'D': {'E': 1},
        'E': {}
    }

    start_node = 'A'
    
    # 2. 执行算法
    distances, predecessors = dijkstra(graph, start_node)
    
    # 3. 打印控制台输出
    print(f"--- Dijkstra Results from node {start_node} ---")
    for node in distances:
        path = []
        curr = node
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
        path.reverse()
        print(f"Target: {node} | Distance: {distances[node]} | Path: {' -> '.join(path)}")

    # 4. 可视化图
    G = nx.DiGraph()
    for u in graph:
        for v, w in graph[u].items():
            G.add_edge(u, v, weight=w)

    plt.figure(figsize=(10, 7))
    pos = nx.spring_layout(G, seed=42)  # 固定布局

    # 绘制背景：节点和所有边
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightgray')
    nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='black', alpha=0.3, arrows=True)
    
    # 绘制边权值
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # 高亮显示最短路径边（基于 predecessors 结果）
    path_edges = []
    for node, pred in predecessors.items():
        if pred is not None:
            path_edges.append((pred, node))
    
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=2.5, edge_color='red', arrows=True)
    nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_color='orange', node_size=800)

    plt.title(f"Dijkstra Visualization (Start: {start_node}, Red lines = Shortest Paths)")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    run_test_and_visualize()