import numpy as np
import matplotlib.pyplot as plt
import time
import os
import pandas as pd
from tqdm import tqdm
import random
from matplotlib.font_manager import FontProperties
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.algorithms.decode import decode
import src.utils.data as da
from src.algorithms.GA import ga

# 确保结果可重现
np.random.seed(42)
random.seed(42)

class NSGAParetoTester:
    def __init__(self, generation=200, popsize=50, cr=0.8, mu=0.2):
        """初始化NSGA帕累托前沿测试器"""
        self.generation = generation
        self.popsize = popsize
        self.cr = cr
        self.mu = mu
        
        # 创建结果目录
        self.results_dir = "results"
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

            
        # 设置中文字体
        self.font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
        plt.rcParams['axes.unicode_minus'] = False
        
        # 添加CPU时间停止条件参数
        self.use_cpu_time_limit = False
        self.cpu_time_options = [100, 200, 300, 500]  # 预定义的CPU时间选项(秒)
        self.selected_cpu_time = 100  # 默认使用100秒
    
    def set_cpu_time_limit(self, use_limit=True, cpu_time=100):
        """设置是否使用CPU时间限制以及限制时间"""
        self.use_cpu_time_limit = use_limit
        if cpu_time in self.cpu_time_options:
            self.selected_cpu_time = cpu_time
        else:
            print(f"警告: 指定的CPU时间 {cpu_time} 不在预定义选项中，使用默认值 {self.selected_cpu_time}")
    
    def run_test(self, datasets, num_runs=10):
        """运行性能测试"""
        print("开始NSGA帕累托前沿测试...")
        
        # 存储所有结果
        all_results = []
        dataset_summary = []
        
        # 遍历每个数据集
        for dataset in datasets:
            print(f"\n处理数据集: {dataset['name']}")
            
            # 创建数据来源目录
            data_source_dir = os.path.join(self.results_dir, dataset['da'])
            if not os.path.exists(data_source_dir):
                os.makedirs(data_source_dir)
            
            # 为当前数据集创建结果目录，使用数据集名称和数据来源
            dataset_folder_name = f"{dataset['name']}"
            dataset_dir = os.path.join(data_source_dir, dataset_folder_name)
            if not os.path.exists(dataset_dir):
                os.makedirs(dataset_dir)
            
            # 存储当前数据集的结果
            dataset_results = []
            all_pareto_fronts = []
            
            # 运行多次实验
            for run in tqdm(range(num_runs), desc="运行实验"):
                # 运行算法并记录结果
                result = self.run_single_test(dataset, run)
                dataset_results.append(result)
                all_results.append(result)
                
                # 收集帕累托前沿
                if 'pareto_front' in result and result['pareto_front'] is not None:
                    all_pareto_fronts.append(result['pareto_front'])
            
            # 保存当前数据集的帕累托前沿
            self.save_pareto_fronts(all_pareto_fronts, dataset_dir)
            
            # 绘制帕累托前沿图
            self.plot_pareto_fronts(all_pareto_fronts, dataset_dir, dataset['name'])
            
            # 计算并保存当前数据集的统计结果
            stats = self.calculate_statistics(dataset_results)
            stats['数据集'] = dataset['name']
            stats['数据来源'] = dataset['da']
            dataset_summary.append(stats)
        
        print(f"\nNSGA帕累托前沿测试完成！结果已保存到 {self.results_dir} 目录")
        
        return all_results, dataset_summary

    def run_single_test(self, dataset, run_id):
        """运行单次测试"""
        # 加载数据
        work, Tmachinetime = da.read(dataset['da'], dataset['name'])

        # 初始化解码器（修正构造函数参数）
        de = decode(work, Tmachinetime)
        
        # 记录开始时间
        start_time = time.time()
        
        # 初始化GA算法（修正构造函数参数）
        ga_algo = ga(self.generation, self.popsize, self.cr, self.mu, Tmachinetime, de)

        # 计算CPU时间限制（如果启用）
        if self.use_cpu_time_limit:
            # 计算总操作数 N
            total_operations = len(work)
            # 设置时间限制为 CPUtime × N
            time_limit = (self.selected_cpu_time * total_operations)/1000.0
            # 设置算法的时间限制
            ga_algo.set_time_limit(time_limit)
        
        # 运行算法（修正调用方式和返回值）
        pareto_front, best_code = ga_algo.total(len(work))
        
        # 记录结束时间
        end_time = time.time()
        runtime = end_time - start_time
        
        return {
            "数据集": dataset['name'],
            "运行ID": run_id + 1,
            "pareto_front": pareto_front,
            "运行时间": runtime,
            "作业数": len(work),
            "机器数": max([max(p[::2]) for p in Tmachinetime]) if Tmachinetime else 0,
            "停止条件": "CPU时间限制" if self.use_cpu_time_limit else "迭代次数"
        }
    
    def calculate_statistics(self, results):
        """计算统计结果"""
        runtimes = [r['运行时间'] for r in results]
        
        return {
            "平均运行时间": np.mean(runtimes),
            "最短运行时间": min(runtimes),
            "最长运行时间": max(runtimes)
        }
    
    def save_pareto_fronts(self, pareto_fronts, dataset_dir):
        """保存帕累托前沿"""
        # 不再为每次运行创建单独的CSV文件
        # 而是创建一个包含所有运行结果的CSV文件，并标注运行ID
        
        if pareto_fronts:
            all_points = []
            
            # 收集所有运行的帕累托前沿点，并标记运行ID
            for run_id, front in enumerate(pareto_fronts):
                if front is not None and len(front) > 0:
                    # 为每个点添加运行ID
                    for point in front:
                        # 创建包含运行ID的点
                        point_with_id = [run_id + 1, point[0], point[1]]
                        all_points.append(point_with_id)
            
            if all_points:
                # 转换为DataFrame并保存所有点
                all_df = pd.DataFrame(all_points, columns=["运行ID", "目标1_完工时间", "目标2_能量消耗"])
                all_df.to_csv(os.path.join(dataset_dir, "all_pareto_points.csv"), index=False)
                print(f"已保存所有帕累托前沿点，共{len(all_points)}个点")
                
                # 计算并保存最终的非支配解集合（真实帕累托前沿）
                # 注意：计算非支配解时只考虑目标值，不考虑运行ID
                points_for_non_dominated = [[p[1], p[2]] for p in all_points]
                final_pareto_front = self.get_non_dominated(points_for_non_dominated)
                
                if final_pareto_front:
                    # 为最终帕累托前沿添加一个标识列
                    final_points_with_id = []
                    for point in final_pareto_front:
                        # 查找该点来自哪次运行
                        for original_point in all_points:
                            if original_point[1] == point[0] and original_point[2] == point[1]:
                                # 添加运行ID和标识为最终帕累托前沿
                                final_points_with_id.append([original_point[0], point[0], point[1], True])
                                break
                    
                    final_df = pd.DataFrame(final_points_with_id, 
                                        columns=["运行ID", "目标1_完工时间", "目标2_能量消耗", "是否为最终帕累托解"])
                    # 按照目标1（完工时间）排序
                    final_df = final_df.sort_values(by=["目标1_完工时间"])
                    final_df.to_csv(os.path.join(dataset_dir, "final_pareto_front.csv"), index=False)
                    print(f"已保存最终帕累托前沿，共{len(final_pareto_front)}个非支配解")
    
    def plot_pareto_fronts(self, pareto_fronts, dataset_dir, dataset_name):
        """绘制帕累托前沿图"""
        plt.figure(figsize=(12, 8))
        
        # 绘制每次运行的帕累托前沿
        for i, front in enumerate(pareto_fronts):
            if front is not None and len(front) > 0:
                front_array = np.array(front)
                plt.scatter(front_array[:, 0], front_array[:, 1], label=f"运行 {i+1}", alpha=0.6, s=30)
        
        plt.title(f"{dataset_name} - 帕累托前沿", fontproperties=self.font)
        plt.xlabel("目标1: 完工时间", fontproperties=self.font)
        plt.ylabel("目标2: 能量消耗", fontproperties=self.font)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(dataset_dir, "pareto_fronts.png"))
        plt.close()
        
        # 绘制所有运行的合并帕累托前沿
        plt.figure(figsize=(12, 8))
        all_points = []
        for front in pareto_fronts:
            if front is not None and len(front) > 0:
                all_points.extend(front)
        
        if all_points:
            all_points_array = np.array(all_points)
            plt.scatter(all_points_array[:, 0], all_points_array[:, 1], color='blue', alpha=0.6, s=30)
            
            # 计算非支配解集合（真实帕累托前沿）
            non_dominated = self.get_non_dominated(all_points)
            non_dominated_array = np.array(non_dominated)
            plt.scatter(non_dominated_array[:, 0], non_dominated_array[:, 1], color='red', s=50, 
                        label="非支配解集合")
            
            # 连接非支配解集合中的点
            sorted_indices = np.argsort(non_dominated_array[:, 0])
            sorted_non_dominated = non_dominated_array[sorted_indices]
            plt.plot(sorted_non_dominated[:, 0], sorted_non_dominated[:, 1], 'r--', linewidth=2)
        
        plt.title(f"{dataset_name} - 合并帕累托前沿", fontproperties=self.font)
        plt.xlabel("目标1: 完工时间", fontproperties=self.font)
        plt.ylabel("目标2: 能量消耗", fontproperties=self.font)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(prop=self.font)
        plt.tight_layout()
        plt.savefig(os.path.join(dataset_dir, "combined_pareto_front.png"))
        plt.close()
    
    def get_non_dominated(self, points):
        """计算非支配解集合（真实帕累托前沿）"""
        if not points:
            return []
        
        points_array = np.array(points)
        non_dominated = []
        
        for i, point in enumerate(points_array):
            dominated = False
            for other_point in points_array:
                # 检查other_point是否支配point
                if (other_point[0] <= point[0] and other_point[1] <= point[1] and 
                    (other_point[0] < point[0] or other_point[1] < point[1])):
                    dominated = True
                    break
            
            if not dominated:
                non_dominated.append(point)
        
        return non_dominated
    

