from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
import os
app = Flask(__name__)  
CORS(app) 



app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost/db_brindis'
# URI de la BBDD                          driver de la BD  user:clave@URLBBDD/nombreBBDD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #none
db = SQLAlchemy(app)   
ma = Marshmallow(app)   


# tablas
class Ingrediente(db.Model):
    __tablename__ = "Ingrediente"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    # categoria_id = db.Column(db.Integer, ForeignKey("Categorias.id",
                                                    #   ondelete="CASCADE"), nullable=False)
    # id_receta

class ListaIngredientes(db.Model):
    __tablename__ = "ListaIngredientes"
    id = db.Column(db.Integer, primary_key=True)
    medida = db.Column(db.Integer, nullable=False)
    unidad = db.Column(db.String(10), nullable=False)
    ingrediente_id = db.Column(db.Integer, ForeignKey("Ingrediente.id",
                                                      ondelete="CASCADE"), nullable=False)
    receta_id = db.Column(db.Integer, ForeignKey("Receta.id", ondelete="CASCADE"),
                          nullable=False)
    # tiene_alcohol = db.Column(db.Boolean, nullable=False)

class Receta(db.Model):   
    __tablename__ = "Receta"   
    id = db.Column(db.Integer, primary_key=True)   
    imagen = db.Column(db.String(500), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    #ingredientes =  por hacer. investigar como hacer una conexion con la
    # tabla de lista de ingredientes donde la receta acceda a ingredientes
    # pero no visceversa. deberemos poder añadir muchos ingredientes.
    instrucciones = db.Column(db.String(1000), nullable=False)
    tiene_alcohol = db.Column(db.Boolean, nullable=False)
    def __init__(self,nombre,imagen,instrucciones,tiene_alcohol):  
        self.nombre = nombre   
        self.imagen = imagen
        self.instrucciones = instrucciones
        self.tiene_alcohol = tiene_alcohol
    def get_ingredientes(self):
        lista_ingredientes = ListaIngredientes.query.filter_by(receta_id=self.id).all()
        ingredientes = Ingrediente.query.all()
        for ingrediente in ingredientes:
            for cosito in lista_ingredientes:
                if cosito.ingrediente_id == ingrediente.id:
                    cosito.ingrediente_id = ingrediente.nombre
        formato = ListaIngredientes_schema.dump(lista_ingredientes)
        return formato


class Categoria(db.Model):
    __tablename__ = "Categorias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), unique=True)

class Imagen(db.Model):
    __tablename__ = "Imagenes"
    id = db.Column(db.Integer, primary_key=True)
    directorio = db.Column(db.String(500), unique=True)




with app.app_context():
    db.create_all()  


class RecetaSchema(ma.Schema):
    class Meta:
        fields=('id','nombre','imagen','instrucciones','tiene_alcohol')

class ImagenSchema(ma.Schema):
    class Meta:
        fields=('id','directorio')
    
class IngredientesSchema(ma.Schema):
    class Meta:
        fields=('id','medida', 'unidad', 'ingrediente_id', 'receta_id')




Receta_schema=RecetaSchema()            
Recetas_schema=RecetaSchema(many=True)
Imagen_schema=ImagenSchema()            
Imagenes_schema=ImagenSchema(many=True) 
Ingredientes_schema=IngredientesSchema()            
ListaIngredientes_schema=IngredientesSchema(many=True) 

# funciones globales. necesarias para cosas que haremos luego

def update_imagenes(): # obtiene TODAS las imagenes que esten en el directorio static/img.
                 # siempre que se llama, chequea si hay nuevas imagenes y las añade a la DB.
                 # si una imagen fue borrada y sigue en la DB, la elimina.
    imagenes = Imagen.query.all()
    lista = []
    lista2 = []
    for imagen in imagenes:
        lista.append(imagen.directorio)
    for archivo in os.listdir("static/img"):
        lista2.append(archivo)
        if archivo not in lista:
            print(archivo)
            nueva = Imagen(directorio=str(archivo))
            db.session.add(nueva)
            db.session.commit()
    for imagen in lista: # itera sobre la lista en memoria que contiene los directorios
                         # de la tabla de imágenes.
        if imagen not in lista2: # si la imagen NO existe en la lista2, que es la lista con
                                 # los archivos actuales, eliminarla de la base de datos.
            imagen = Imagen.query.filter_by(directorio=str(imagen)).one()
            db.session.delete(imagen)
            db.session.commit()

def get_images():
    imagenes = Imagen.query.all()
    imagenes_lista = [(i.directorio,i.directorio) for i in imagenes]
    return imagenes_lista

# def get_ingredientes(id_receta):
#     lista_ingredientes = ListaIngredientes.query.filter_by(receta_id=id_receta).all()
#     ingredientes = Ingrediente.query.all()
#     for ingrediente in ingredientes:
#         for cosito in lista_ingredientes:
#             if cosito.ingrediente_id == ingrediente.id:
#                 cosito.ingrediente_id = ingrediente.nombre
#     formato = ListaIngredientes_schema.dump(lista_ingredientes)
    
#     return jsonify(formato)


# def getCategorias(): es posible que esta no sea necesaria.
#     categorias = Categoria.query.all()
#     categorias_lista = [(i.nombre_interno,i.nombre_impreso) for i in categorias]
#     return categorias_lista

# rutas
@app.route('/recetas',methods=['GET'])
def get_recetas():
    all_Recetas = Receta.query.all()
    result = Recetas_schema.dump(all_Recetas)
    return jsonify(result)

@app.route('/imagenes',methods=['GET'])
def get_imagenes():
    update_imagenes()
    all_imagenes = Imagen.query.all()
    result = Imagenes_schema.dump(all_imagenes)
    return jsonify(result)

@app.route('/ingredientes/<id>',methods=['GET'])
def display_ingredientes(id):
    receta = Receta.query.filter_by(id=id).one()
    return receta.get_ingredientes()

@app.route('/recetas/<id>',methods=['GET'])
def get_receta(id):
    Receta=Receta.query.get(id)
    return Receta_schema.jsonify(Receta)

@app.route('/recetas/<id>',methods=['DELETE'])
def delete_receta(id):
    Receta=Receta.query.get(id)
    db.session.delete(Receta)
    db.session.commit()
    return Receta_schema.jsonify(Receta)


@app.route('/recetas', methods=['POST'])
def create_receta():
    #print(request.json)  # request.json contiene el json que envio el cliente
    nombre=request.json['nombre']
    tiene_alcohol=request.json['tiene_alcohol']
    imagen=request.json['imagen']
    instrucciones=request.json['instrucciones']
    new_Receta=Receta(nombre,imagen,instrucciones,tiene_alcohol)
    db.session.add(new_Receta)
    db.session.commit()
    return Receta_schema.jsonify(new_Receta)


@app.route('/recetas/<id>' ,methods=['PUT'])
def update_receta(id):
    Receta=Receta.query.get(id)
 
    nombre=request.json['nombre']
    instrucciones=request.json['instrucciones']
    tiene_alcohol=request.json['tiene_alcohol']
    imagen=request.json['imagen']


    Receta.nombre=nombre
    Receta.instrucciones=instrucciones
    Receta.tiene_alcohol=tiene_alcohol
    Receta.imagen=imagen


    db.session.commit()
    return Receta_schema.jsonify(Receta)
 


# main
if __name__=='__main__':  
    app.run(debug=True, port=5000)