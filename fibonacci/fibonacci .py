import time
import math
import sys
import numpy as np
from functools import lru_cache
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 提高递归深度限制，以防测试较大的 n
sys.setrecursionlimit(2000)

# 1. 纯递归 (Recursive) - 注意：n > 35 会非常慢
def fib_recursive(n):
    if n <= 1: return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)

# 2. 记忆化递归 (Memoization)
@lru_cache(None)
def fib_memo(n):
    if n <= 1: return n
    return fib_memo(n - 1) + fib_memo(n - 2)

# 3. 迭代法 (Iterative) - 空间 O(1)
def fib_iterative(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# 4. 矩阵快速幂 (Matrix Exponentiation)
def fib_matrix(n):
    if n <= 1: return n
    # 使用 numpy 加速矩阵运算
    matrix = np.array([[1, 1], [1, 0]], dtype=object) 
    res = np.linalg.matrix_power(matrix, n - 1)
    return res[0][0]

# 5. 通项公式 (Binet's Formula)
def fib_formula(n):
    if n > 70: return "Precision Risk" # 超过70精度开始明显下降
    phi = (1 + math.sqrt(5)) / 2
    return round((phi**n) / math.sqrt(5))

# --- 性能测试函数 ---
def benchmark(n):
    methods = [
        ("递归法", fib_recursive),
        ("记忆化递归", fib_memo),
        ("迭代法", fib_iterative),
        ("矩阵快速幂", fib_matrix),
        ("通项公式", fib_formula)
    ]
    
    print(f"{'方法':<15} | {'结果':<15} | {'耗时 (秒)':<15}")
    print("-" * 50)
    
    for name, func in methods:
        # 由于纯递归太慢，超过 35 就跳过
        if name == "递归法" and n > 35:
            print(f"{name:<15} | {'跳过 (太慢)':<15} | {'N/A':<15}")
            continue
            
        start = time.perf_counter()
        result = func(n)
        end = time.perf_counter()
        
        # 格式化结果显示（防止结果过长）
        display_res = str(result) if len(str(result)) < 15 else str(result)[:12] + "..."
        
        print(f"{name:<15} | {display_res:<15} | {end - start:.8f}")

if __name__ == "__main__":
    test_n = 35
    print(f"开始测试 n = {test_n} 的性能：\n")
    benchmark(test_n)
    
    print("\n" + "="*50 + "\n")
    
    test_n_large = 500
    print(f"开始测试大规模数据 n = {test_n_large} 的性能：\n")
    benchmark(test_n_large)