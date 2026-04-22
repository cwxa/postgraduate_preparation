import time

# --- 1. 递归 + 备忘录 (Top-down) ---
def knapsack_memo(weights, values, capacity):
    memo = {}

    def dfs(index, current_capacity):
        if index < 0 or current_capacity <= 0:
            return 0
        state = (index, current_capacity)
        if state in memo:
            return memo[state]
        
        # 不选当前物品
        res = dfs(index - 1, current_capacity)
        # 选当前物品 (如果装得下)
        if current_capacity >= weights[index]:
            res = max(res, values[index] + dfs(index - 1, current_capacity - weights[index]))
        
        memo[state] = res
        return res

    return dfs(len(weights) - 1, capacity)


# --- 2. 二维动态规划 (Bottom-up) ---
def knapsack_2d(weights, values, capacity):
    n = len(weights)
    # dp[i][j] 表示前 i 个物品在容量为 j 时的最大价值
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i-1] <= w:
                # 状态转移：max(不放, 放)
                dp[i][w] = max(dp[i-1][w], dp[i-1][w - weights[i-1]] + values[i-1])
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][capacity]


# --- 3. 一维动态规划 (Space Optimized) ---
def knapsack_1d(weights, values, capacity):
    # dp[w] 表示容量为 w 时的最大价值
    dp = [0] * (capacity + 1)
    
    for i in range(len(weights)):
        # 必须逆序遍历，防止同一物品被重复放入（变动为完全背包问题）
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
            
    return dp[capacity]


# --- 性能测试 ---
def benchmark():
    # 测试数据：100个物品，背包容量1000
    weights = [i % 50 + 1 for i in range(100)]
    values = [i % 100 + 10 for i in range(100)]
    capacity = 1000

    print(f"Testing with {len(weights)} items, Capacity: {capacity}\n")

    methods = [
        ("Memoization (Recursive)", knapsack_memo),
        ("2D Table (Iterative)", knapsack_2d),
        ("1D Table (Optimized)", knapsack_1d)
    ]

    for name, func in methods:
        start = time.perf_counter()
        result = func(weights, values, capacity)
        end = time.perf_counter()
        print(f"[{name}] Result: {result}, Time: {(end - start)*1000:.2f} ms")

if __name__ == "__main__":
    benchmark()