
## 📅 10阶段学习计划（每天2小时，Python）

### 🔁 通用建议
- 每天结构：20分钟理论学习 + 60分钟编码实践 + 40分钟调试/总结/笔记
- 使用 **Jupyter Notebook** 进行实验，最终整理成 `.py` 脚本上传 GitHub
- 每阶段结束后，在 GitHub 仓库中创建一个 `README.md` 记录关键收获和运行结果

---

## ✅ 阶段1：算法基础与时间复杂度分析（5天，共10小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | 大O表示法，递归与迭代复杂度分析 | 分析斐波那契数列的多种实现复杂度 | [Big-O Cheat Sheet](https://www.bigocheatsheet.com/) |
| 2 | 分治法：归并排序、快速排序 | 实现归并排序并绘制递归树 |[排序演示](https://visualgo.net/zh) |
| 3 | 动态规划：背包问题 | 实现0-1背包问题（DP表） | [背包问题详解](https://www.geeksforgeeks.org/0-1-knapsack-problem-dp-10/) |
| 4 | 动态规划：最短路径（Floyd-Warshall） | 实现Floyd算法，输出任意两点最短路径 | [Floyd-Warshall](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm) |
| 5 | 阶段复习与小测验 | 写一个函数判断任意代码的时间复杂度；整理笔记 | 自测题：LeetCode 53（最大子序和，动态规划） |

**✅ 阶段成果**：  
- 能独立分析常见算法的时间复杂度  
- 提交一个 `algorithms_basics.py`，包含归并排序、背包DP、Floyd算法

---

## ✅ 阶段2：路径规划基础（5天，共10小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | 图论基础，邻接矩阵/邻接表 | 用Python实现图结构（字典+列表） | networkx库入门 |
| 2 | Dijkstra算法 | 实现Dijkstra，并在简单图上测试 | [Dijkstra可视化](https://www.cs.usfca.edu/~galles/visualization/Dijkstra.html) |
| 3 | A*算法与启发函数（曼哈顿、欧几里得） | 实现A*，解决网格地图最短路径 | [Red Blob Games: A*](https://www.redblobgames.com/pathfinding/a-star/) |
| 4 | 可视化路径（matplotlib） | 绘制网格地图，展示Dijkstra/A*路径 | 使用 `matplotlib.patches.Rectangle` |
| 5 | 对比Dijkstra与A*效率 | 在随机迷宫中测试并记录耗时 | 生成随机迷宫（递归回溯法） |

**✅ 阶段成果**：  
- 代码 `path_planning.py` 包含Dijkstra和A*，可输出路径及可视化  
- 性能对比表格（不同地图大小）

---

## ✅ 阶段3：旅行商问题与启发式算法（6天，共12小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | TSP问题定义，暴力搜索（n≤10） | 实现全排列枚举TSP | 使用 `itertools.permutations` |
| 2 | 最近邻贪心算法 | 实现贪心TSP，分析不足 | 对比最优解（小规模） |
| 3 | 动态规划（Held-Karp） | 实现O(n²·2ⁿ)的DP求解TSP | [Held-Karp算法](https://en.wikipedia.org/wiki/Held-Karp_algorithm) |
| 4 | 模拟退火（SA）原理 | 实现SA求解TSP，设计邻域结构（2-opt） | [模拟退火TSP教程](https://towardsdatascience.com/simulated-annealing-for-tsp-7c7d0b6b5f6c) |
| 5 | SA参数调优（温度衰减、马尔可夫链长） | 绘制收敛曲线，找最佳参数 | 可视化：`matplotlib` 绘制距离随迭代变化 |
| 6 | 对比多种算法效果（小规模标准库TSPLIB） | 使用 `tsplib95` 加载 `berlin52` 等实例 | [TSPLIB数据集](http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/) |

**✅ 阶段成果**：  
- 代码 `tsp_solvers.py` 包含暴力、贪心、DP、SA  
- 报告对比各算法在 `berlin52` 上的解质量与时间

---

## ✅ 阶段4：调度问题入门（5天，共10小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | 调度问题基本概念：makespan、FlowShop、JobShop | 描述并建模一个简单2机FlowShop | [调度问题综述](https://www.youtube.com/watch?v=oYc9qFqZ0nY) |
| 2 | 双机FlowShop的Johnson算法 | 实现Johnson算法，验证正确性 | [Johnson's rule](https://en.wikipedia.org/wiki/Johnson%27s_rule) |
| 3 | 单机调度：加权完成时间和（1||ΣwjCj） | 实现Smith规则（WSPT） | 调度理论书籍：Pinedo |
| 4 | 可视化甘特图（matplotlib） | 画出调度结果的甘特图 | `matplotlib` 的 `barh` |
| 5 | 随机生成调度实例并测试 | 对比Johnson与随机调度的makespan | 编写 `scheduling_utils.py` |

**✅ 阶段成果**：  
- 代码 `flowshop_johnson.py` 可求解双机FlowShop并画甘特图  
- 生成10个随机实例的对比报告

---

## ✅ 阶段5：局部搜索与变邻域搜索（5天，共10小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | 局部搜索基本框架，邻域结构设计 | 对TSP实现2-opt局部搜索 | [2-opt可视化](https://en.wikipedia.org/wiki/2-opt) |
| 2 | 变邻域搜索（VND）原理 | 实现VND，使用2-opt, 3-opt, Or-opt | 论文：Hansen & Mladenović |
| 3 | 将VND应用于FlowShop调度 | 设计调度问题的邻域（交换、插入） | 参考：Taillard的基准 |
| 4 | 对比VND与模拟退火（SA） | 在相同实例上比较收敛速度和解质量 | 绘制箱线图 |
| 5 | 阶段项目：实现一个混合算法（SA+VND） | 在TSP或FlowShop上测试 | 代码整合，增加参数自动调优 |

**✅ 阶段成果**：  
- 代码 `vnd_scheduling.py` 能解决FlowShop或TSP  
- 混合算法性能报告

---

## ✅ 阶段6：进化算法（6天，共12小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | 遗传算法（GA）基本原理：编码、选择、交叉、变异 | 实现二进制编码GA求解函数最大值 | [GA教程](https://www.geeksforgeeks.org/genetic-algorithms/) |
| 2 | 顺序编码（排列编码）解决TSP | 实现PMX交叉、交换变异 | 参考：`deap`库示例 |
| 3 | 将GA应用于FlowShop调度（排列编码） | 实现调度GA，目标最小化makespan | [论文：GA for FlowShop](https://www.researchgate.net/publication/220425699) |
| 4 | 多目标优化简介，Pareto支配 | 实现非支配排序 | [NSGA-II论文](https://ieeexplore.ieee.org/document/996017) |
| 5 | 使用 `pymoo` 库运行NSGA-II | 解决两目标FlowShop（makespan + 总流时间） | [pymoo官方文档](https://pymoo.org/) |
| 6 | 对比单目标GA与多目标NSGA-II | 可视化Pareto前沿，分析结果 | 使用 `matplotlib` 绘制 |

**✅ 阶段成果**：  
- 代码 `ga_tsp.py` 和 `ga_flowshop.py`  
- 多目标优化结果图（Pareto前沿）

---

## ✅ 阶段7：高级算法与边缘计算（5天，共10小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | 粒子群优化（PSO）原理 | 实现标准PSO求解Sphere函数 | [PSO教程](https://machinelearningmastery.com/particle-swarm-optimization/) |
| 2 | 离散PSO解决TSP | 修改速度更新公式，使用交换序 | [离散PSO论文](https://www.sciencedirect.com/science/article/pii/S0305054812002035) |
| 3 | 博弈论基础：纳什均衡、囚徒困境 | 用Python实现收益矩阵，求纯策略纳什均衡 | [博弈论入门](https://www.youtube.com/watch?v=PCWzYg3mFkg) |
| 4 | 边缘计算概念（任务卸载、资源调度） | 阅读一篇综述，写200字总结 | 论文：Edge computing scheduling survey |
| 5 | 将博弈论用于边缘计算调度（简单模型） | 实现一个任务卸载的博弈模型，求均衡 | 参考：[边缘计算中的博弈论](https://ieeexplore.ieee.org/document/8771322) |

**✅ 阶段成果**：  
- 代码 `pso_tsp.py` 和 `game_theory_scheduling.py`  
- 一篇边缘计算+博弈论的读书笔记

---

## ✅ 阶段8：强化学习入门（6天，共12小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | 强化学习基本概念（MDP, 策略, 值函数） | 手动实现Q-learning解决迷宫（grid world） | [OpenAI Spinning Up](https://spinningup.openai.com/) |
| 2 | 深度Q网络（DQN）原理 | 使用 `stable-baselines3` 跑DQN解决CartPole | [SB3文档](https://stable-baselines3.readthedocs.io/) |
| 3 | PPO算法简介 | 跑通PPO在CartPole上的训练与评估 | PPO论文：Schulman et al. |
| 4 | 将RL用于单机调度问题（环境设计） | 用Gym环境封装单机调度，状态为剩余作业特征 | [论文：RL for scheduling](https://arxiv.org/abs/2102.04296) |
| 5 | 训练PPO解决简单调度问题（n=5作业） | 对比随机调度、WSPT规则 | 使用自定义Gym环境 |
| 6 | 总结：RL与经典算法的优缺点 | 写一篇300字博客风格总结 | 发布到GitHub仓库 |

**✅ 阶段成果**：  
- 代码 `rl_scheduling.py`，自定义Gym环境  
- 训练日志与结果对比表

---

## ✅ 阶段9：数学基础与信息熵（4天，共8小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | 信息熵定义与计算 | 实现熵函数，计算随机变量的熵 | [熵的直观解释](https://towardsdatascience.com/what-is-entropy-9c2d6e2d2d3e) |
| 2 | 帕累托最优（Pareto Optimality） | 生成随机多目标点，可视化Pareto前沿 | `matplotlib` 散点图，高亮非支配解 |
| 3 | 模糊数学基础：隶属度、模糊集运算 | 实现模糊交并补，用于简单决策 | [模糊逻辑教程](https://www.cse.unsw.edu.au/~cs9417/ML/Fuzzy/Introduction.html) |
| 4 | 综合应用：用熵权法做多指标决策 | 实现熵权法（EWM）求解调度方案评分 | 参考：[熵权法Python实现](https://github.com/guofei9987/scikit-opt/blob/master/sko/EWM.py) |

**✅ 阶段成果**：  
- 代码 `math_tools.py` 包含熵、Pareto、模糊运算  
- 一个演示熵权法评价调度方案的Jupyter Notebook

---

## ✅ 阶段10：GKD项目专项准备（5天，共10小时）

| 天数 | 学习内容 | 实践任务 | 推荐资源 |
|------|----------|----------|----------|
| 1 | 麒麟操作系统（Kylin OS）基础 | 在虚拟机或实体机上安装Kylin，搭建Python环境 | [麒麟官网](http://www.kylinos.cn/) |
| 2 | 前端开发基础（HTML/CSS/JS） | 制作一个简单的调度参数输入页面 | [MDN Web Docs](https://developer.mozilla.org/) |
| 3 | 将后端算法封装为Web服务（Flask） | 用Flask提供API，前端调用并显示甘特图 | Flask + matplotlib 生成图片 |
| 4 | 三维建图效果（Three.js 或 Plotly） | 用Python生成三维地形图，展示风险区域 | [Plotly 3D Surface](https://plotly.com/python/3d-surface-plots/) |
| 5 | 海洋风险评估：阅读张教授PDF | 写一篇读书笔记（500字），总结风险评估框架 | 使用Markdown记录，上传GitHub |

**✅ 阶段成果**：  
- 在麒麟系统上成功运行一个完整的Web demo（调度算法可视化）  
- 三维风险图截图 + 风险评估笔记

---

## 📌 最终综合项目（可选，建议作为结业挑战）

**目标**：结合多个阶段所学，实现一个**基于强化学习或进化算法的动态调度系统**，并带有前端可视化界面。

**要求**：
- 后端：Python实现调度算法（GA/SA/PPO任意）
- 前端：Streamlit或Flask，可输入作业参数
- 可视化：甘特图 + 关键指标