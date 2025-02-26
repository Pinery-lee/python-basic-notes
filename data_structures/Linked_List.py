# 无序列表包含无序数组和链表，无序数组和链表的区别在于无序数组是连续存储的，而链表是分散存储在内存中的
# 需要实现无序链表的判断是否为空is_empty(), 添加add(), 遍历print(), 插入insert(), 搜索search(), 删除remove(),  获取长度len(), 清空clear()等操作

# 首先需要定义一个Node类，用于构造链表
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None  # 将节点接地

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_next(self):
        return self.next

    def set_next(self, next_element):
        self.next = next_element


# 然后定义一个无序链表类
class LinkedList:
    def __init__(self):
        self.head = None  # 头节点

    def is_empty(self):
        # 只需判断头节点是否为空
        return self.head is None

    def print(self):
        # 遍历链表并打印
        current = self.head
        while current is not None:
            print(current.get_data())
            current = current.get_next()

    def add(self, data):
        # # 如将元素添加到链表的尾部, 时间复杂度为O(n)，因为要遍历整个链表
        # node = Node(data)
        # if self.head is None:
        #     self.head = node
        # else:
        #     current = self.head
        #     while current.get_next() is not None:
        #         current = current.get_next()
        #     current.set_next(node)
        # 如将元素添加到链表的头部，时间复杂度为O(1)，最简单
        node = Node(data)
        node.set_next(self.head)
        self.head = node

    def __len__(self):  # 重写len()方法，获取链表长度
        # 获取链表长度，时间复杂度为O(n)
        current = self.head
        count = 0
        while current is not None:
            count += 1
            current = current.get_next()
        return count

    def insert(self, data, index):
        # 插入元素到指定位置，时间复杂度为O(n)
        if index < 0 or index > len(self):
            return False
        node = Node(data)
        if index == 0:
            node.set_next(self.head)
            self.head = node
        else:
            current = self.head
            previous = None
            for i in range(index):
                previous = current
                current = current.get_next()
            previous.set_next(node)
            node.set_next(current)

    def search(self, data):
        # 搜索元素，时间复杂度为O(n)
        current = self.head
        while current is not None:
            if current.get_data() == data:
                return True
            current = current.get_next()
        return False

    def remove(self, data):
        # 删除元素，时间复杂度为O(n)
        if self.head is None:
            return False
        if self.head.get_data() == data:
            self.head = self.head.get_next()
            return True
        current = self.head
        previous = None
        while current is not None:
            if current.get_data() == data:
                previous.set_next(current.get_next())
                return True
            previous = current
            current = current.get_next()
        return False

    def clear(self):
        # 清空链表，时间复杂度为O(1)
        self.head = None


if __name__ == '__main__':
    # 测试添加到链表尾部和头部的区别
    print("------------")
    linked_list = LinkedList()
    linked_list.add('q')
    linked_list.add(2)
    linked_list.add("hello")
    linked_list.print()
    print(len(linked_list))
    # 测试插入元素到指定位置
    print("------------")
    linked_list.insert('world', 0)
    linked_list.insert(2343245, 3)
    linked_list.print()
    # 测试搜索元素
    print("------------")
    print(linked_list.search(2343245))
    print(linked_list.search('edu.cm'))
    # 测试删除元素
    print("------------")
    linked_list.remove(2343245)
    linked_list.print()
    # 测试清空链表
    print("------------")
    linked_list.clear()
    linked_list.print()


