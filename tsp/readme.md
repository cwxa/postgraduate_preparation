# TSP 项目说明

## 怎么运行

在仓库根目录执行：

```powershell
python tsp\tsp.py
```

## 会生成什么

运行后会做三组实验：

* `9 cities`：小规模，包含精确最优解对比
* `12 cities`：中规模，包含 Held-Karp 最优解对比
* `18 cities`：大规模，只比较启发式方法

同时会输出英文实验表格，并生成图片到：

```text
tsp/figures/
```

目录按规模拆分：

* `tsp/figures/small/`
  包含小规模实例的路径图和 summary 图

* `tsp/figures/medium/`
  包含中规模实例的路径图和 summary 图

* `tsp/figures/large/`
  包含大规模实例的路径图和 summary 图

* `tsp/figures/cross_instance/`
  包含跨实例的收敛图、总览图、runtime 对数图、gap 对数兼容图

## 怎么看图

建议按下面顺序看：

1. 先看 `small/routes.png`、`medium/routes.png`、`large/routes.png`
   作用：看不同算法走出来的路径形状差异

2. 再看各目录下的 `summary.png`
   作用：看当前规模下的 gap 和 runtime 对比

3. 最后看 `cross_instance/` 里的总览图
   重点图：
   * `all_instances_summary.png`
   * `runtime_log_summary.png`
   * `gap_log_summary.png`
   * `sa_convergence.png`

## 指标怎么理解

* `baseline`
  当前实例里拿来做比较的参考解

* `gap`
  公式为：

```text
gap = (cost - baseline) / baseline * 100%
```

* `runtime`
  算法运行时间，单位是毫秒（ms）

## 推荐读图顺序

如果只想快速把握结果，建议：

1. 看 `medium/summary.png`
2. 看 `large/summary.png`
3. 看 `cross_instance/runtime_log_summary.png`
4. 看 `cross_instance/gap_log_summary.png`

这样最快能看出不同方法在“解质量”和“耗时”之间的取舍。
