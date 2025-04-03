import struct

# no es necesario colocar el tamaño del float o int, los coloca struct en automatico.
FORMAT = "i30sif10sii"


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

    # Sirve para ejecutar esto al llamar como función a una clase.
    def __call__(self):

        print("Venta: ")
        print(f"Id: {self.id}")
        print(f"Nombre: {self.name}")
        print(f"Stock: {self.stock}")
        print(f"Precio: {self.precio}")
        print(f"Fecha: {self.date}\n")

    # Sirve para poder usar una clase en un string, debe retornar si o si un string
    # para el print o str.
    def __str__(self):

        return (f"Venta(id = {self.id}, nombre = {self.name}, stock = {self.stock}, precio = {self.stock}"
                f"fecha = {self.date})")

