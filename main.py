from BST.Venta import Venta
from BST.BSTFile import BSTFile


def Insert(bst):
    ventas = [
        Venta(2, "Producto B", 50, 29.99, "2023-04-02"),
        Venta(1, "Producto E", 15, 49.99, "2023-04-05"),
        Venta(4, "Producto C", 200, 9.99, "2023-04-03"),
        Venta(7, "Producto G", 75, 25.00, "2023-04-07"),
        Venta(3, "Producto D", 0, 39.99, "2023-04-04"),
        Venta(6, "Producto F", 120, 15.50, "2023-04-06"),
        Venta(9, "Producto I", 150, 12.99, "2023-04-09"),
        Venta(8, "Producto H", 10, 89.99, "2023-04-08"),
        Venta(10, "Producto J", 30, 35.99, "2023-04-10"),
    ]

    for venta in ventas:
        bst.Insert(venta)



def Search(bst):
    print(bst.Search(20))
    print(bst.Search(10))
    print(bst.Search(5))
    print(bst.Search(11))


def Remove(bst):
    bst.Remove(1)
    bst.Remove(2)
    bst.Remove(3)
    bst.Remove(10)


def ReadVenta(bst, ID):
    venta = bst.ReadVenta(ID)

    print(venta[0]())
    print(f"Left: {venta[1]}")
    print(f"Right: {venta[2]}")


if __name__ == "__main__":
    bst = BSTFile("./BST/binario.dat")

    ReadVenta(bst, 4)
