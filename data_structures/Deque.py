# 双端队列的实现Deque ['dek] double-ended queue
# 实现的方法有add_front(), add_rear(), remove_front(), remove_rear(), is_empty(), size()

class Deque:
    def __init__(self):
        self.items = []

    def add_front(self, item):
        # 在双端队列的头部添加元素，将list的前端视为队列前端
        # 时间复杂度O(n)
        self.items.insert(0, item)

    def add_rear(self, item):
        # 在Deque的尾部添加元素 rear [rɪr]
        # 时间复杂度O(1)
        self.items.append(item)

    def remove_front(self):
        # 从Deque的头部删除元素
        # 时间复杂度O(n)
        if not self.is_empty():
            return self.items.pop(0)
        else:
            return None

    def remove_rear(self):
        # 从Deque的尾部删除元素
        # 时间复杂度O(1)
        if not self.is_empty():
            return self.items.pop()
        else:
            return None

    def is_empty(self):
        # 判断Deque是否为空
        # 时间复杂度O(1)
        return len(self.items) == 0

    def size(self):
        # 返回Deque的大小
        # 时间复杂度O(1)
        return len(self.items)


if __name__ == '__main__':
    # 测试
    d = Deque()
    print(d.is_empty())
    print(d.remove_rear())
    d.add_front("hello")
    d.add_front("world")
    d.add_rear(2)
    print(d.items)
    print(d.remove_front())
    print(d.items)
    print(d.remove_rear())
    print(d.items)
    print(d.size())