import struct
import os
from BST.Venta import FORMAT, Venta

RECORD_SIZE = struct.calcsize(FORMAT) +12  # 12 bytes para la altura, left y right

class AVLFile:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(filename):
            raise ValueError(f"El archivo {filename} no existe.")

        with open(self.filename, "r+b") as file:
            file.seek(0)
            bytes_read = file.read(4)
            if not bytes_read:
                file.seek(0)
                file.write(struct.pack("i", -1))  # raíz inicial

    def get_root(self):
        """Devuelve la posición de la raíz del árbol AVL.  (4 bytes) para guardar el nodo raiz"""
        with open(self.filename, "rb") as file:
            file.seek(0)
            root_pos = struct.unpack("i", file.read(4))[0]
            return root_pos # retronamos la posicion de la raiz

    def set_root(self, pos):
        """Actualiza la posición de la raíz del árbol AVL."""
        with open(self.filename, "r+b") as file:
            file.seek(0)
            file.write(struct.pack("i", pos)) # actualizamos la raiz

    def read_node(self, pos):
        """
        Lee un nodo desde el archivo en la posición lógica `pos`.
        Retorna: (venta: Venta, altura: int, left: int, right: int)
        """
        with open(self.filename, "rb") as file:
            offset = 4 + pos * RECORD_SIZE  # Saltamos el header (4 bytes) + registros anteriores
            file.seek(offset)

            # Leer los bytes del registro completo
            data = file.read(RECORD_SIZE)

            # Extraemos la parte de Venta
            venta_size = struct.calcsize(FORMAT)
            venta_data = data[:venta_size]#solo venta sacamos
            venta = Venta.to_data(venta_data) #desempacamos la venta

            # Extraemos los 3 campos adicionales (altura, left, right)
            extras = data[venta_size:]
            altura, left, right = struct.unpack("iii", extras)

            return venta, altura, left, right

    def write_node(self, pos, venta, altura, left, right):
        """
        Escribe un nodo completo en la posición lógica `pos`.
        Incluye los campos de Venta + altura + hijos.
        """
        with open(self.filename, "r+b") as file:
            offset = 4 + pos * RECORD_SIZE  # Saltamos el header (4 bytes)
            file.seek(offset)

            venta_bytes = venta.to_byte()  # Serializamos la venta
            extras = struct.pack("iii", altura, left, right)  # altura, left, right como enteros

            file.write(venta_bytes + extras)


    def insert(self, venta):
        """Inserta una venta en el árbol AVL, reequilibrando si es necesario."""
        with open(self.filename,"r+b")as file:
            root_pos = self.get_root() #obtener la poss actual de la raiz del arbol

            #llamar ala funcion de insercion recursiva, y balancea
            new_root_pos = self._insert_rec(file, root_pos, venta)

            #una vez insertado, update la raiz del tree
            self.set_root(new_root_pos)


    def _insert_rec(self, file, pos, venta):
        """
        Inserta recursivamente un nodo en el árbol AVL.
        Retorna la nueva raíz del subárbol (posición lógica).
        """
        # Si el árbol está vacío, inserta el nuevo nodo.
        if pos == -1:
            file.seek(0)
            new_pos= (file.tell()-4) // RECORD_SIZE #file.tell:total de bytes del archivo -4 por el header
            # // dividimos por el Record y optenesmo el poss final
            self.write_node(new_pos, venta, altura=1, left=-1, right=-1) # escribimos  el nuevo nodo.
            return new_pos

        venta_current,hight,left,right=self.read_node(pos)

        if venta.id<venta_current.id:
           new_left= self._insert_rec(file,left,venta) # nos moveos hasta el -1 pasadno el left del arbol
           left= new_left # update con el nuevo pos para el left que fue retornado x el case base
        elif venta.id> venta_current.id:
            #similar logic
            new_right= self._insert_rec(file,right,venta)
            right =new_right
        else:#si no entra ya existe
            raise ValueError(f"El id {venta.id} ya esta registrado")

        #calculo de la alutras
        if left!=-1:#Si el hijo izquierdo existe
            altura_left=self.read_node(left)[1] # sacamos la altura
        else:
            altura_left=0
        if right!=-1:
            altura_right=self.read_node(right)[1]
        else:
            altura_right=0

        #update altura
        altura=self.update_height(altura_left,altura_right)

        #escribir el nodo actual
        self.write_node(pos,venta_current,altura,left,right)

        # Balancear el nodo actual si es necesario
        return self.balance(file, pos)






    def remove(self, id):
        pass

    def _remove_rec(self, file, pos, id):
        pass

    def balance_factor(self, altura_izq, altura_der):
        pass

    def update_height(self, altura_izq, altura_der):
        pass

    def rotate_left(self, file, pos):
        """Realiza una rotación izquierda y retorna la nueva raíz del subárbol."""
        pass

    def rotate_right(self, file, pos):
        """Realiza una rotación derecha y retorna la nueva raíz del subárbol."""
        pass

    def balance(self, file, pos):
        """Verifica y balancea un subárbol en la posición dada."""
        pass

    def search(self, id):
        pass
