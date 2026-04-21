import matplotlib.pyplot as plt
import networkx as nx
import sys

class MergeSortVisualizer:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_count = 0

    def sort(self, arr):
        """外部调用接口：清除旧图并开始排序"""
        self.graph.clear()
        self.node_count = 0
        return self._merge_sort(arr)

    def _merge_sort(self, arr):
        # 记录当前节点，用于构建递归树
        current_id = self.node_count
        label = f"ID:{current_id}\n{arr}"
        self.graph.add_node(current_id, label=label)
        
        # 递归终止条件：数组长度小于等于1
        if len(arr) <= 1:
            return arr

        # 分治步骤：折半拆分
        mid = len(arr) // 2
        
        # 处理左子树
        self.node_count += 1
        left_id = self.node_count
        self.graph.add_edge(current_id, left_id)
        left = self._merge_sort(arr[:mid])
        
        # 处理右子树
        self.node_count += 1
        right_id = self.node_count
        self.graph.add_edge(current_id, right_id)
        right = self._merge_sort(arr[mid:])

        # 合并步骤
        return self._merge(left, right)

    def _merge(self, left, right):
        res = []
        i = j = 0
        # 比较两个有序数组的元素
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                res.append(left[i]); i += 1
            else:
                res.append(right[j]); j += 1
        # 收集剩余元素
        res.extend(left[i:]); res.extend(right[j:])
        return res

    def draw_tree(self):
        """绘制递归调用树"""
        try:
            pos = self._hierarchy_pos(self.graph, 0)
            labels = nx.get_node_attributes(self.graph, 'label')
            
            plt.figure(figsize=(12, 7))
            nx.draw(self.graph, pos, with_labels=True, labels=labels, 
                    node_size=3000, node_color="skyblue", 
                    font_size=8, font_weight="bold", alpha=0.9)
            plt.title("Merge Sort Recursion Tree", fontsize=14)
            plt.show()
        except Exception as e:
            print(f"Drawing error: {e}")

    def _hierarchy_pos(self, G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
        """计算树状布局坐标的辅助函数"""
        pos = {root: (xcenter, vert_loc)}
        children = list(G.neighbors(root))
        if children:
            dx = width / len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos.update(self._hierarchy_pos(G, child, width=dx, 
                                             vert_gap=vert_gap, 
                                             vert_loc=vert_loc-vert_gap, 
                                             xcenter=nextx))
        return pos

if __name__ == "__main__":
    # 测试数据
    test_data = [38, 27, 43, 3, 9, 82, 10]
    print(f"Original Data: {test_data}")
    
    vis = MergeSortVisualizer()
    result = vis.sort(test_data)
    
    print(f"Sorted Result: {result}")
    print("Generating recursion tree visualization...")
    vis.draw_tree()