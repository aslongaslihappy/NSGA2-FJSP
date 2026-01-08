# FJSP 入门与 NSGA-II 实践：从问题到代码

这篇博客面向入门学习者，先介绍 FJSP（柔性车间调度）问题，再说明 NSGA-II 多目标进化算法，最后结合本项目代码，梳理如何完成求解与可视化。

项目代码地址：<https://github.com/aslongaslihappy/NSGA2-FJSP>

---

## 1. FJSP 是什么

FJSP（Flexible Job Shop Scheduling Problem，柔性车间调度）是经典调度问题的扩展。  
与传统车间调度不同，FJSP 允许每道工序在多台机器中选择一台进行加工，因此具有更强的灵活性，但也带来更高的搜索复杂度。

### 1.1 基本元素
- 工件（Job）：由多道工序组成
- 工序（Operation）：工件必须按顺序加工的步骤
- 机器（Machine）：每道工序可选的加工设备集合

### 1.2 典型约束
- 同一台机器同一时间只能加工一道工序
- 同一工件的工序必须遵循先后顺序

### 1.3 常见优化目标（多目标）
FJSP 通常是多目标优化问题，本项目关注两类目标：
- **Makespan（完工时间）**：所有工件完成的总时间
- **TEC（总能耗）**：加工能耗 + 机器空闲能耗

由于目标之间相互冲突，实际求解的是 **Pareto 最优解集合**，即一组“互不支配”的解。

---

## 2. NSGA-II 简介

NSGA-II（Non-dominated Sorting Genetic Algorithm II）是经典的多目标进化算法，核心思想是：
1. **非支配排序**：将解分层，第一层是最优的非支配解
2. **拥挤度距离**：衡量解在目标空间的稀疏程度，保证多样性
3. **精英保留**：父代与子代合并后再选择

### 2.1 算法流程（简述）
1. 初始化种群
2. 计算目标函数（多目标）
3. 非支配排序  + 拥挤度
4. 二元锦标赛选择
5. 交叉、变异产生子代
6. 环境选择得到新种群
7. 重复迭代，得到 Pareto 前沿

---

## 3. 本项目如何解决 FJSP

项目实现了 NSGA-II + FJSP 的完整流程，关键模块如下：

```
main.py
src/
  algorithms/
    GA.py
    decode.py
    initialization.py
    selection.py
    crossover.py
    mutation.py
    sorting.py
  utils/
    data.py
    performance _test.py
```

下面按求解流程梳理代码思路。

---

### 3.1 数据读取（src/utils/data.py）
`data.py` 支持两种格式：
- `*.txt`（优先读取）
- `*.fjs`

读取结果返回：
- `work`：记录每个工序属于哪个工件
- `Tmachinetime`：每道工序的可选机器与加工时间

这为后续编码、解码提供基础数据。

---

### 3.2 编码设计（OS/MS 双层编码）
项目使用经典的 **OS/MS 双层编码**：
- **OS（Operation Sequence）**：全局工序加工顺序
- **MS（Machine Selection）**：每道工序选择哪台机器

这样可以同时表达“工序顺序”和“机器选择”两个维度，适合 FJSP 的可行解表示。

---

### 3.3 初始化、交叉与变异
主要在 `src/algorithms/initialization.py`、`crossover.py`、`mutation.py` 中完成：
- 初始化生成随机可行的 OS/MS
- 交叉算子：例如 POX、UX
- 变异算子：改变工序顺序或机器选择

这些操作负责探索更广的解空间。

---

### 3.4 目标函数与解码（src/algorithms/decode.py）
解码模块负责把 OS/MS 转换为可执行调度，并计算目标函数：
1. **根据工件顺序和机器资源安排开始/结束时间**
2. **计算 Makespan**
3. **计算 TEC（加工能耗 + 空闲能耗）**
4. 可选绘制甘特图并保存结果

关键输出是一个形如 `[C_max, TEC]` 的目标向量。

---

### 3.5 NSGA-II 主流程（src/algorithms/GA.py）
`GA.py` 是核心：
- **binary_tournament_selection**：二元锦标赛选择
- **fast_non_dominated_sort**：非支配排序
- **calculate_crowding_distance**：拥挤度距离
- **environment_selection**：环境选择保留精英

主循环：
1. 初始化种群
2. 交叉与变异生成子代
3. 计算子代目标函数
4. 合并父代与子代，进行非支配排序
5. 用拥挤度距离选择下一代

最终输出：
- Pareto 前沿解集
- 最佳个体（用于甘特图绘制）

---

### 3.6 主入口（main.py）
`main.py` 负责串联所有模块：
1. 读取数据
2. 初始化解码器与 GA
3. 设置迭代次数或 CPU 时间限制
4. 调用 `ga.total()` 得到结果
5. 输出 Pareto 前沿并绘制甘特图

---

## 4. 结果与可视化
项目输出主要包括：
- **甘特图**：展示具体调度方案
- **Pareto 前沿图**：展示多目标权衡结果

这些图像被保存在 `results/` 目录下，适合用于论文或实验报告。

---

## 5. 小结
本项目的实现路径是：
**数据读取 → OS/MS 编码 → NSGA-II 进化 → 解码与多目标计算 → 可视化输出**。

对入门者来说，建议阅读顺序：
1. `main.py`（了解整体流程）
2. `GA.py`（理解 NSGA-II 主循环）
3. `decode.py`（理解目标函数与调度解码）

如果想进一步提升效果，可尝试：
- 引入局部搜索（如 VNS）
- 自适应交叉与变异概率
- 更真实的能耗模型

---

如果你也在做调度或多目标优化，希望这份项目能帮你快速入门并搭建自己的实验框架。
