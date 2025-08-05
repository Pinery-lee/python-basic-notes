# 通过回溯来穷举所有可能性。具体来说，将爬楼梯想象为一个多轮选择的过程：
# 从地面出发，每轮选择上 1 阶或 2 阶，每当到达楼梯顶部时就将方案数量加1，
# 当越过楼梯顶部时就将其剪枝。
# 在回溯算法中，我们需要在整个递归过程中共享一个状态来记录所有可能的方案数量。如果使用一个整数变量 res，每次递归调用都会尝试修改这个整数，但由于整数的不可变性，这种修改不会在递归调用之间持久化。
# 通过将整数放在一个单元素列表 res[0] 中，我们可以在递归调用之间共享和修改这个状态。因为列表本身是可变的，对列表元素的修改会反映在所有递归层级中。

def backtrack(choices: list[int], state: int, n: int, res: list[int]) -> None:
    """回溯"""
    # 当爬到第 n 阶时，方案数量加 1
    if state == n:
        res[0] += 1
        return
    # 遍历每种选择
    for choice in choices:
        # 剪枝：不允许越过第 n 阶
        if state + choice > n:
            continue
        # 尝试：做出选择，更新状态
        backtrack(choices, state + choice, n, res)


# """Driver Code"""
if __name__ == "__main__":
    choices = [1, 2]  # 可选择向上爬 1 阶或 2 阶
    state = 0  # 从第 0 阶开始爬
    res = [0]  # 使用 res[0] 记录方案数量
    n = 25  # 爬到第 5 阶
    backtrack(choices, state, n, res)
    print(f"爬 {n} 阶楼共有 {res[0]} 种方案")
