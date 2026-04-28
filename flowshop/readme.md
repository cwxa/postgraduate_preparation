# FlowShop 项目

## 快速开始

### 运行项目

```bash
python flowshop/main.py
```

## 项目结构

```
flowshop/
├── main.py              # 主入口，运行后自动执行所有实验
├── algorithms.py        # Johnson算法（2机最优解）
├── heuristics.py        # 多机启发式算法（NEH/SA/GA/TS）
├── dynamic_scheduler.py # 动态调度仿真（FIFO/SPT/EDD）
├── visualization.py     # 甘特图和对比图绘制
├── experiments.py       # 实验运行器
├── logging_config.py    # 日志配置
├── note.md              # 学习笔记与实验分析
├── figures/             # 生成的图表
└── logs/                # 详细日志
```

## 输出内容

运行后生成以下文件：

### 图表文件（figures/）

| 文件 | 说明 |
|------|------|
| johnson_gantt.png | Johnson算法甘特图 |
| random_gantt.png | 随机序列甘特图 |
| johnson_vs_random.png | 100次实验对比 |
| multi_machine_heuristics.png | 多算法对比 |
| multi_machine_gantt.png | 多机器调度图 |
| dynamic_dispatch_comparison.png | 动态规则对比 |
| dynamic_fifo_gantt.png | 动态调度图 |

### 日志文件

- `logs/flowshop.log`：详细执行日志（DEBUG级别）
- 控制台：仅显示关键结果（WARNING级别）

## 主要功能

1. **2机Flow Shop**：Johnson最优算法
2. **多机Flow Shop**：NEH、SA、GA、TS启发式算法
3. **动态Flow Shop**：FIFO、SPT、EDD、PRIORITY调度规则

## 查看实验分析

实验结果和分析请参考 `note.md` 文件。

## 推荐参考

- [Flow shop scheduling - Wikipedia](https://en.wikipedia.org/wiki/Flow_shop_scheduling)
- [Johnson's rule - Wikipedia](https://en.wikipedia.org/wiki/Johnson%27s_rule)