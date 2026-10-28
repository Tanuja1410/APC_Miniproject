from functools import reduce
from array import array


def run_demo():
    amounts = array("i", [500, 1200, 800, 1500])
    total = reduce(lambda a, b: a + b, amounts, 0)
    doubled = list(map(lambda x: x * 2, amounts))
    large = list(filter(lambda x: x >= 1000, amounts))
    print("Amounts:", list(amounts))
    print("Total:", total)
    print("Doubled:", doubled)
    print("1000+:", large)

    for i in range(1, 4):
        if i == 2:
            continue
        print("Loop:", i)

    x = 10
    y = 20
    print("Arithmetic:", x + y, x // 3, x % 3, x ** 2)
    print("Comparison:", x < y)
    print("Logical:", x < y and y > 0)
    print("Bitwise:", x & y, x | y, x ^ y)
    print("Membership:", 500 in amounts)
    print("Identity:", amounts is amounts)

    choice = 2
    match choice:
        case 1:
            print("One")
        case 2:
            print("Two")
        case _:
            print("Other")

    def countdown(n):
        if n == 0:
            return
        print(n)
        countdown(n - 1)

    countdown(3)


if __name__ == "__main__":
    run_demo()
