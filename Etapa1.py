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

