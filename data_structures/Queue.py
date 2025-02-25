# 使用list实现队列 Queue: 先进先出
# 实现的方法有：进入队列enqueue(), 离开队列dequeue(), 队列是否为空is_empty(), 队列大小size()

class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        # 入队, 将list尾部当做队列尾部,入队从队列尾部开始
        # 时间复杂度O(1)
        self.items.append(item)

    def dequeue(self):
        # 出队，返回list头部元素
        # 时间复杂度O(n)
        if not self.is_empty():
            return self.items.pop(0)
        else:
            return None

    def is_empty(self):
        # 队列是否为空
        # 时间复杂度O(1)
        return len(self.items) == 0

    def size(self):
        # 队列大小
        # 时间复杂度O(1)
        return len(self.items)


if __name__ == '__main__':
    # 测试
    q = Queue()
    q.enqueue("hello")
    q.enqueue("2")
    q.enqueue(234)
    print(q.items)
    print(q.dequeue())
    print(q.items)
    print(q.size())
    print(q.is_empty())