# NSGA2-FJSP

基于 NSGA-II 的多目标柔性车间调度（FJSP）示例代码，面向学习与研究。  
优化目标：最小化完工时间（Makespan）与总能耗（TEC）。

## 特性
- NSGA-II 选择机制（快速非支配排序 + 拥挤度距离）
- OS/MS 双层编码与对应的交叉、变异算子
- 支持按迭代次数或 CPU 时间限制停止
- 解码与甘特图绘制，输出最终 Pareto 前沿
- 批量实验脚本与结果可视化

## 环境与依赖
- Python 3.8+（建议 3.10/3.11）
- 依赖：`numpy`、`matplotlib`、`pandas`  
- 批量实验额外依赖：`tqdm`

安装示例：
```bash
pip install numpy matplotlib pandas tqdm
```

## 快速开始
```bash
python main.py
```

默认读取 `data/Brandimarte_Data/Mk01.txt`，运行结束后会：
- 控制台输出最终 Pareto 前沿与最优编码
- 在 `results/` 下保存甘特图（`gantt_chart.png` / `gantt_chart.pdf`）

## 批量实验（可选）
```bash
python "src/utils/performance _test.py"
```
说明：
- 该脚本会对多个数据集重复运行并统计结果
- 输出位于 `results/<数据源>/<数据集>/` 下，包括：
  - `all_pareto_points.csv`
  - `final_pareto_front.csv`
  - `pareto_fronts.png`
  - `combined_pareto_front.png`

## 参数配置
主要参数集中在 `main.py`：
- `da_`：数据源文件夹名，如 `Brandimarte_Data`
- `a`：具体实例名，如 `Mk01`
- `generation, popsize, cr, mu`：迭代次数、种群规模、交叉/变异概率
- `use_cpu_time_limit`：是否启用 CPU 时间限制  
  时间限制计算：`time_limit = cpu_time * N / 1000`（N 为总工序数）

能耗参数在 `src/algorithms/decode.py` 中设置：
- `processing_power`：加工功率（kW）
- `idle_power`：空闲功率（kW）

## 数据格式
支持两种数据格式：
- `*.txt`（默认优先读取）
- `*.fjs`

数据放在 `data/<数据源>/` 下，例如：
```
data/Brandimarte_Data/Mk01.txt
```

## 目录结构
```
.
├─ main.py
├─ data/
├─ results/
└─ src/
   ├─ algorithms/
   │  ├─ GA.py
   │  ├─ decode.py
   │  ├─ crossover.py
   │  ├─ mutation.py
   │  └─ ...
   └─ utils/
      ├─ data.py
      └─ performance _test.py
```
