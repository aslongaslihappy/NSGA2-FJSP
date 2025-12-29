import numpy as np

class Initialization:
    def __init__(self, work, Tmachinetime):
        self.work = work
        self.Tmachinetime = Tmachinetime

    def creat(self):
        OS = np.copy(self.work)
        np.random.shuffle(OS)
        OS = OS.tolist()
        MS = []
        
        for i in range(len(OS)):
            P = self.Tmachinetime[i]
            n_machine = [P[j] for j in range(0, len(P), 2)]
            index = np.random.randint(0, len(n_machine), 1)
            selected_machine = n_machine[index[0]]
            MS.append(selected_machine)
                
        return OS, MS