import struct

FORMAT = "i30sif10sB"

class VentaSecuencial:
    def __init__(self, id, name, stock, precio, date, eliminado=False):
        self.id = id
        self.name = name
        self.stock = stock
        self.precio = precio
        self.date = date
        self.eliminado = eliminado

    def to_byte(self):
        return struct.pack(
            FORMAT,
            self.id,
            self.name.encode().ljust(30)[:30],
            self.stock,
            self.precio,
            self.date.encode().ljust(10)[:10],
            1 if self.eliminado else 0
        )

    @staticmethod
    def to_data(data):
        unpacked = struct.unpack(FORMAT, data)
        return VentaSecuencial(
            unpacked[0],
            unpacked[1].decode().strip(),
            unpacked[2],
            unpacked[3],
            unpacked[4].decode().strip(),
            bool(unpacked[5])
        )

    def __call__(self):
        print("Venta:")
        print(f"ID: {self.id}")
        print(f"Nombre: {self.name}")
        print(f"Stock: {self.stock}")
        print(f"Precio: {self.precio}")
        print(f"Fecha: {self.date}")
        print(f"Estado: {'Eliminado' if self.eliminado else 'Activo'}\n")

    def __str__(self):
        estado = "Eliminado" if self.eliminado else "Activo"
        return (f"Venta(ID={self.id}, Producto='{self.name}', Stock={self.stock}, "
                f"Precio={self.precio}, Fecha='{self.date}', Estado={estado})")
