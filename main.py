from src.algorithms.decode import decode
import src.utils.data as da
from src.algorithms.GA import ga
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  # 新增导入
from datetime import datetime  # 新增导入
# 设置是否使用CPU时间限制
use_cpu_time_limit = True  # 设置为True启用CPU时间限制，False使用迭代次数
cpu_time = 100# 选择CPU时间限制(秒)，可选值如：100, 200, 300, 500

da_ = 'Brandimarte_Data'           # 数据案例

if da_== 'Brandimarte_Data':
    a = 'Mk01'                  # 第一个数据案例，生产情况表01到09，

work, Tmachinetime = da.read(da_,a) # 生产情况
de = decode(work, Tmachinetime) # 解码模块

generation, popsize, cr, mu = 2000, 50, 0.8, 0.15      # 迭代次数，种群规模，交叉概率，变异概率
h = ga(generation, popsize, cr, mu,Tmachinetime,de)
# 设置CPU时间限制
if use_cpu_time_limit:
    # 计算总操作数 N
    total_operations = len(work)
    # 设置时间限制为 CPUtime × N
    time_limit = (cpu_time * total_operations)/1000.0
    # 设置算法的时间限制
    h.set_time_limit(time_limit)
    print(f"使用CPU时间限制: {cpu_time}秒 × 操作数 = {time_limit:.2f}秒")
else:
    print(f"使用固定迭代次数: {generation}代")

final_pareto_solutions, best_code = h.total(len(work))

# 输出最终帕累托前沿
print("最终帕累托前沿(完工时间, 能量消耗):")
for i, (c_finish, tec) in enumerate(final_pareto_solutions, start=1):
    print(f"解 {i}: 完工时间 = {c_finish:.2f}, 能量消耗 = {tec:.2f}")

# 输出最优解
print("最优解编码:")
print("{")
for key, value in best_code.items():
    print(f"'{key}': {value},")
print("}")

# 执行最优解的解码计算
print("\n执行最优解解码计算...")
result = de.caculate(
    best_code['OS'], 
    best_code['MS'], 
    True  # 设置为True以绘制甘特图
)


