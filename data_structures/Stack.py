# 实现栈：栈是一种线性数据结构，其特点是先进后出（Last In First Out，LIFO）。
# 栈的操作有入栈（push）、出栈（pop）、查看栈顶元素（peek）、判断栈是否为空（isEmpty）、获取栈的大小（size）。

class Stack:
    def __init__(self):
        # 栈的底层实现用列表来实现
        self.items = []

    def push(self, item):
        # 向栈顶添加元素
        # 时间复杂度O(1)
        self.items.append(item)

    def pop(self):
        # 弹出栈顶元素
        # 时间复杂度O(1)
        return self.items.pop()

    def peek(self):
        # 查看栈顶元素
        # 时间复杂度O(1)
        return self.items[-1]

    def isEmpty(self):
        # 判断栈是否为空
        # 时间复杂度O(1)
        return len(self.items) == 0

    def size(self):
        # 获取栈的大小
        # 时间复杂度O(1)
        return len(self.items)


if __name__ == '__main__':
    # 测试栈及其方法
    # 创建栈
    stack = Stack()
    # 入栈
    stack.push(1)
    stack.push(2)
    stack.push(3)
    # 直接打印是看不到栈里面的元素的
    print(stack)
    # 出栈
    print(stack.pop())
    # 查看栈顶元素
    print(stack.peek())
    # 判断栈是否为空
    print(stack.isEmpty())
    # 获取栈的大小
    print(stack.size())
