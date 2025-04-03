import struct

FORMAT = "4i30s4i8f10s4i4i"


class Venta:

    def __init__(self, id, name, stock, precio, date):
        self.id = id
        self.name = name
        self.stock = stock
        self.precio = precio
        self.date = date
        self.left = -1
        self.right = -1

    def to_byte(self):
        return struct.pack(
            FORMAT,
            self.id,
            self.name.encode().ljust(30)[:30],
            self.stock,
            self.precio,
            self.date.encode().ljust(10)[:10],
            self.left,
            self.right
        )

    # staticmethod es para crear un método de la clase, que no necesite una instancia a
    # la clase.
    @staticmethod
    def to_data(data):

        # unpack en base al formato y la cadena de bytes, desempaca todo
        # en una lista, con los valores de cada campo.
        unpacked = struct.unpack(FORMAT, data)
        return Venta(
            unpacked[0],
            unpacked[1].decode().strip(),
            unpacked[2],
            unpacked[3],
            unpacked[4].decode().strip()
        ), unpacked[5], unpacked[6]

    def __call__(self):

        print("Venta: ")
        print(f"Id: {self.id}")
        print(f"Nombre: {self.name}")
        print(f"Stock: {self.stock}")
        print(f"Precio: {self.precio}")
        print(f"Fecha: {self.date}")

