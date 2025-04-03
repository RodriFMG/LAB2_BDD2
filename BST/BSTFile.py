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
            pos = 0

            while True:

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

            pos = 0
            while True:

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

        # validación de que el nodo existe...

        with open(self.FileName, "r+b") as file:

            pos = 0
            while True:

                file.seek(pos*RECORD_SIZE)
                idNode = struct.unpack("i", file.read(4))

                if idNode == ID:
                    PosNode = pos
                    break
                elif idNode > ID:

                    IdToLeft = RECORD_SIZE - 4 - 8
                    file.seek(IdToLeft)

                    PosPadre = pos
                    isLeft = True
                    pos = struct.unpack("i", file.read(4))
                else:

                    IdToRight = RECORD_SIZE - 4 - 4
                    file.seek(IdToRight)

                    PosPadre = pos
                    isLeft = False
                    pos = struct.unpack("i", file.read(4))

            file.seek(((PosNode + 1)*RECORD_SIZE) - 8, 0)
            left = struct.unpack("i", file.read(4))
            right = struct.unpack("i", file.read(4))
            factor = 8 if isLeft else 4

            if left == -1 and right == -1:

                data = struct.pack("i", -1)
                file.seek(((PosPadre+1)*RECORD_SIZE) - factor, 0)
                file.write(data)

            elif left != -1 or right != -1:

                data = struct.pack("i", -1)

                file.seek((PosNode + 1) * RECORD_SIZE - factor, 0)
                file.write(data)

                swap = struct.pack("i", left if isLeft else right)
                file.seek((PosPadre + 1) * RECORD_SIZE - factor, 0)
                file.write(swap)

            elif left != 1 and right != 1:

                pos = right
                while True:

                    file.seek(((pos + 1)*RECORD_SIZE) - 8, 0)
                    leftIO = struct.unpack("i", file.read(4))
                    rightIO = struct.unpack("i", file.read(4))

                    if leftIO == -1 and rightIO == -1:
                        break
                    else:
                        # el padre del nodo hoja
                        PosSwap = pos

                        # el nodo hoja
                        pos = rightIO

                # cambiamos la referencia del nodo del padre.
                swap = struct.pack("i", pos)
                file.seek((PosPadre + 1) * RECORD_SIZE - factor, 0)
                file.write(swap)

                # cambiamos la referencia del nodo actual
                dataL = struct.pack("i", -1)
                dataR = struct.pack("i", -1)
                file.seek(((PosNode+1)*RECORD_SIZE)-8, 0)
                file.write(dataL)
                file.write(dataR)

                # cambiamos la referencia del nodo InOrden
                dataL = struct.pack("i", left)
                dataR = struct.pack("i", right)
                file.seek(((pos+1)*RECORD_SIZE)-8, 0)
                file.write(dataL)
                file.write(dataR)

                # al padre del nodo InOrden le quitamos la referencia al nodo elegido
                dataR = struct.pack("i", PosSwap)
                file.seek(((PosSwap+1)*RECORD_SIZE)-4, 0)
                file.write(dataR)














    # el remove tiene que hacer que los registros borrados no apunte A NADA
    # maybe poner un -2, en cada nodo.