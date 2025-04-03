from BST.Venta import Venta
from BST.BSTFile import BSTFile

'''
Venta(1, "Producto E", 15, 49.99, "2023-04-05"),
Venta(4, "Producto C", 200, 9.99, "2023-04-03"),
Venta(2, "Producto B", 50, 29.99, "2023-04-02"),
Venta(7, "Producto G", 75, 25.00, "2023-04-07"),
Venta(3, "Producto D", 0, 39.99, "2023-04-04"),
Venta(6, "Producto F", 120, 15.50, "2023-04-06"),
Venta(9, "Producto I", 150, 12.99, "2023-04-09"),
Venta(8, "Producto H", 10, 89.99, "2023-04-08"),
Venta(10, "Producto J", 30, 35.99, "2023-04-10"),
'''

if __name__ == "__main__":

    ventas = [
        Venta(10, "Producto E", 15, 49.99, "2023-04-05"),
        Venta(20, "Producto B", 50, 29.99, "2023-04-02"),
    ]

    # Muestra los detalles de las ventas
    #for venta in ventas:
    #    print(venta)


    bst = BSTFile("./BST/binario.dat")

    #for venta in ventas:
    #    bst.Insert(venta)

    #bst.Remove(5)


    # Falta testear desde EL ROOT para los 3 casos.
    print(bst.ReadVenta(0))
    print("Root: ", bst.getRoot())

