from BST.Venta import Venta
from BST.BSTFile import BSTFile


if __name__ == "__main__":

    ventas = [
        Venta(3, "Producto A", 100, 19.99, "2023-04-01"),
        Venta(2, "Producto B", 50, 29.99, "2023-04-02"),
        Venta(4, "Producto C", 200, 9.99, "2023-04-03"),
        Venta(5, "Producto D", 0, 39.99, "2023-04-04"),
        Venta(1, "Producto E", 15, 49.99, "2023-04-05")
    ]

    # Muestra los detalles de las ventas
    #for venta in ventas:
    #    print(venta)


    bst = BSTFile("./BST/binario.dat")

    #for venta in ventas:
    #    bst.insert(venta)

    bst.Remove()
    print(bst.ReadVenta(0))

