import struct
import os
from .Venta import FORMAT, Venta

RECORD_SIZE = struct.calcsize(FORMAT)


class BSTFile:

    def __init__(self, File):

        if os.path.exists(File) is False:
            raise ValueError(f"El fichero de la ruta {File} no existe.")

        self.FileName = File

        with open(self.FileName, "r+b") as file:
            file.seek(0, 0)
            bytes_read = file.read(4)

            if not bytes_read:
                file.seek(0, 0)
                file.write(struct.pack("i", -1))

    # falta no considerar a los elementos BORRADOS.
    def Insert(self, Venta):

        if self.Search(Venta.id) is True:
            raise ValueError(f"El ID: {Venta.id} ya existe entre los registros.")

        with open(self.FileName, "r+b") as file:

            file.seek(0, 0)

            idInsert = Venta.id
            file.seek(0, 2)
            file.write(Venta.to_byte())
            file.seek(0, 0)

            # NO CONSIDERES A LOS ELEMENTOS ELIMINADOS, ESTO SI LO ESTA CONSIDERANDO...
            TotalRegisters = int((len(file.read()) - 4) / RECORD_SIZE)

            print("Content: ", TotalRegisters)
            pos = self.getRoot()

            isRoot = False

            if pos == -1:
                file.seek(0, 0)
                file.write(struct.pack("i", TotalRegisters - 1))
                pos = TotalRegisters - 1
                isRoot = True

            NodePos = pos
            while True:

                file.seek(4 + pos * RECORD_SIZE, 0)

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

            # Cambiando la referencia al nodo padre del registro insertado.

            if TotalRegisters != 1 and not isRoot:

                data = struct.pack("i", TotalRegisters - 1)
                factor = 8 if IsLeft else 4

                file.seek(4 + (NodePos + 1) * RECORD_SIZE - factor, 0)
                file.write(data)

    def Search(self, ID):

        with open(self.FileName, "rb") as file:

            file.seek(0, 0)
            TotalBytes = len(file.read())

            pos = self.getRoot()

            if TotalBytes == 0 or pos == -1:
                return False

            while True:

                file.seek(4 + pos * RECORD_SIZE, 0)
                idNode = struct.unpack("i", file.read(4))[0]

                if idNode == ID:

                    # Si quiero retornar la venta, pero generalmente se quiere retornar el booleano.
                    # Como avance 4 bytes, lo retrocedo en base la posición actual.
                    # file.seek(-4, 1)
                    # return Venta.to_data(file.read(RECORD_SIZE))
                    return True


                # left
                elif idNode > ID:

                    IdToLeft = RECORD_SIZE - 4 - 8
                    file.seek(IdToLeft, 1)

                    pos = struct.unpack("i", file.read(4))[0]

                # right
                else:

                    IdToRight = RECORD_SIZE - 4 - 4
                    file.seek(IdToRight, 1)

                    pos = struct.unpack("i", file.read(4))[0]

                # Registro no existente.
                if pos == -1:
                    return False

    def Remove(self, ID):

        if self.Search(ID) is False:
            raise ValueError(f"El {ID} no existe en el registro.")

        with open(self.FileName, "r+b") as file:

            pos = self.getRoot()
            isRoot = True
            isLeft = None
            while True:

                file.seek(4 + pos * RECORD_SIZE, 0)
                idNode = struct.unpack("i", file.read(4))[0]

                if idNode == ID:
                    PosNode = pos
                    break
                elif idNode > ID:

                    IdToLeft = RECORD_SIZE - 4 - 8
                    file.seek(IdToLeft, 1)

                    PosPadre = pos
                    isLeft = True
                    pos = struct.unpack("i", file.read(4))[0]
                    if isRoot:
                        isRoot = False
                else:

                    IdToRight = RECORD_SIZE - 4 - 4
                    file.seek(IdToRight, 1)

                    PosPadre = pos
                    isLeft = False
                    pos = struct.unpack("i", file.read(4))[0]
                    if isRoot:
                        isRoot = False

            file.seek(4 + ((PosNode + 1) * RECORD_SIZE) - 8, 0)

            # hijos del nodo a borrar.
            left = struct.unpack("i", file.read(4))[0]
            right = struct.unpack("i", file.read(4))[0]
            factor = 8 if isLeft else 4

            # Caso 1: el nodo es hoja
            if left == -1 and right == -1:

                if isRoot:
                    file.seek(0, 0)
                    file.write(struct.pack("i", -1))
                else:

                    file.seek(0, 0)
                    data = struct.pack("i", -1)
                    file.seek(4 + ((PosPadre + 1) * RECORD_SIZE) - factor, 0)
                    file.write(data)

            # Caso 2: el nodo tiene 1 hijo
            elif (left != -1) ^ (right != -1):

                factorNode = 8 if left != -1 else 4

                if isRoot:
                    hijo = left if left != -1 else right
                    file.seek(0, 0)
                    file.write(struct.pack("i", hijo))
                    file.seek(4 + RECORD_SIZE - 8, 0)

                    # borro ambos hijos. CHECAR
                    file.write(struct.pack("i", -1))
                    file.write(struct.pack("i", -1))
                else:

                    data = struct.pack("i", -1)
                    # Actualizo el nodo a borrar para que no tenga enlaces.
                    file.seek(4 + (PosNode + 1) * RECORD_SIZE - factorNode, 0)
                    file.write(data)

                    # hacer que el nodo padre apunte al hijo del nodo actual.
                    swap = struct.pack("i", left if left != -1 else right)
                    file.seek(4 + (PosPadre + 1) * RECORD_SIZE - factor, 0)
                    file.write(swap)

            # Caso 3: el nodo tiene ambos hijos
            elif left != -1 and right != -1:

                posIO = right
                PosPadreIO = PosNode
                while True:

                    file.seek(4 + ((posIO + 1) * RECORD_SIZE) - 8, 0)
                    leftIO = struct.unpack("i", file.read(4))[0]

                    if leftIO == -1:
                        break
                    else:
                        PosPadreIO = posIO
                        posIO = leftIO

                # Leer los enlaces del sucesor inorden
                file.seek(4 + (posIO + 1) * RECORD_SIZE - 8, 0)
                leftIO = struct.unpack("i", file.read(4))[0]
                rightIO = struct.unpack("i", file.read(4))[0]

                # Esto corresponde a actualizar los enlaces del SUCESOR, su padre del SUCESOR
                # y del nodo a eliminar.

                    # SACO LOS ENLACES DEL NODO A ELIMINAR
                file.seek(4 + (PosNode + 1) * RECORD_SIZE - 8, 0)
                dataL = struct.pack("i", left)

                # Con esto soluciono el problema cuando PosPadreIO == PosNode
                dataR = struct.pack("i", rightIO if PosPadreIO == PosNode else right)

                    # LE QUITO LOS ENLACES AL NODO A ELIMINAR.
                file.write(struct.pack("i", -1))
                file.write(struct.pack("i", -1))

                    # LOS COLOCO AL NODO SUCESOR.
                file.seek(4 + (posIO + 1) * RECORD_SIZE - 8, 0)
                file.write(dataL)
                file.write(dataR)

                # Actualizar la referencia del padre del sucesor inorden
                # Si son iguales, con el cambio del sucesor InOrden es suficiente.
                if PosPadreIO != PosNode:

                    # Si son diferentes, se asume que siempre será el hijo izquierdo
                    file.seek(4 + (PosPadreIO + 1) * RECORD_SIZE - 8, 0)

                    # le pasamos el hijo derecho, en caso tenga. PERO LO PASAMOS COMO LEFT
                    file.write(struct.pack("i", rightIO))


                # Esto conlleva a actualizar el enlace del nodo padre al SUCESOR.

                # Actualizamos el root.
                if isRoot:
                    file.seek(0, 0)
                    file.write(struct.pack("i", posIO))
                else:
                    file.seek(4 + (PosPadre + 1) * RECORD_SIZE - factor, 0)
                    file.write(struct.pack("i", posIO))




    def ReadVenta(self, pos):

        with open(self.FileName, "rb") as file:
            file.seek(4 + pos * RECORD_SIZE)
            print(Venta.to_data(file.read(RECORD_SIZE)))

    def getRoot(self):
        with open(self.FileName, "rb") as file:
            file.seek(0, 0)
            return struct.unpack("i", file.read(4))[0]
