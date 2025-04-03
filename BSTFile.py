import struct
from Venta import FORMAT, Venta

RECORD_SIZE = struct.calcsize(FORMAT)


class BSTFile:

    def __init__(self, File):

        self.FileName = File

    # falta no considerar a los elementos BORRADOS.
    def insert(self, Venta):

        with open(self.FileName, "r+b") as file:

            idInsert = Venta.id

            # para escribir al final

            # 2 <- puntero al final
            # 1 <- puntero a la posicion actual del puntero.
            # 0 <- puntero al incio
            file.seek(0, 2)
            file.write(Venta.to_byte())

            TotalRegisters = len(file.read()) / RECORD_SIZE

            # Para empezar desde 0
            TotalRegisters -= 1

            while True:

                pos = 0
                file.seek(pos * RECORD_SIZE, 0)

                # Devuelve un array con todos los campos puestos en EL FORMATO.
                idNode = struct.unpack("i", file.read(4))[0]

                if idNode > idInsert:

                    # distancia desde ID hasta LEFT de un registro.
                    IdToLeft = RECORD_SIZE - 4 - 8
                    file.seek(IdToLeft, 1)

                    pos = struct.unpack("i", file.read(4))[0]
                    IsLeft = True

                else:

                    # distancia desde ID hasta RIGHT en el registro.
                    IdToRight = RECORD_SIZE - 4 - 4
                    file.seek(IdToRight, 1)

                    pos = struct.unpack("i", file.read(4))[0]
                    IsLeft = False

                if pos == -1:
                    break
                else:
                    NodePos = pos

            data = struct.pack("i", TotalRegisters)
            if IsLeft:
                file.seek((NodePos + 1) * RECORD_SIZE - 8, 0)
                file.write(data)
            else:
                file.seek((NodePos + 1) * RECORD_SIZE - 4, 0)
                file.write(data)

    def Search(self, ID):

        with open(self.FileName, "rb") as file:

            while True:

                pos = 0
                file.seek(pos*RECORD_SIZE, 0)
                idNode = struct.unpack("i", file.read(4))

                if idNode == ID:

                    # Como avance 4 bytes, lo retrocedo en base la posición actual.
                    file.seek(-4, 1)
                    return Venta.to_data(file.read(RECORD_SIZE))

                # left
                elif idNode > ID:

                    IdToLeft = RECORD_SIZE - 4 - 8
                    file.seek(IdToLeft, 1)

                    pos = struct.unpack("i", file.read(4))

                # right
                else:

                    IdToRight = RECORD_SIZE - 4 - 4
                    file.seek(IdToRight, 1)

                    pos = struct.unpack("i", file.read(4))

                # Registro no existente.
                if pos == -1:
                    return False

    def Remove(self, ID):
        pass



    # el remove tiene que hacer que los registros borrados no apunte A NADA
    # maybe poner un -2, en cada nodo.