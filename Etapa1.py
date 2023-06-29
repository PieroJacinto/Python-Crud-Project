# -------------------------------------------------------------------
# Definimos la clase "Producto"
# -------------------------------------------------------------------
class Producto:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self, codigo, descripcion, cantidad, precio):
        self.codigo = codigo           # Código del producto
        self.descripcion = descripcion # Descripción del producto
        self.cantidad = cantidad       # Cantidad disponible del producto
        self.precio = precio           # Precio del producto

    # Este método permite modificar un producto.
    def modificar(self, nueva_descripcion, nueva_cantidad, nuevo_precio):
        self.descripcion = nueva_descripcion  # Modifica la descripción del producto
        self.cantidad = nueva_cantidad        # Modifica la cantidad del producto
        self.precio = nuevo_precio            # Modifica el precio del producto


# Probamos la clase Producto


# -------------------------------------------------------------------
# Definimos la clase "Inventario"
# El inventario gestiona una lista de productos.
# -------------------------------------------------------------------
class Inventario:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self):
        self.productos = []  # Lista de productos en el inventario (variable de clase)


    # Este método permite crear objetos de la clase "Producto" y
    # agregarlos al inventario.
    def agregar_producto(self, codigo, descripcion, cantidad, precio):
        nuevo_producto = Producto(codigo, descripcion, cantidad, precio)
        self.productos.append(nuevo_producto)  # Agrega un nuevo producto a la lista


    # Este método permite consultar datos de productos que están en el inventario
    # Devuelve el producto correspondiente al código proporcionado o False si no existe.
    def consultar_producto(self, codigo):
        for producto in self.productos:
            if producto.codigo == codigo:
                return producto
        return False


    # Este método permite modificar datos de productos que están en el inventario
    # Utiliza el método consultar_producto del inventario y modificar del producto.
    def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio):
        producto = self.consultar_producto(codigo)
        if producto:
            producto.modificar(nueva_descripcion, nueva_cantidad, nuevo_precio)
            print("-"*50)
            print(f'Producto modificado:\nCódigo: {producto.codigo}\nDescripción: {producto.descripcion}\nCantidad: {producto.cantidad}\nPrecio: {producto.precio}')


    # Este método elimina el producto indicado por codigo de la lista
    # mantenida en el inventario
    def eliminar_producto(self, codigo):
        for producto in self.productos:
            if producto.codigo == codigo:
                self.productos.remove(producto)
                print("Producto {codigo} eliminado.")
                break
        else:
            print("Producto {codigo} no encontrado.")


    # Este método imprime en la terminal una lista con los datos de los
    # productos que figuran en el inventario.
    def listar_productos(self):
        print("-"*50)
        print("INVENTARIO - Lista de productos:")
        print("Código\tDescripción\t\tCant\tPrecio")
        for producto in self.productos:
            print(f'{producto.codigo}\t{producto.descripcion}\t{producto.cantidad}\t{producto.precio}')
        print("-"*50)

# -------------------------------------------------------------------
# Definimos la clase "Carrito"
# -------------------------------------------------------------------
class Carrito:
    # Definimos el constructor e inicializamos los atributos de instancia
    def __init__(self):
        self.items = []  # Lista de items en el carrito (variable de clase)

    # Este método permite agregar productos del inventario al carrito.

    def agregar(self, codigo, cantidad, inventario):
        # Nos aseguramos que el producto esté en el inventario
        producto = inventario.consultar_producto(codigo)
        if producto is False:
            print("El producto no existe.")
            return False

        # Verificamos que la cantidad en stock sea suficiente
        if producto.cantidad < cantidad:
            print("Cantidad en stock insuficiente.")
            return False

        # Si existe y hay stock, vemos si ya existe en el carrito.
        for item in self.items:
            if item.codigo == codigo:
                item.cantidad += cantidad
                # Actualizamos la cantidad en el inventario restando la cantidad ya que se agrega al carrito
                producto = inventario.consultar_producto(codigo)
                producto.modificar(
                    producto.descripcion, producto.cantidad - cantidad, producto.precio)
                return True

        # Si no existe en el carrito, lo agregamos como un nuevo item.
        nuevo_item = Producto(codigo, producto.descripcion,
                              cantidad, producto.precio)
        self.items.append(nuevo_item)
        # Actualizamos la cantidad en el inventario restando la cantidad ya que se agrega al carrito
        producto = inventario.consultar_producto(codigo)
        producto.modificar(producto.descripcion,
                           producto.cantidad - cantidad, producto.precio)
        return True

    # Este método quita unidades de un elemento del carrito, o lo elimina.

    def quitar(self, codigo, cantidad, inventario):
        for item in self.items:
            if item.codigo == codigo:
                if cantidad > item.cantidad:
                    print("Cantidad a quitar mayor a la cantidad en el carrito.")
                    return False
                item.cantidad -= cantidad
                print(
                    f'Se ha/n eliminado {cantidad} ítem/s del producto {codigo} en el carrito.')
                if item.cantidad == 0:
                    self.items.remove(item)
                    print(f'Producto {codigo} eliminado del carrito.')
                # Actualizamos la cantidad en el inventario
                producto = inventario.consultar_producto(codigo)
                producto.modificar(
                    producto.descripcion, producto.cantidad + cantidad, producto.precio)
                return True

        # Si el bucle finaliza sin novedad, es que ese producto NO ESTA en el carrito.
        print("El producto no se encuentra en el carrito.")
        return False

    def mostrar(self):
        print("-"*50)
        print("CARRITO - Lista de productos:")
        print("Código\tDescripción\t\tCant\tPrecio")
        for item in self.items:
            print(
                f'{item.codigo}\t{item.descripcion}\t{item.cantidad}\t{item.precio}')
        print("-"*50)

