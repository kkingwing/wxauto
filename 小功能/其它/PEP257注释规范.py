class Calculator:
    """
    一个简单的计算器类，可以进行基本的算术运算。

    这个类提供了加法、减法、乘法和除法功能。
    """

    def add(self, a, b):
        """
        返回两个数的和。

        Args:
            a (int or float): 第一个加数。
            b (int or float): 第二个加数。

        Returns:
            int or float: 两个数的和。

        Raises:
            TypeError: 如果传入的参数不是数值类型。
        """
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("参数必须是数值类型")
        return a + b

    def subtract(self, a, b):
        """
        返回两个数的差。

        Args:
            a (int or float): 被减数。
            b (int or float): 减数。

        Returns:
            int or float: 两个数的差。

        Raises:
            TypeError: 如果传入的参数不是数值类型。
        """
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("参数必须是数值类型")
        return a - b

    def multiply(self, a, b):
        """
        返回两个数的积。

        Args:
            a (int or float): 第一个乘数。
            b (int or float): 第二个乘数。

        Returns:
            int or float: 两个数的积。

        Raises:
            TypeError: 如果传入的参数不是数值类型。
        """
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("参数必须是数值类型")
        return a * b

    def divide(self, a, b):
        """
        返回两个数的商。

        Args:
            a (int or float): 被除数。
            b (int or float): 除数。

        Returns:
            float: 两个数的商。

        Raises:
            TypeError: 如果传入的参数不是数值类型。
            ZeroDivisionError: 如果除数为零。
        """
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise TypeError("参数必须是数值类型")
        if b == 0:
            raise ZeroDivisionError("除数不能为零")
        return a / b
