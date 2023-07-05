

import sqlite3
from flask import Flask,  jsonify, request, send_from_directory
from flask_cors import CORS

from werkzeug.utils import secure_filename

from datetime import datetime
import os
# Configurar la conexión a la base de datos SQLite
DATABASE = 'fotos2.db'

def get_db_connection():
    print("Obteniendo conexión...") # Para probar que se ejecuta la función
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Crear la tabla 'productos' si no existe
def create_table():
    print("Creando tabla productos...") # Para probar que se ejecuta la función
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            codigo INTEGER PRIMARY KEY,
            plataforma TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            foto TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Verificar si la base de datos existe, si no, crearla y crear la tabla
def create_database():
    print("Creando la BD...") # Para probar que se ejecuta la función
    conn = sqlite3.connect(DATABASE)
    conn.close()
    create_table()

# Crear la base de datos y la tabla si no existen
create_database()

# -------------------------------------------------------------------
# Definimos la clase "Producto"
# -------------------------------------------------------------------
class Producto:
    def __init__(self, codigo, plataforma, descripcion, cantidad, precio, foto):
        self.codigo = codigo
        self.plataforma = plataforma
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.precio = precio
        self.foto = foto

    def modificar(self, nueva_plataforma, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_foto):
        self.plataforma = nueva_plataforma
        self.descripcion = nueva_descripcion
        self.cantidad = nueva_cantidad
        self.precio = nuevo_precio
        self.foto = nueva_foto


# -------------------------------------------------------------------
# Definimos la clase "Inventario"
# -------------------------------------------------------------------
class Inventario:
    def __init__(self):
        self.conexion = get_db_connection()
        self.cursor = self.conexion.cursor()

    def agregar_producto(self, codigo, plataforma, descripcion, cantidad, precio, foto):
        producto_existente = self.consultar_producto(codigo)
        if producto_existente:
            return jsonify({'message': 'Ya existe un producto con ese código.'}), 400

        #nuevo_producto = Producto(codigo, descripcion, cantidad, precio)
        self.cursor.execute("INSERT INTO productos VALUES (?, ?, ?, ?, ?, ?)", (codigo, plataforma, descripcion, cantidad, precio, foto))
        self.conexion.commit()
        return jsonify({'message': 'Producto agregado correctamente.'}), 200

    def consultar_producto(self, codigo):
        self.cursor.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
        row = self.cursor.fetchone()
        if row:
            codigo, plataforma, descripcion, cantidad, precio, foto = row
            return Producto(codigo, plataforma, descripcion, cantidad, precio, foto)
        return None

    def modificar_producto(self, codigo, nueva_plataforma, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_foto):
        producto = self.consultar_producto(codigo)
        if producto:
            # Eliminar la imagen anterior si existe
            if producto.foto:
                foto_anterior = os.path.join(app.config['UPLOAD_FOLDER'], producto.foto)
                if os.path.exists(foto_anterior):
                    os.remove(foto_anterior)
                else:
                    print(f"El archivo '{foto_anterior}' no existe.")

            # Actualizar los datos del producto
            #producto.modificar(nueva_plataforma, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_foto)
            self.cursor.execute("UPDATE productos SET plataforma = ?, descripcion = ?, cantidad = ?, precio = ?, foto = ? WHERE codigo = ?",
                                (nueva_plataforma, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_foto, codigo))
            self.conexion.commit()
            return jsonify({'message': 'Producto modificado correctamente.'}), 200
        return jsonify({'message': 'Producto no encontrado.'}), 404

    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        rows = self.cursor.fetchall()
        productos = []
        for row in rows:
            codigo, plataforma, descripcion, cantidad, precio, foto = row
            producto = {'codigo': codigo, 'plataforma': plataforma, 'descripcion': descripcion, 'cantidad': cantidad, 'precio': precio, 'foto': foto}
            productos.append(producto)
        return jsonify(productos), 200

    def eliminar_producto(self, codigo):
        # Obtener el nombre del archivo de la foto del producto
        self.cursor.execute("SELECT foto FROM productos WHERE codigo = ?", (codigo,))
        result = self.cursor.fetchone()
        if result:
            foto = result[0]
            # Eliminar el producto de la base de datos
            self.cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
            if self.cursor.rowcount > 0:
                self.conexion.commit()
                # Construir la ruta completa del archivo de la foto
                ruta_foto = os.path.join(app.config['UPLOADS'], foto)
                # Verificar si el archivo existe y eliminarlo
                if os.path.exists(ruta_foto):
                    os.remove(ruta_foto)
                return jsonify({'message': 'Producto eliminado correctamente.'}), 200
        return jsonify({'message': 'Producto no encontrado.'}), 404


