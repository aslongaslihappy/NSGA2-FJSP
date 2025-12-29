import random
import time
import numpy as np
import os
from src.algorithms.selection import binary_tournament_selection
from src.algorithms.crossover import Crossover
from src.algorithms.mutation import Mutation
from src.algorithms.sorting import fast_non_dominated_sort, calculate_crowding_distance
from src.algorithms.initialization import Initialization

class ga:
    def __init__(self, generation, pop_size, cr, mu, Tmachinetime, de):
        self.generation, self.pop_size, self.cr, self.mu = generation, pop_size, cr, mu
        self.Tmachinetime = Tmachinetime
        self.de = de
        self.initialization = Initialization(de.work, Tmachinetime)
        self.crossover = Crossover(Tmachinetime)  
        self.mutation = Mutation(Tmachinetime)

    def set_time_limit(self, time_limit):
        """设置算法运行的时间限制（秒）"""
        self.time_limit = time_limit
        self.use_time_limit = True
            
    def total(self, job_length):
        population_job = np.zeros((self.pop_size, job_length), dtype=int)
        population_machine = np.zeros((self.pop_size, job_length), dtype=int)
        objectives = []  # 存储目标值

        # 记录开始时间（用于时间限制）
        start_time = time.time()

        # 初始化种群
        population_job, population_machine, objectives = self.random_init_population(job_length)

        for generation in range(1, self.generation):
            # 检查是否达到时间限制
            if hasattr(self, 'use_time_limit') and self.use_time_limit:
                current_time = time.time()
                if current_time - start_time > self.time_limit:
                    break
        
            # 创建子代
            offspring_job = np.zeros((self.pop_size, job_length), dtype=int)
            offspring_machine = np.zeros((self.pop_size, job_length), dtype=int)
            offspring_objectives = []

            # 二元锦标赛选择父代
            selected_parents = binary_tournament_selection(objectives, population_job, population_machine)

            # 交叉和变异，生成子代
            for i in range(0, self.pop_size, 2):
                parent1_job, parent1_machine = selected_parents[i]
                parent2_job, parent2_machine = selected_parents[i + 1]

                # 交叉
                if np.random.random() < self.cr:
                    parent1_job, parent2_job = self.crossover.pox(parent1_job, parent2_job)
                    parent1_machine, parent2_machine = self.crossover.ux(parent1_machine, parent2_machine)
                # 变异
                if np.random.random() < self.mu:
                    parent1_job = self.mutation.OS_mutation(parent1_job)
                    parent1_machine = self.mutation.MS_mutation(parent1_machine)
                    parent2_job  = self.mutation.OS_mutation(parent2_job)
                    parent2_machine = self.mutation.MS_mutation(parent2_machine)

                # 计算子代目标值
                offspring1_obj = self.de.caculate(parent1_job, parent1_machine)
                offspring2_obj = self.de.caculate(parent2_job, parent2_machine)

                # 保存子代
                offspring_job[i], offspring_machine[i] = parent1_job, parent1_machine
                offspring_job[i + 1], offspring_machine[i + 1] = parent2_job, parent2_machine

                offspring_objectives.append(offspring1_obj)
                offspring_objectives.append(offspring2_obj)

            # 环境选择
            population_job, population_machine, objectives = self.environment_selection(population_job, population_machine, offspring_job, offspring_machine, objectives, offspring_objectives)
            
            print('迭代次数:', generation)

        # 找出帕累托前沿
        pareto_front = fast_non_dominated_sort(objectives)[0]

        # 获取去重后的最终帕累托前沿
        final_pareto_solutions, unique_indices = self.get_final_pareto_front(objectives, pareto_front)
        best_idx = unique_indices[0]

        #选择Makespan最小的解作为最优解用于绘制甘特图
        best_job = population_job[best_idx].tolist()
        best_machine = population_machine[best_idx].tolist()
        best_individual = {'OS': best_job,'MS': best_machine}

        # 返回最终的帕累托前沿
        return final_pareto_solutions, best_individual

    def get_final_pareto_front(self, objectives, pareto_front):
        """
        获取最终的帕累托前沿，并去除重复解
        
        参数:
        objectives -- 目标值列表
        pareto_front -- 帕累托前沿索引列表
        
        返回:
        unique_solutions -- 去重后的最终帕累托前沿解列表
        unique_indices -- 去重后的最终帕累托前沿索引列表
        """
        # 去除重复的解
        unique_solutions = []
        unique_indices = []
        
        for idx in pareto_front:
            solution = objectives[idx]
            # 检查是否已经存在相同的解
            is_duplicate = False
            for existing_solution in unique_solutions:
                # 如果两个解的目标值非常接近（考虑浮点数精度），则认为是重复的
                if (abs(solution[0] - existing_solution[0]) < 1e-6 and 
                    abs(solution[1] - existing_solution[1]) < 1e-6):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_solutions.append(solution)
                unique_indices.append(idx)
        
        # 按完工时间排序
        sorted_indices = sorted(range(len(unique_solutions)), key=lambda i: unique_solutions[i][0])
        unique_solutions = [unique_solutions[i] for i in sorted_indices]
        unique_indices = [unique_indices[i] for i in sorted_indices]
        
        return unique_solutions, unique_indices
    

    def environment_selection(
        self,
        population_job,
        population_machine,
        offspring_job,
        offspring_machine,
        objectives,
        offspring_objectives,
    ):
        combined_job = np.vstack((population_job, offspring_job))
        combined_machine = np.vstack((population_machine, offspring_machine))
        combined_objectives = objectives + offspring_objectives

        fronts = fast_non_dominated_sort(combined_objectives)

        next_population_indices = []
        next_objectives = []
        next_job, next_machine = [], []

        front_index = 0
        while len(next_population_indices) + len(fronts[front_index]) <= self.pop_size:
            crowding_distances = calculate_crowding_distance(combined_objectives, fronts[front_index])

            for j in fronts[front_index]:
                next_population_indices.append(j)
                next_objectives.append(combined_objectives[j])
                next_job.append(combined_job[j])
                next_machine.append(combined_machine[j])

            front_index += 1

        if len(next_population_indices) < self.pop_size:
            crowding_distances = calculate_crowding_distance(combined_objectives, fronts[front_index])

            sorted_front = sorted(fronts[front_index], key=lambda j: -crowding_distances[j])

            for j in sorted_front[: self.pop_size - len(next_population_indices)]:
                next_population_indices.append(j)
                next_objectives.append(combined_objectives[j])
                next_job.append(combined_job[j])
                next_machine.append(combined_machine[j])

        return np.array(next_job), np.array(next_machine), next_objectives


    def random_init_population(self, job_length):
        population_job = np.zeros((self.pop_size, job_length), dtype=int)
        population_machine = np.zeros((self.pop_size, job_length), dtype=int)
        objectives = []

        for i in range(self.pop_size):
            job, machine = self.initialization.creat()
            obj = self.de.caculate(job, machine)
            population_job[i], population_machine[i] = job, machine
            objectives.append(obj)

        return population_job, population_machine, objectives