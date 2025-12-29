import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.pylab import mpl
import matplotlib.patches as patches
from datetime import datetime
import os
mpl.rcParams['font.sans-serif'] = ['SimHei'] 

class decode:
    def __init__(self, work, Tmachinetime):
        self.work = work
        self.Tmachinetime = Tmachinetime
        '''
        Tmachinetime = [
            [machine1, time1, machine2, time2, ...],  # 工序0的可选机器和对应加工时间
            [machine1, time1, machine2, time2, ...],  # 工序1的可选机器和对应加工时间
            [machine1, time1, machine2, time2, ...],  # 工序2的可选机器和对应加工时间
            ...
        ]
        '''

    def caculate(self, OS, MS, draw_gantt=False):
        job_num, machine_num = max(OS), max(MS)
        t_job = np.zeros((1, job_num), dtype=int)
        t_mac = np.zeros((1, machine_num), dtype=int)
        
        # 甘特图数据收集
        gantt_data = {
            'machines': []      # 机器加工任务
        }
        
        # 能耗计算相关变量
        machine_processing_energy = np.zeros(machine_num)  # 机器加工能耗
        machine_processing_time = np.zeros(machine_num)    # 每台机器的总加工时间
        
        # 能耗参数（可根据实际情况调整）
        processing_power = 30.0  # 加工功率 kW
        idle_power = 1.0         # 空闲功率 kW
        
        startime = 0
        count = np.zeros((1, job_num), dtype=int)

        for i in range(len(OS)):
            jo = OS[i] - 1
            idx = self.work.index(jo + 1) + count[0, jo]
            ma = MS[idx]
            
            # 经典FJSP：机器开始时间 = max(工件完成时间, 机器可用时间)
            startime = max(t_mac[0, ma-1], t_job[0, jo])
            
            # 从Tmachinetime中查找对应的加工时间
            processing_time = self.get_processing_time(idx, ma)
            gantt_data['machines'].append({
                'machine_id': ma,
                'start_time': startime,
                'end_time': startime + processing_time,
                'job_id': jo + 1,
                'operation': count[0, jo] + 1,
                'processing_time': processing_time
            })
            
            # 计算机器加工能耗
            machine_processing_energy[ma-1] += processing_time * processing_power
            # 累计该机器的总加工时长（用于计算空闲能耗）
            machine_processing_time[ma-1] += processing_time
            
            t_mac[0, ma-1] = startime + processing_time
            t_job[0, jo] = startime + processing_time
            count[0, jo] += 1

        C_max = max(t_job[0])
        
        # 按公式逐机器计算空闲能耗
        machine_idle_energy = np.zeros(machine_num)
        for k in range(machine_num):
            idle_time_k = C_max - machine_processing_time[k]
            machine_idle_energy[k] = idle_power * idle_time_k

        TEC = np.sum(machine_processing_energy) + np.sum(machine_idle_energy)

        # 绘制甘特图
        if draw_gantt:
            self.draw_gantt_chart(gantt_data, C_max, job_num, machine_num)

        return [C_max, TEC]


    def get_processing_time(self, operation_idx, machine_id):
        """
        根据工序索引和机器ID从Tmachinetime中查找对应的加工时间
        
        Args:
            operation_idx: 工序在Tmachinetime中的索引
            machine_id: 机器ID
            
        Returns:
            processing_time: 对应的加工时间
        """
        if operation_idx < len(self.Tmachinetime):
            machine_time_pairs = self.Tmachinetime[operation_idx]
            # Tmachinetime格式：[machine1, time1, machine2, time2, ...]
            for i in range(0, len(machine_time_pairs), 2):
                if i + 1 < len(machine_time_pairs) and machine_time_pairs[i] == machine_id:
                    return machine_time_pairs[i + 1]
        
        # 如果没找到，返回默认值（这种情况不应该发生）
        print(f"Warning: No processing time found for operation {operation_idx} on MS {machine_id}")
        return 1

    def draw_gantt_chart(self, gantt_data, C_max, job_num, machine_num):
        """绘制现代化风格的甘特图，显示完成时间"""
        
        # 设置现代化的matplotlib参数
        plt.style.use('default')
        plt.rcParams.update({
            'font.family': ['Arial', 'sans-serif'],
            'font.size': 11,
            'font.weight': 'normal',
            'axes.linewidth': 1.2,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'axes.grid': True,
            'grid.alpha': 0.3,
            'grid.linewidth': 0.8,
            'xtick.major.size': 6,
            'ytick.major.size': 6,
            'xtick.minor.size': 3,
            'ytick.minor.size': 3,
            'legend.frameon': True,
            'legend.fancybox': True,
            'legend.shadow': True
        })
        
        # 创建图形和子图
        fig, ax = plt.subplots(figsize=(16, 8))
        fig.patch.set_facecolor('white')
        
        # 设置标题，包含完成时间信息
        fig.suptitle(f'Production Scheduling Gantt Chart', 
                    fontsize=16, fontweight='bold', y=0.95)
        
        # 使用您提供的新鲜颜色配置
        fresh_colors = [
            '#fbb4ae',  # Light Pink
            '#ffd9a8',  # Light Orange
            '#b3cde4',  # Light Blue
            '#cceac4',  # Light Green
            '#decae5',  # Light Purple
            '#66c2a5',  # Teal
            '#FFB6C1',  # Light Pink
            '#98FB98',  # Pale Green
            '#87CEEB',  # Sky Blue
            '#DDA0DD',  # Plum
            '#F0E68C',  # Khaki
            '#FFA07A',  # Light Salmon
            '#20B2AA',  # Light Sea Green
            '#FFE4B5',  # Moccasin
            '#D3D3D3',  # Light Gray
            '#F5DEB3'   # Wheat
        ]
        
        # 确保有足够的颜色
        if job_num > len(fresh_colors):
            import matplotlib.cm as cm
            additional_colors = cm.Set3(np.linspace(0, 1, job_num - len(fresh_colors)))
            job_colors = fresh_colors + [cm.colors.to_hex(c) for c in additional_colors]
        else:
            job_colors = fresh_colors[:job_num]
        
        # 计算布局参数 - 只考虑机器
        total_machines = machine_num
        
        # Y轴位置分配 - 只有机器
        y_positions = {}
        bar_height = 0.8
        
        # 机器区域
        machine_y_positions = {}
        for i in range(1, total_machines + 1):
            machine_y_positions[i] = i - 1
            y_positions[f'M {i}'] = i - 1
        
        total_height = total_machines
        
        # X轴范围
        x_max = C_max * 1.1
        
        # 绘制机器加工任务
        for task in gantt_data.get('machines', []):
            machine_id = task['machine_id']
            start_time = task['start_time']
            duration = task['end_time'] - task['start_time']
            job_id = task['job_id']
            operation = task['operation']
            
            if machine_id in machine_y_positions:
                y_pos = machine_y_positions[machine_id]
                color = job_colors[(job_id - 1) % len(job_colors)]
                
                # 主矩形
                rect = patches.Rectangle(
                    (start_time, y_pos - bar_height/2), duration, bar_height,
                    facecolor=color, alpha=0.9, edgecolor='black', linewidth=2,
                    linestyle='-'
                )
                ax.add_patch(rect)
                
                # 添加标签
                if duration > x_max * 0.02:
                    ax.text(start_time + duration/2, y_pos, f'J{job_id}O{operation}',
                        ha='center', va='center', fontsize=10, fontweight='bold',
                        color='black')
        
        # 添加完成时间的垂直线
        ax.axvline(x=C_max, color='red', linestyle='--', linewidth=2, alpha=0.8, label=f'Makespan: {C_max:.2f}')
        
        # 在完成时间线上添加标注
        ax.text(C_max, total_height * 0.9, f'C_max = {C_max:.2f}', 
                rotation=90, ha='right', va='top', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # 设置坐标轴
        ax.set_xlim(0, x_max)
        ax.set_ylim(-1, total_height + 0.4)
        ax.set_xlabel('Time', fontsize=13, fontweight='bold')
        ax.set_ylabel('Resources', fontsize=13, fontweight='bold')
        
        # 设置Y轴标签
        y_labels = []
        y_ticks = []
        for label, pos in sorted(y_positions.items(), key=lambda x: x[1]):
            y_labels.append(label)
            y_ticks.append(pos)
        
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, fontsize=11)
        
        # 在简化的FJSP模型中，只有机器，不需要分隔线
        
        # 创建现代化图例
        legend_elements = []
        
        # 工件图例
        for i in range(job_num):
            legend_elements.append(patches.Patch(color=job_colors[i], 
                                            label=f'Job {i+1}'))
        
        # 设置网格
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        # 调整布局
        plt.tight_layout()
        plt.subplots_adjust(right=0.75, top=0.88)  # 调整右边距和顶部边距
        
        # 保存图片（固定文件名，覆盖旧图片）
        filename = 'gantt_chart.png'
        
        # 确保results目录存在
        results_dir = 'results'
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        filepath = os.path.join(results_dir, filename)
        plt.savefig(filepath, dpi=600, bbox_inches='tight', facecolor='white',
                edgecolor='none', format='png')
        print(f"现代化甘特图已保存至: {filepath}")
        print(f"总完成时间 (C_max): {C_max:.2f}")
        
        # 同时保存PDF版本
        pdf_filepath = filepath.replace('.png', '.pdf')
        plt.savefig(pdf_filepath, bbox_inches='tight', facecolor='white',
                edgecolor='none', format='pdf')
        print(f"PDF版本已保存至: {pdf_filepath}")
        
        # 显示图片
        plt.show()
        
        return filepath