# -------------------------------------------------------------------
# Definimos la clase "Carrito"
# -------------------------------------------------------------------
class Carrito:
    def __init__(self):
        self.conexion = get_db_connection()
        self.cursor = self.conexion.cursor()
        self.items = []

    def agregar(self, codigo, cantidad, inventario):
        producto = inventario.consultar_producto(codigo)
        if producto is None:
            return jsonify({'message': 'El producto no existe.'}), 404
        if producto.cantidad < cantidad:
            return jsonify({'message': 'Cantidad en stock insuficiente.'}), 400

        for item in self.items:
            if item.codigo == codigo:
                item.cantidad += cantidad
                self.cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE codigo = ?",
                                    (cantidad, codigo))
                self.conexion.commit()
                return jsonify({'message': 'Producto agregado al carrito correctamente.'}), 200

        nuevo_item = Producto(codigo, producto.plataforma, producto.descripcion, cantidad, producto.precio, producto.foto)
        self.items.append(nuevo_item)
        self.cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE codigo = ?",
                            (cantidad, codigo))
        self.conexion.commit()
        return jsonify({'message': 'Producto agregado al carrito correctamente.'}), 200

    def quitar(self, codigo, cantidad, inventario):
        for item in self.items:
            if item.codigo == codigo:
                if cantidad > item.cantidad:
                    return jsonify({'message': 'Cantidad a quitar mayor a la cantidad en el carrito.'}), 400
                item.cantidad -= cantidad
                if item.cantidad == 0:
                    self.items.remove(item)
                self.cursor.execute("UPDATE productos SET cantidad = cantidad + ? WHERE codigo = ?",
                                    (cantidad, codigo))
                self.conexion.commit()
                return jsonify({'message': 'Producto quitado del carrito correctamente.'}), 200

        return jsonify({'message': 'El producto no se encuentra en el carrito.'}), 404

    def mostrar(self):
        productos_carrito = []
        for item in self.items:
            producto = {'codigo': item.codigo, 'plataforma': item.plataforma, 'descripcion': item.descripcion, 'cantidad': item.cantidad,
                        'precio': item.precio}
            productos_carrito.append(producto)
        return jsonify(productos_carrito), 200

# -------------------------------------------------------------------
# Configuración y rutas de la API Flask
# -------------------------------------------------------------------
#1)	Importación de los módulos y creación de la aplicación Flask

app = Flask(__name__)
CORS(app)
UPLOADS = os.path.join(app.root_path, 'uploads')
app.config['UPLOADS'] = UPLOADS
app.config['UPLOAD_FOLDER'] = '/home/pieroja/mysite/uploads/'
carrito = Carrito()         # Instanciamos un carrito
inventario = Inventario()   # Instanciamos un inventario

@app.route('/uploads/<path:filename>')
def serve_image(filename):
    print(app.config['UPLOADS'], filename)
    return send_from_directory(app.config['UPLOADS'], filename)
# 2 - Ruta para obtener los datos de un producto según su código
# GET: envía la información haciéndola visible en la URL de la página web.
@app.route('/productos/<int:codigo>', methods=['GET'])
def obtener_producto(codigo):
    producto = inventario.consultar_producto(codigo)
    if producto:
        return jsonify({
            'codigo': producto.codigo,
            'plataforma': producto.plataforma,
            'descripcion': producto.descripcion,
            'cantidad': producto.cantidad,
            'precio': producto.precio,
            'foto': producto.foto
        }), 200
    return jsonify({'message': 'Producto no encontrado.'}), 404

# 3 - Ruta para obtener la lista de productos del inventario
@app.route('/productos', methods=['GET'])
def obtener_productos():
    return inventario.listar_productos()
# 4 - Ruta para agregar un producto al inventario
# POST: envía la información ocultándola del usuario.
@app.route('/productos', methods=['POST'])
def agregar_producto():
    codigo = request.form.get('codigo')
    plataforma = request.form.get('plataforma')
    descripcion = request.form.get('descripcion')
    cantidad = request.form.get('cantidad')
    precio = request.form.get('precio')
    foto = request.files['foto']

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    filename = secure_filename(foto.filename)
    nuevoFilename = tiempo + '_' + filename
    foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nuevoFilename))
    nueva_foto = os.path.join(app.config['UPLOAD_FOLDER'], nuevoFilename)
    return inventario.agregar_producto(codigo, plataforma, descripcion, cantidad, precio, nuevoFilename)

# 5 - Ruta para modificar un producto del inventario
# PUT: permite actualizar información.
@app.route('/productos/<codigo>', methods=['PUT'])
def modificar_producto(codigo):
    # Obtener los datos del producto del formulario
    nueva_plataforma = request.form['plataformaModificar']
    nueva_descripcion = request.form['descripcionModificar']
    nueva_cantidad = request.form['cantidadModificar']
    nuevo_precio = float(request.form['precioModificar'])  # Convertir a float
    foto = request.files['fotoModificar']
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if foto:
        filename = secure_filename(foto.filename)
        nuevoFilename = tiempo + '_' + filename
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nuevoFilename))
        nueva_foto = os.path.join(app.config['UPLOAD_FOLDER'], nuevoFilename)
        print('-----foto-path----', nueva_foto)
    else:
        foto_path = None
    print(nueva_foto)

    return inventario.modificar_producto(codigo, nueva_plataforma, nueva_descripcion, nueva_cantidad, nuevo_precio, nuevoFilename)
# 6 - Ruta para eliminar un producto del inventario
# DELETE: permite eliminar información.
@app.route('/productos/<int:codigo>', methods=['DELETE'])
def eliminar_producto(codigo):
    return inventario.eliminar_producto(codigo)

# 7 - Ruta para agregar un producto al carrito
@app.route('/carrito', methods=['POST'])
def agregar_carrito():
    codigo = request.json.get('codigo')
    cantidad = request.json.get('cantidad')
    inventario = Inventario()
    return carrito.agregar(codigo, cantidad, inventario)

# 8 - Ruta para quitar un producto del carrito
@app.route('/carrito', methods=['DELETE'])
def quitar_carrito():
    codigo = request.json.get('codigo')
    cantidad = request.json.get('cantidad')
    inventario = Inventario()
    return carrito.quitar(codigo, cantidad, inventario)

# 9 - Ruta para obtener el contenido del carrito
@app.route('/carrito', methods=['GET'])
def obtener_carrito():
    return carrito.mostrar()

# 10 - Ruta para obtener el index
@app.route('/')
def index():
    return 'API de Inventario'

# Finalmente, si estamos ejecutando este archivo, lanzamos app.
if __name__ == '__main__':
    app.run()