def main():
    """主函数"""
    # 实验参数
    generation = 2000
    popsize = 50
    cr = 0.9    
    mu = 0.15
    num_runs = 2  # 每个数据集运行20次
    
    # 数据集参数
    datasets = [
        {'name': 'Mk01', 'da': 'Brandimarte_Data'},
        {'name': 'Mk02', 'da': 'Brandimarte_Data'},
        # {'name': 'Mk03', 'da': 'Brandimarte_Data'},
        # {'name': 'Mk04', 'da': 'Brandimarte_Data'},
        # {'name': 'Mk05', 'da': 'Brandimarte_Data'},
        # {'name': 'Mk06', 'da': 'Brandimarte_Data'}, 
        # {'name': 'Mk07', 'da': 'Brandimarte_Data'},
        # {'name': 'Mk08', 'da': 'Brandimarte_Data'},
        # {'name': 'Mk09', 'da': 'Brandimarte_Data'},
        # {'name': 'Mk10', 'da': 'Brandimarte_Data'},

    ]
    
    # 创建NSGA帕累托前沿测试器
    tester = NSGAParetoTester(generation, popsize, cr, mu)
    
    # 设置是否使用CPU时间限制
    use_cpu_time = True  # 设置为True启用CPU时间限制，False使用迭代次数
    cpu_time = 100  # 选择100, 200, 300或500秒
    
    if use_cpu_time:
        tester.set_cpu_time_limit(True, cpu_time)
        print(f"使用CPU时间限制: {cpu_time}秒 × 操作数")
    else:
        print(f"使用固定迭代次数: {generation}代")
    
    # 运行测试
    tester.run_test(datasets, num_runs)

if __name__ == "__main__":
    main()

