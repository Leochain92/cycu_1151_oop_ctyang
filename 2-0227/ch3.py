import math
import matplotlib.pyplot as plt


def func1(x):
    """Return a list of y values using y = sin(x)."""
    y = []
    for value in x:
        y.append(math.sin(value))
    return y


def draw(x, y):
    """Plot matching lists of x and y values."""
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")

    plt.figure()
    plt.plot(x, y, marker="o", markersize=4, linewidth=2, label="y = sin(x)")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("y = sin(x)")
    plt.grid(True)
    plt.legend()
    plt.savefig("sin_plot.png", dpi=200)
    plt.show()


if __name__ == "__main__":
    x = [i / 10 for i in range(-30, 31)]
    y = func1(x)
    print("x =", x)
    print("y =", y)
    draw(x, y)