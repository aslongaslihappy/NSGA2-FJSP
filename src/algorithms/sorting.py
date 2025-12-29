def fast_non_dominated_sort(objectives):
    """
    快速非支配排序
    
    Args:
        objectives: 目标函数值列表
        
    Returns:
        非支配前沿列表
    """
    n = len(objectives)
    domination_count = [0] * n  # 被支配计数
    domination_sets = [[] for _ in range(n)]  # 支配集合
    fronts = [[]]  # 非支配前沿
    
    for i in range(n):
        for j in range(n):
            if i != j:
                # 如果i支配j
                if all(objectives[i][k] <= objectives[j][k] for k in range(len(objectives[i]))) and \
                any(objectives[i][k] < objectives[j][k] for k in range(len(objectives[i]))):
                    domination_sets[i].append(j)
                # 如果j支配i
                elif all(objectives[j][k] <= objectives[i][k] for k in range(len(objectives[i]))) and \
                    any(objectives[j][k] < objectives[i][k] for k in range(len(objectives[i]))):
                    domination_count[i] += 1
        
        if domination_count[i] == 0:
            fronts[0].append(i)
    
    i = 0
    while fronts[i]:
        next_front = []
        for j in fronts[i]:
            for k in domination_sets[j]:
                domination_count[k] -= 1
                if domination_count[k] == 0:
                    next_front.append(k)
        i += 1
        fronts.append(next_front)
    
    return fronts[:-1]  # 最后一个前沿为空，不返回

def calculate_crowding_distance(objectives, front):
    """
    计算拥挤度距离
    
    Args:
        objectives: 目标函数值列表
        front: 当前前沿
        
    Returns:
        拥挤度距离字典
    """
    if len(front) <= 2:
        return {i: float('inf') for i in front}
    
    distances = {i: 0 for i in front}
    
    # 对每个目标函数计算拥挤度
    for m in range(len(objectives[0])):
        # 按目标函数m排序
        sorted_front = sorted(front, key=lambda i: objectives[i][m])
        
        # 边界点拥挤度设为无穷大
        distances[sorted_front[0]] = float('inf')
        distances[sorted_front[-1]] = float('inf')
        
        # 计算中间点的拥挤度
        f_max = objectives[sorted_front[-1]][m]
        f_min = objectives[sorted_front[0]][m]
        
        if f_max == f_min:
            continue
            
        for i in range(1, len(sorted_front) - 1):
            distances[sorted_front[i]] += (objectives[sorted_front[i+1]][m] - objectives[sorted_front[i-1]][m]) / (f_max - f_min)
    
    return distances
