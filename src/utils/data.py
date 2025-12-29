'''
数据读取文件
'''
import re
import os

def read(da_,a):
    # 支持 .txt 和 .fjs 两种格式；优先读取 .txt，若不存在则读取 .fjs
    txt_path = f'./data/{da_}/{a}.txt'
    fjs_path = f'./data/{da_}/{a}.fjs'

    if os.path.exists(txt_path):
        with open(txt_path,'r', encoding='utf-8') as f:
            data = f.read()
        data = data.split('\n')
        work = []
        Tmachinetime = []
        i = 0
        for row in data[1:]:
            if row:
                row = re.findall(r'[0-9]+', row)
                row = [int(ro) for ro in row]
                wor = [i+1 for w in range(row[0])]        # 每一行是一个工件
                work += wor                                # 记录工序
                i += 1

                row1 = row[1:]                            # 第二个数开始提取工序加工信息
                while row1:
                    signal = row1[0]                      # 第一个数是工序的可加工机器数
                    Tmachinetime.append([])
                    for j in range(signal):               # 提取对应工序的加工机器和加工时间
                        mt = row1[2*j+1:2*j+3]
                        Tmachinetime[-1] += mt
                    row1 = row1[2*signal+1:]              # row1提取完的信息截取掉，都提完后,row1变为[],跳出循环
        return work, Tmachinetime

    elif os.path.exists(fjs_path):
        # 解析 FJS 格式（Behnke–Geiger）
        with open(fjs_path, 'r', encoding='utf-8') as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]

        # 首行头部：J、M、(可忽略的第三值)，仅使用 J
        header_nums = re.findall(r'[0-9]+(?:\.[0-9]+)?', lines[0])
        if len(header_nums) < 2:
            raise ValueError(f'FJS头部格式不正确: {lines[0]}')
        J = int(float(header_nums[0]))
        # M = int(float(header_nums[1]))  # 如需校验可使用
        # 其余头部值（如 6.08）忽略

        # 将后续行的所有整数按连续流解析
        tail = '\n'.join(lines[1:])
        nums = [int(x) for x in re.findall(r'[0-9]+', tail)]
        ptr = 0

        work = []
        Tmachinetime = []
        for job_idx in range(J):
            if ptr >= len(nums):
                raise ValueError('FJS解析越界：缺少工序数量')
            num_ops = nums[ptr]; ptr += 1

            # 记录该作业的工序数量（与现有结构一致）
            work += [job_idx + 1] * num_ops

            for _ in range(num_ops):
                if ptr >= len(nums):
                    raise ValueError('FJS解析越界：缺少候选机器数量')
                sigma = nums[ptr]; ptr += 1

                op_mt = []
                for _ in range(sigma):
                    if ptr + 1 >= len(nums):
                        raise ValueError('FJS解析越界：缺少(机器,时间)对')
                    m = nums[ptr]; t = nums[ptr + 1]; ptr += 2
                    op_mt += [m, t]
                Tmachinetime.append(op_mt)

        return work, Tmachinetime

    else:
        raise FileNotFoundError(f'未找到数据文件：{txt_path} 或 {fjs_path}')

