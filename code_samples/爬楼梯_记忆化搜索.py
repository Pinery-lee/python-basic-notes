# 一次能爬1阶或者2阶，输入n阶，输出爬楼梯的总步数。
# 暴力搜索的时间复杂度是O(2^n)
# 但是其中有很多子问题被重复计算
# 通过一个额外的数组，记录已经计算过的子问题的解，将极大的减少计算量

# 直接将时间复杂度优化到了O(n)，巨大的飞跃
# 但是空间复杂度还是O(n)

def dfs(n, memory):
    """带记忆的深度优先搜索"""
    # 基础情况
    if n == 2 or n == 1:
        return n
    # 记忆化搜索
    # 如果没有记忆过
    if memory[n] == -1:
        # 计算子问题的解
        count = dfs(n-1, memory) + dfs(n-2, memory)
        # 记忆
        memory[n] = count
        return count
    # 如果记忆过
    else:
        return memory[n]


if __name__ == '__main__':
    n = 100
    # 初始化一个数组，索引是爬的楼梯数，值是步数，初始值设为-1，表示还没有计算过
    memory = [-1] * (n+1)  # 能存从0-n阶的步数
    print(dfs(n, memory))