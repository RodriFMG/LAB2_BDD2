import struct
import os
from .Venta import FORMAT, Venta

RECORD_SIZE = struct.calcsize(FORMAT)


class BSTFile:

    def __init__(self, File):

        # Verificamos si existe el archivo.
        if os.path.exists(File) is False:
            raise ValueError(f"El fichero de la ruta {File} no existe.")

        self.FileName = File

        # Extraemos el nodo padre.
        with open(self.FileName, "r+b") as file:
            file.seek(0, 0)
            bytes_read = file.read(4)

            # Si aún no inserto ningun elemento, no existirá esa cadena de bytes.
            if not bytes_read:
                file.seek(0, 0)
                file.write(struct.pack("i", -1))

    # # O(log2(n)) + O(log2(n)), O(n) + O(n) en el peor de los casos.
    def Insert(self, Venta):

        # Verificamos si existe un registro con el mismo ID.
        # O(log2(n)), O(n) en el peor de los casos.
        if self.Search(Venta.id) is True:
            raise ValueError(f"El ID: {Venta.id} ya existe entre los registros.")

        with open(self.FileName, "r+b") as file:

            file.seek(0, 0)

            idInsert = Venta.id
            file.seek(0, 2)

            # Insertamos al final el nuevo registro.
            file.write(Venta.to_byte())
            file.seek(0, 0)

            TotalRegisters = int((len(file.read()) - 4) / RECORD_SIZE)

            # Obtenemos el nodo padre.
            pos = self.getRoot()

            isRoot = False

            # Si el nodo padre es -1, significa que no hay ningun nodo en el arbol.
            if pos == -1:
                file.seek(0, 0)
                file.write(struct.pack("i", TotalRegisters - 1))
                pos = TotalRegisters - 1

                # Si es que estamos insertando un nodo padre.
                isRoot = True

            NodePos = pos

            # O(log2(n)), O(n) en el peor de los casos.
            while True:

                # Los primeros 4 bytes es el nodo padre.

                # Movemos el puntero al inicio del registro.
                file.seek(4 + pos * RECORD_SIZE, 0)

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

                # Nodos sin left o right, se colocó -1.
                if pos == -1:
                    break
                else:
                    NodePos = pos

            # Si es que el root existe:
            if TotalRegisters != 1 and not isRoot:
                data = struct.pack("i", TotalRegisters - 1)
                factor = 8 if IsLeft else 4

                # Actualizamos el left o right del nodo que tiene como hijo al registro insertado.
                file.seek(4 + (NodePos + 1) * RECORD_SIZE - factor, 0)
                file.write(data)

    # O(log2(n)), O(n) en el peor de los casos.
    def Search(self, ID):

        with open(self.FileName, "rb") as file:

            file.seek(0, 0)
            TotalBytes = len(file.read())

            pos = self.getRoot()

            # Si es que el archivo está vacio o el arbol está vacio.
            # Realizado porque cuando insertemos el 1er elemento al arbol, el archivo binario estará vació.
            if TotalBytes == 0 or pos == -1:
                return False

            # O(log2(n)), O(n) en el peor de los casos.
            while True:

                file.seek(4 + pos * RECORD_SIZE, 0)
                idNode = struct.unpack("i", file.read(4))[0]

                # Verificar si existe el registro.
                if idNode == ID:
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

                # Si el arbol no se encuentra el registro, se llegará a un -1.
                if pos == -1:
                    return False

    # O(log2(n)) + O(log2(n)) + O(log2(n)), O(n) + O(n) + O(n) en el peor de los casos.
    def Remove(self, ID):

        # Verificamos si el registro existe.
        # O(log2(n)), O(n) en el peor de los casos.
        if self.Search(ID) is False:
            raise ValueError(f"El {ID} no existe en el registro.")

        with open(self.FileName, "r+b") as file:

            pos = self.getRoot()

            # isRoot: necesario, porque si eliminamos el root, debemos actualizar los primeros 4 byts
            # que permite al insert saber cuál es el punto de inicio del arbol.
            isRoot = True

            # Necesario para saber si nos encontramos al nodo izquierdo o derecho del nodo padre.
            isLeft = None

            # Lo que buscamos es rescatar el número de registro del nodo a eliminar y su padre
            # para actualizar sus enlaces directamente desde el contenido del archivo binario.

            # O(log2(n)), O(n) en el peor de los casos.
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

            # Nos posicionamos en el nodo siguiente, para rescatar fácilmente
            # los hijos del nodo a borrar.
            file.seek(4 + ((PosNode + 1) * RECORD_SIZE) - 8, 0)

            # hijos del nodo a borrar.
            left = struct.unpack("i", file.read(4))[0]
            right = struct.unpack("i", file.read(4))[0]

            factor = 8 if isLeft else 4

            # Caso 1: el nodo es hoja
            if left == -1 and right == -1:

                # Si es root, solo debemos actualizar la referencia al nodo padre a -1
                # lo cual indica, que el arbol está vació.
                if isRoot:
                    file.seek(0, 0)
                    file.write(struct.pack("i", -1))
                else:

                    file.seek(0, 0)
                    data = struct.pack("i", -1)

                    # Actualizamos al padre, ya no tiene como hijo al nodo a eliminar.
                    file.seek(4 + ((PosPadre + 1) * RECORD_SIZE) - factor, 0)
                    file.write(data)

            # Caso 2: el nodo tiene 1 hijo
            # O(log2(n)), O(n) en el peor de los casos.
            elif (left != -1) ^ (right != -1):

                # Verificamos si el nodo a eliminar tiene hijo izquierdo o derecho.
                # factor: es con respecto al nodo padre, si el nodo a eliminar es left o right.
                factorNode = 8 if left != -1 else 4

                if isRoot:

                    # Si eliminamos el root, el root no tiene PosPadre, su único hijo será el nuevo
                    # root.
                    hijo = left if left != -1 else right
                    file.seek(0, 0)

                    # Actualizamos al único hijo, como nuevo root.
                    file.write(struct.pack("i", hijo))
                    file.seek(4 + RECORD_SIZE - 8, 0)

                    # Elimino los enlaces del nodo padre.
                    file.write(struct.pack("i", -1))
                    file.write(struct.pack("i", -1))
                else:

                    data = struct.pack("i", -1)

                    # Quitamos el enlace al nodo a eliminar.
                    file.seek(4 + (PosNode + 1) * RECORD_SIZE - factorNode, 0)
                    file.write(data)

                    # Le asignamos al nodo padre el nodo hijo del registro a eliminar.
                    swap = struct.pack("i", left if left != -1 else right)
                    file.seek(4 + (PosPadre + 1) * RECORD_SIZE - factor, 0)
                    file.write(swap)

            # Caso 3: el nodo tiene ambos hijos
            elif left != -1 and right != -1:

                # Debemos actualizar:
                # PosPadre: posición del nodo padre
                # NodePos: posición del nodo a eliminar
                # posIO: posición del nodo InOrder sucesor.
                # PosPadreIO: posición del padre del nodo InOrder sucesor.

                posIO = right
                PosPadreIO = PosNode

                # # Conseguiremos el sucesor con mínimo valor.
                while True:

                    file.seek(4 + ((posIO + 1) * RECORD_SIZE) - 8, 0)
                    leftIO = struct.unpack("i", file.read(4))[0]

                    # Indica que ya pasamos por un nodo hoja.
                    if leftIO == -1:
                        break
                    else:
                        PosPadreIO = posIO
                        posIO = leftIO

                # Hijos del nodo candidato.
                file.seek(4 + (posIO + 1) * RECORD_SIZE - 8, 0)

                leftIO = struct.unpack("i", file.read(4))[0]
                rightIO = struct.unpack("i", file.read(4))[0]

                # EXTRAEMOS LOS ENLACES DEL NODO A ELIMINAR
                file.seek(4 + (PosNode + 1) * RECORD_SIZE - 8, 0)
                dataL = struct.pack("i", left)

                # Si el nodo sucesor el hijo del nodo a eliminar, le anclaremos
                # su right del sucesor, si no, el right del nodo a eliminar.
                dataR = struct.pack("i", rightIO if PosPadreIO == PosNode else right)

                # LE QUITO LOS ENLACES AL NODO A ELIMINAR.
                file.write(struct.pack("i", -1))
                file.write(struct.pack("i", -1))

                # LOS COLOCO AL NODO SUCESOR.
                file.seek(4 + (posIO + 1) * RECORD_SIZE - 8, 0)
                file.write(dataL)
                file.write(dataR)

                # Actualizar la referencia del padre del sucesor
                if PosPadreIO != PosNode:
                    file.seek(4 + (PosPadreIO + 1) * RECORD_SIZE - 8, 0)

                    # Le pasamos el contenido del hijo derecho del nodo sucesor, ya que puede
                    # pasar que el nodo candidato tenga right.
                    file.write(struct.pack("i", rightIO))

                # Si eliminamos el root, debemos actualizar la referencia al nuevo root, el cual sería
                # el nodo candidato.
                if isRoot:
                    file.seek(0, 0)
                    file.write(struct.pack("i", posIO))
                else:

                    # En caso no sea el root, debemos actualizar el enlace del nodo padre
                    # al nodo candidato.
                    file.seek(4 + (PosPadre + 1) * RECORD_SIZE - factor, 0)
                    file.write(struct.pack("i", posIO))

    # O(log2(n)) + O(log2(n)), O(n) + O(n) en el peor de los casos
    def ReadVenta(self, ID):

        # O(log2(n)), O(n) en el peor de los casos
        if self.Search(ID) is False:
            raise ValueError(f"El {ID} no existe en el registro.")

        with open(self.FileName, "rb") as file:

            file.seek(0, 0)
            pos = self.getRoot()

            file.seek(0, 0)

            # O(log2(n)), O(n) en el peor de los casos
            while True:

                file.seek(4 + pos * RECORD_SIZE, 0)
                idNode = struct.unpack("i", file.read(4))[0]

                if idNode == ID:
                    break
                elif idNode > ID:

                    IdToLeft = RECORD_SIZE - 4 - 8
                    file.seek(IdToLeft, 1)
                    pos = struct.unpack("i", file.read(4))[0]

                else:

                    IdToRight = RECORD_SIZE - 4 - 4
                    file.seek(IdToRight, 1)
                    pos = struct.unpack("i", file.read(4))[0]

            file.seek(0, 0)
            file.seek(4 + pos * RECORD_SIZE)

            return Venta.to_data(file.read(RECORD_SIZE))

    # O(1), solo rescatamos los 4 primeros bytes, el root.
    def getRoot(self):
        with open(self.FileName, "rb") as file:
            file.seek(0, 0)
            return struct.unpack("i", file.read(4))[0]
