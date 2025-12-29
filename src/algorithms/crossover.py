import numpy as np
import random

class Crossover:
    """
    交叉操作类
    实现了工序编码、机器编码和AGV编码的交叉操作
    """
    
    def __init__(self, Tmachinetime):
        """
        初始化交叉操作类
        
        Args:
            Tmachinetime: 工序对应的加工情况
        """
        self.Tmachinetime = Tmachinetime
    
    def pox(self, parent1, parent2):
        """
        部分顺序交叉(Precedence Operation Crossover)
        
        Args:
            parent1: 第一个父代的工序编码
            parent2: 第二个父代的工序编码
            
        Returns:
            交叉后的两个子代工序编码
        """
        job_list = list(set(parent1))                      # 工序编码去重得到工件
        split_index = np.random.randint(0, len(job_list), 1)[0]  # 随机生成位置切分工件为两个集合
        job_set1 = job_list[:split_index+1]                # 集合1
        job_set2 = job_list[split_index+1:]                # 集合2

        offspring1, offspring2 = [], []
        genes_to_fill1, genes_to_fill2 = [], []
        for i in range(len(parent1)):
            gene1 = parent1[i]
            gene2 = parent2[i]
            if gene1 in job_set1:                  # 如果parent1的基因gene1属于集合1
                offspring1.append(gene1)           # 子代offspring1记录基因，即对应位置基因保存不变
            else:                                  # 如果parent1的基因gene1不属于集合1，即属于集合2
                genes_to_fill2.append(gene1)       # genes_to_fill2记录不变的基因，用于填充后续parent2子代offspring2
                offspring1.append(-1)              # 子代offspring1记录为-1，后续用genes_to_fill1填
            if gene2 in job_set1:                  # 如果parent2的基因gene2属于集合1
                offspring2.append(gene2)           # 子代offspring2记录基因，即对应位置基因保存不变
            else:                                  # 如果parent2的基因gene2不属于集合1，即属于集合2
                genes_to_fill1.append(gene2)       # genes_to_fill1记录不变的基因，用于填充后续parent1子代offspring1
                offspring2.append(-1)              # 子代offspring2记录为-1，后续用genes_to_fill2填

        for j in range(len(parent1)):
            gene1 = offspring1[j]
            gene2 = offspring2[j]
            if gene1 == -1:                        # 如果parent1的子代offspring1基因为-1
                offspring1[j] = genes_to_fill1[0]  # 用genes_to_fill1的第一个基因填
                del genes_to_fill1[0]              # 填完删除
            if gene2 == -1:                        # 如果parent2的子代offspring2基因为-1          
                offspring2[j] = genes_to_fill2[0]  # 用genes_to_fill2的第一个基因填
                del genes_to_fill2[0]              # 填完删除
        return offspring1, offspring2
    
    def ux(self, parent1_machine, parent2_machine):
        """
        机器编码的均匀交叉(Uniform Crossover)
        
        Args:
            parent1_machine: 第一个父代的机器编码
            parent2_machine: 第二个父代的机器编码
            
        Returns:
            交叉后的两个子代的机器编码
        """
        child1_machine = parent1_machine.copy()
        child2_machine = parent2_machine.copy()
        
        # 生成随机二进制掩码
        mask = [random.randint(0, 1) for _ in range(len(parent1_machine))]
        
        # 根据掩码交换基因
        for i in range(len(parent1_machine)):
            if mask[i] == 1:  # 如果掩码为1，交换两个父代在该位置的基因
                child1_machine[i], child2_machine[i] = child2_machine[i], child1_machine[i]
        
        return child1_machine, child2_machine
    
    


    