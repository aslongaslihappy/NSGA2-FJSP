import numpy as np
import random

def binary_tournament_selection(objectives, population_job, population_machine):
    """
    二元锦标赛选择
    
    Args:
        objectives: 目标函数值列表
        population_job: 工序编码种群
        population_machine: 机器编码种群
        population_time: 时间编码种群
        
    Returns:
        选择的父代列表
    """
    pop_size = len(objectives)
    selected_parents = []
    
    for _ in range(pop_size):
        # 随机选择两个个体
        idx1, idx2 = random.sample(range(pop_size), 2)
        
        # 比较两个个体的非支配关系
        if dominates(objectives[idx1], objectives[idx2]):
            winner = idx1
        elif dominates(objectives[idx2], objectives[idx1]):
            winner = idx2
        else:
            # 如果两个个体互不支配，随机选择一个
            winner = random.choice([idx1, idx2])
        
        # 添加获胜者到选择列表
        selected_parents.append((
            population_job[winner].tolist(),
            population_machine[winner].tolist()
        ))
    
    return selected_parents

def dominates(obj1, obj2):
    """
    判断obj1是否支配obj2
    
    Args:
        obj1: 第一个目标函数值
        obj2: 第二个目标函数值
        
    Returns:
        如果obj1支配obj2返回True，否则返回False
    """
    return (all(o1 <= o2 for o1, o2 in zip(obj1, obj2)) and 
            any(o1 < o2 for o1, o2 in zip(obj1, obj2)))