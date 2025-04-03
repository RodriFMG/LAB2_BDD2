import struct
from Venta import FORMAT, Venta

RECORD_SIZE = struct.calcsize(FORMAT)


class BSTFile:

    def __init__(self, File):

        self.FileName = File

    # falta no considerar a los elementos BORRADOS.
    def insert(self, Venta):

        if self.Search(Venta.id) is True:
            ValueError(f"El ID: {Venta.id} ya existe entre los registros.")

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

                    # Si quiero retornar la venta, pero generalmente se quiere retornar el booleano.
                    # Como avance 4 bytes, lo retrocedo en base la posición actual.
                    #file.seek(-4, 1)
                    #return Venta.to_data(file.read(RECORD_SIZE))
                    return True


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

        if self.Search(ID) is False:
            ValueError(f"El {ID} no existe en el registro.")

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
                    file.seek(IdToLeft, 1)

                    PosPadre = pos
                    isLeft = True
                    pos = struct.unpack("i", file.read(4))
                else:

                    IdToRight = RECORD_SIZE - 4 - 4
                    file.seek(IdToRight, 1)

                    PosPadre = pos
                    isLeft = False
                    pos = struct.unpack("i", file.read(4))

            file.seek(((PosNode + 1)*RECORD_SIZE) - 8, 0)

            # hijos del nodo a borrar.
            left = struct.unpack("i", file.read(4))[0]
            right = struct.unpack("i", file.read(4))[0]
            factor = 8 if isLeft else 4

            # Caso 1: el nodo es hoja
            if left == -1 and right == -1:

                data = struct.pack("i", -1)
                file.seek(((PosPadre+1)*RECORD_SIZE) - factor, 0)
                file.write(data)

            # Caso 2: el nodo tiene 1 hijo
            elif (left != -1) ^ (right != -1):

                data = struct.pack("i", -1)

                # Actualizo el nodo a borrar para que no tenga enlaces.
                factorNode = 4 if left != -1 else 8
                file.seek((PosNode + 1) * RECORD_SIZE - factorNode, 0)
                file.write(data)

                # hacer que el nodo padre apunte al hijo del nodo actual.
                swap = struct.pack("i", left if left != -1 else right)
                file.seek((PosPadre + 1) * RECORD_SIZE - factor, 0)
                file.write(swap)

            # Caso 3: el nodo tiene ambos hijos
            elif left != -1 and right != -1:

                posIO = right
                PosPadreIO = PosNode
                while True:

                    file.seek(((pos + 1)*RECORD_SIZE) - 8, 0)
                    leftIO = struct.unpack("i", file.read(4))[0]

                    if leftIO == -1:
                        break
                    else:
                        PosPadreIO = posIO
                        posIO = leftIO

                    # Leer los enlaces del sucesor inorden
                    file.seek(((posIO + 1) * RECORD_SIZE) - 8, 0)
                    leftIO = struct.unpack("i", file.read(4))[0]
                    rightIO = struct.unpack("i", file.read(4))[0]

                    # Reemplazar el nodo a eliminar con el sucesor inorden
                    file.seek(-8, 1)
                    dataL = struct.pack("i", left)
                    dataR = struct.pack("i", -1 if PosPadreIO == PosNode else right)
                    file.write(dataL)
                    file.write(dataR)

                    # Actualizar la referencia del padre del sucesor inorden
                    # Si son iguales, con el cambio del sucesor InOrden es suficiente.
                    if PosPadreIO != PosNode:

                        # Si son diferentes, se asume que siempre será el hijo izquierdo
                        file.seek((PosPadreIO+1)*RECORD_SIZE - 8, 0)

                        # le pasamos el hijo derecho, en caso tenga.
                        file.write(rightIO)

                    # Quitamos las referencias al nodo a eliminar, al colocar estas
                    # nunca se llegará a este nodo, simulando que esta eliminado.
                    data = struct.pack("i", -1)
                    file.seek((PosNode+1)*RECORD_SIZE - 8, 0)
                    file.write(data)
                    file.write(data)

















    # el remove tiene que hacer que los registros borrados no apunte A NADA
    # maybe poner un -2, en cada nodo.