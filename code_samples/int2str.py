# 使用栈实现整数到任意进制的字符串的转换
from data_structures.Stack import Stack


def single_digit(digit, base):
    """
    Convert a single digit to a string in a given base.
    :param digit: a single digit to be converted.
    :param base: the base to convert the digit to.
    :return: a string representation of the digit in the given base.
    """
    # 16进制的数字
    hex_digits = '0123456789ABCDEF'

    if base == 16:
        return hex_digits[digit]
    else:
        return str(digit)


def int2str(num, stack, base=10):
    """
    Convert an integer to a string in a given base.
    :param stack: a stack to store the string representation of the integer.
    :param num: an integer to be converted.
    :param base: the base to convert the integer to.
    :return: a string representation of the integer in the given base.
    """
    if num < base:
        single_str = single_digit(num, base)
        stack.push(single_str)
    else:
        # 除以基数，取余数，将余数入栈
        divisor = num // base
        remainder = num % base
        single_str = single_digit(remainder, base)
        stack.push(single_str)
        int2str(divisor, stack, base)
    return stack

if __name__ == '__main__':
    input_stack = Stack()
    input_num = 123456789  # 对应的16进制是75BCD15
    input_base = 16
    stack_str = int2str(input_num, input_stack, input_base)
    for i in range(stack_str.size()):
        print(stack_str.pop())
