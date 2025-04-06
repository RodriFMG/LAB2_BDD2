import struct
import os
from BST.Venta import FORMAT, Venta

RECORD_SIZE = struct.calcsize(FORMAT) +4  # para altura
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

    def read_node(self, pos, file):
        offset = 4 + pos * RECORD_SIZE
        file.seek(offset)
        data = file.read(RECORD_SIZE)
        venta_data = data[:-4]
        altura_bytes = data[-4:]
        venta, left, right = Venta.to_data(venta_data)
        altura = struct.unpack("i", altura_bytes)[0]
        return venta, altura, left, right

    def write_node(self, pos, venta, altura, left, right, file):
        offset = 4 + pos * RECORD_SIZE
        file.seek(offset)

        venta.left = left
        venta.right = right

        venta_bytes = venta.to_byte()
        altura_bytes = struct.pack("i", altura)
        file.write(venta_bytes + altura_bytes)

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
            file.seek(0,2)
            new_pos= (file.tell()-4) // RECORD_SIZE #file.tell:total de bytes del archivo -4 por el header
            # // dividimos por el Record y optenesmo el poss final
            self.write_node(new_pos, venta, altura=1, left=-1, right=-1,file=file) # escribimos  el nuevo nodo.
            return new_pos

        venta_current,hight,left,right=self.read_node(pos,file)

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
            altura_left=self.read_node(left,file)[1] # sacamos la altura
        else:
            altura_left=0
        if right!=-1:
            altura_right=self.read_node(right,file)[1]
        else:
            altura_right=0

        #update altura
        altura=self.update_height(altura_left,altura_right)

        #escribir el nodo actual
        self.write_node(pos,venta_current,altura,left,right,file)

        # Balancear el nodo actual si es necesario
        return self.balance(file, pos)

    def remove(self, id):
        with open(self.filename, "r+b") as file:
            root_pos = self.get_root()
            new_root_pos = self._remove_rec(file, root_pos, id)
            self.set_root(new_root_pos)

    def _remove_rec(self, file, pos, id):
        if pos == -1:
            raise ValueError(f"ID {id} no encontrado.")

        venta, altura, left, right = self.read_node(pos,file)

        # 🔁 Buscar nodo a eliminar
        if id < venta.id:
            new_left = self._remove_rec(file, left, id)
            left = new_left

        elif id > venta.id:
            new_right = self._remove_rec(file, right, id)
            right = new_right

        else:

            # ✅ CASO 1: Nodo hoja
            if left == -1 and right == -1:
                return -1

            # ✅ CASO 2: Un solo hijo
            if left == -1:
                return right
            elif right == -1:
                return left

            # ✅ CASO 3: Dos hijos
            # Buscar sucesor inorden (mínimo del subárbol derecho)
            suc_pos = right
            while True:
                venta_suc, _, suc_left, _ = self.read_node(suc_pos,file)
                if suc_left == -1:
                    break
                suc_pos = suc_left

            # Leer el sucesor inorden completamente
            venta_suc, altura_suc, left_suc, right_suc = self.read_node(suc_pos,file)

            # Sustituir el nodo actual con el sucesor
            venta = venta_suc
            right = self._remove_rec(file, right, venta_suc.id)  # eliminar el sucesor original

        # 🔄 Recalcular altura
        altura_izq = self.read_node(left,file)[1] if left != -1 else 0
        altura_der = self.read_node(right,file)[1] if right != -1 else 0
        altura = self.update_height(altura_izq, altura_der)

        # 💾 Guardar el nodo actualizado
        self.write_node(pos, venta, altura, left, right,file)

        return self.balance(file, pos)

    def balance_factor(self, altura_izq, altura_der):
        """
        Retorna el factor de balanceo: altura_izquierda - altura_derecha.
        Si es > 1 o < -1, el nodo está desbalanceado.
        """
        return altura_izq - altura_der

    def update_height(self, altura_izq, altura_der):
        """
        retorna la nueva altura del nodo actual
        a partir de las alturas de sus hijos.
        """
        return 1 + max(altura_izq, altura_der)

    def rotate_left(self, file, pos):
        """
        Rotación simple a la izquierda.
        `pos` es la posición del nodo A.
        Devuelve la nueva raíz del subárbol (posición de B).
        """
        # Nodo A (raíz actual del subárbol)
        venta_a, altura_a, left_a, right_a = self.read_node(pos,file)

        # Nodo B (hijo derecho de A)
        venta_b, altura_b, left_b, right_b = self.read_node(right_a,file)

        # A se convierte en hijo izquierdo de B
        new_right_a = left_b  # El hijo izquierdo de B pasa a ser hijo derecho de A
        new_left_b = pos  # A se convierte en hijo izquierdo de B

        # Recalcular alturas
        altura_izq_a = self.read_node(left_a,file)[1] if left_a != -1 else 0
        altura_der_a = self.read_node(new_right_a,file)[1] if new_right_a != -1 else 0
        altura_a = self.update_height(altura_izq_a, altura_der_a)

        altura_izq_b = self.update_height(altura_a, self.read_node(right_b,file)[1] if right_b != -1 else 0)

        # Reescribir nodo A con nuevos enlaces
        self.write_node(pos, venta_a, altura_a, left_a, new_right_a,file)

        # Reescribir nodo B con nuevos enlaces
        self.write_node(right_a, venta_b, altura_izq_b, new_left_b, right_b,file)

        # Nueva raíz del subárbol
        return right_a

    def rotate_right(self, file, pos):
        """
        Rotación simple a la derecha.
        `pos` es la posición del nodo A.
        Devuelve la nueva raíz del subárbol (posición de B).
        """
        # Nodo A
        venta_a, altura_a, left_a, right_a = self.read_node(pos,file)

        # Nodo B (hijo izquierdo de A)
        venta_b, altura_b, left_b, right_b = self.read_node(left_a,file)

        # A se convierte en hijo derecho de B
        new_left_b = left_b
        new_right_b = pos  # A pasa a ser hijo derecho de B

        # El hijo derecho de B pasa a ser el hijo izquierdo de A
        new_left_a = right_b  # Este era right de B, ahora será left de A

        # Recalcular alturas
        altura_izq_a = self.read_node(new_left_a,file)[1] if new_left_a != -1 else 0
        altura_der_a = self.read_node(right_a,file)[1] if right_a != -1 else 0
        altura_a = self.update_height(altura_izq_a, altura_der_a)

        altura_izq_b = self.read_node(new_left_b,file)[1] if new_left_b != -1 else 0
        altura_der_b = self.update_height(altura_izq_b, altura_a)

        # Escribir nodo A actualizado
        self.write_node(pos, venta_a, altura_a, new_left_a, right_a,file)

        # Escribir nodo B actualizado en su misma posición
        self.write_node(left_a, venta_b, altura_der_b, new_left_b, new_right_b,file)

        # Retornar nueva raíz del subárbol
        return left_a

    def balance(self, file, pos):
        """
        Verifica el factor de balanceo de un nodo en `pos` y aplica rotaciones si es necesario.
        Retorna la nueva posición raíz del subárbol balanceado.
        """
        venta, altura, left, right = self.read_node(pos,file)

        # Obtener alturas de los hijos
        altura_izq = self.read_node(left,file)[1] if left != -1 else 0
        altura_der = self.read_node(right,file)[1] if right != -1 else 0

        bf = self.balance_factor(altura_izq, altura_der)

        # Caso LL (rotación simple a la derecha)
        if bf > 1:
            hijo_izq = self.read_node(left,file)
            altura_hi_izq = self.read_node(hijo_izq[2],file)[1] if hijo_izq[2] != -1 else 0
            altura_hi_der = self.read_node(hijo_izq[3],file)[1] if hijo_izq[3] != -1 else 0
            if altura_hi_izq >= altura_hi_der:
                return self.rotate_right(file, pos)
            else:
                # LR
                new_left = self.rotate_left(file, left)
                self.write_node(pos, venta, altura, new_left, right,file)
                return self.rotate_right(file, pos)

        # Caso RR (rotación simple a la izquierda)
        if bf < -1:
            hijo_der = self.read_node(right,file)
            altura_hd_izq = self.read_node(hijo_der[2],file)[1] if hijo_der[2] != -1 else 0
            altura_hd_der = self.read_node(hijo_der[3],file)[1] if hijo_der[3] != -1 else 0
            if altura_hd_der >= altura_hd_izq:
                return self.rotate_left(file, pos)
            else:
                # RL
                new_right = self.rotate_right(file, right)
                self.write_node(pos, venta, altura, left, new_right,file)
                return self.rotate_left(file, pos)

        # Ya está balanceado
        return pos

    def search(self, id):
        """
        Busca un nodo con el ID especificado.
        Retorna True si existe, False en caso contrario.
        """
        with open(self.filename, "rb") as file:
            pos = self.get_root()

            while pos != -1:
                venta, altura, left, right = self.read_node(pos,file)

                if id == venta.id:
                    return True
                elif id < venta.id:
                    pos = left
                else:
                    pos = right

            return False

    def search_range(self, id_min, id_max):
        with open(self.filename, "rb") as file:
            results = []
            self._search_range_rec(file, self.get_root(), id_min, id_max, results)
            return results

    def _search_range_rec(self, file, pos, id_min, id_max, results):
        if pos == -1:
            return

        venta, altura, left, right = self.read_node(pos,file)

        # Si puede haber valores válidos a la izquierda
        if venta.id > id_min:
            self._search_range_rec(file, left, id_min, id_max, results)

        # Si está en el rango, lo agregamos
        if id_min <= venta.id <= id_max:
            results.append(venta)

        # Si puede haber valores válidos a la derecha
        if venta.id < id_max:
            self._search_range_rec(file, right, id_min, id_max, results)

