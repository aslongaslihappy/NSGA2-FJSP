import numpy as np
import random

class Mutation:
    """
    变异操作类
    实现了工序编码和机器编码的变异操作
    """
    
    def __init__(self, Tmachinetime):
        """
        初始化变异操作类
        
        Args:
            Tmachinetime: 工序对应的加工情况
        """
        self.Tmachinetime = Tmachinetime
  

    def OS_mutation(self, OS):
        """
        工序编码插入变异
        
        Args:
            OS: 工序编码
            
        Returns:
            变异后的工序编码
        """
        if len(OS) <= 1:
            return OS.copy()
        
        pos1, pos2 = random.sample(range(len(OS)), 2)
        if pos1 > pos2:
            pos1, pos2 = pos2, pos1
            
        OS_copy = OS.copy()
        value = OS_copy[pos2]
        del OS_copy[pos2]
        OS_copy.insert(pos1, value)
        
        return OS_copy
        
    def MS_mutation(self, MS):
        """
        机器编码重分配变异
        
        Args:
            MS: 机器编码
            
        Returns:
            变异后的机器编码
        """
        if len(MS) == 0:
            return MS.copy()
        
        pos = random.randint(0, len(MS) - 1)
        P = self.Tmachinetime[pos]
        available_machines = [P[j] for j in range(0, len(P), 2)]  # 偶数项取加工机器号
        
        if len(available_machines) > 0:
            idx = random.randint(0, len(available_machines) - 1)
            MS_copy = MS.copy()
            MS_copy[pos] = available_machines[idx]
            return MS_copy
        
        return MS.copy()
    

