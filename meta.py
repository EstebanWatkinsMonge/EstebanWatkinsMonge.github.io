from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

# Conectar a MongoDB (servidor local en puerto 27017)
usuario = MongoClient('mongodb+srv://ewatkinsm895:Stbwtk07@cluster0.zlvtlhj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = usuario['colegio']               # Base de datos "colegio"
coleccion = db['estudiantes']          # Colección "estudiantes"

app = Flask(__name__)

# Leer todos los estudiantes (GET /estudiantes)
@app.route('/estudiantes', methods=['GET'])
def obtener_estudiantes():
    documentos = list(coleccion.find())  # Obtenemos todos los documentos
    # Convertir ObjectId a cadena para cada documento
    for doc in documentos:
        doc['_id'] = str(doc['_id'])
    return jsonify(documentos)  # Devolvemos la lista de documentos como JSON

# Leer un estudiantes por ID (GET /estudiantes/<id>)
@app.route('/estudiantes/<id>', methods=['GET'])
def obtener_estudiante(id):
    try:
        obj_id = ObjectId(id)
    except Exception as e:
        return jsonify({"error": "ID inválido"}), 400
    documento = coleccion.find_one({"_id": obj_id})
    if documento:
        documento['_id'] = str(documento['_id'])
        return jsonify(documento)
    else:
        return jsonify({"error": "estudiante no encontrado"}), 404

# Crear un nuevo estudiantes (POST /estudiantes)
@app.route('/estudiantes', methods=['POST'])
def crear_estudiante():
    datos = request.get_json()  # Equivalent to req.body en Flask
    if not datos or not datos.get('nombre') or datos.get('cedula') is None:
        return jsonify({"error": "Datos incompletos"}), 400
    resultado = coleccion.insert_one({
        "nombre": datos['nombre'],
        "cedula": datos['cedula']
    })
    # Obtener el id insertado
    nuevo_id = resultado.inserted_id
    return jsonify({
        "_id": str(nuevo_id),
        "nombre": datos['nombre'],
        "cedula": datos['cedula']
    }), 201

# Actualizar un estudiante (PUT /estudiantes/<id>)
@app.route('/estudiantes/<id>', methods=['PUT'])
def actualizar_estudiante(id):
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se proporcionaron datos"}), 400
    try:
        obj_id = ObjectId(id)
    except Exception:
        return jsonify({"error": "ID inválido"}), 400
    # Construir el diccionario de campos a actualizar, excluyendo _id si viene
    campos_a_actualizar = { k: v for k, v in datos.items() if k != '_id' }
    resultado = coleccion.update_one({"_id": obj_id}, {"$set": campos_a_actualizar})
    if resultado.matched_count == 0:
        return jsonify({"error": "estudiante no encontrado"}), 404
    # matched_count > 0 significa que encontró el documento; ahora ver si modificó algo
    if resultado.modified_count == 0:
        return jsonify({"mensaje": "No hubo cambios"}), 200
    return jsonify({"mensaje": "estudiante actualizado correctamente"}), 200

# Borrar un estudiante (DELETE /estudiantes/<id>)
@app.route('/estudiantes/<id>', methods=['DELETE'])
def eliminar_estudiante(id):
    try:
        obj_id = ObjectId(id)
    except Exception:
        return jsonify({"error": "ID inválido"}), 400
    resultado = coleccion.delete_one({"_id": obj_id})
    if resultado.deleted_count == 0:
        return jsonify({"error": "estudiante no encontrado"}), 404
    return jsonify({"mensaje": "estudiante eliminado correctamente"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
