from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)  
 



app.config[ 'SQLALCHEMY_DATABASE_URI' ]='mysql+pymysql://root:root@localhost/db_brindis'
# URI de la BBDD                          driver de la BD  user:clave@URLBBDD/nombreBBDD
app.config[ 'SQLALCHEMY_TRACK_MODIFICATIONS' ] = False #none
db = SQLAlchemy(app)   
ma = Marshmallow(app)
app.config['FOLDER_IMG'] = "/Static/img/"   
CORS(app)


# tablas
class Receta(db.Model):   
    __tablename__ = "Receta"   
    id = db.Column(db.Integer, primary_key=True)   
    # imagen = db.Column(ForeignKey())
    imagen = db.Column(db.Integer, ForeignKey("Imagenes.id", ondelete="CASCADE"),
                          nullable=False) 
    nombre = db.Column(db.String(100), nullable=False)
    ingredientes = db.Column(db.String(1000), nullable=False)
    instrucciones = db.Column(db.String(1000), nullable=False)
    tiene_alcohol = db.Column(db.Boolean, nullable=False)
    def __init__(self,nombre,imagen,instrucciones,ingredientes,tiene_alcohol):  
        self.nombre = nombre   
        self.imagen = imagen
        self.instrucciones = instrucciones
        self.ingredientes = ingredientes
        self.tiene_alcohol = tiene_alcohol
    def get_ingredientes(self):
        return jsonify(self.ingredientes.split("*"))
    def get_instrucciones(self):
        return jsonify(self.instrucciones.split("*"))
    

class Imagen(db.Model):
    __tablename__ = "Imagenes"
    id = db.Column(db.Integer, primary_key=True)
    directorio = db.Column(db.String(500), unique=True)
    def __init__(self,imagen,nombre_cocktail,mantener_original):
        nombre_imagen = secure_filename(imagen.filename)
        # original, extension = os.path.splitext(nombre_imagen)
        # if mantener_original:
        #     self.directorio = f"{nombre_imagen}"
        # else:
        #     self.directorio = f"cocktail_{nombre_cocktail}{extension}"
        # nombre_imagen = self.directorio
        imagen.save(os.path.join(app.config['FOLDER_IMG'], nombre_imagen))
        # return jsonify(self)
    # def __init__(self,imagen):
    #     nombre_imagen = secure_filename(imagen.filename)
    #     imagen.save(os.path.join(app.config['FOLDER_IMG'], nombre_imagen))
    #     # original, extension = os.path.splitext(nombre_imagen)
    #     self.directorio = nombre_imagen
    #     return self.id
    def get_directorio(self):
        return self.directorio
    def get_id(self):
        return f"{self.id}"

        



with app.app_context():
    db.create_all()  

# honestamente no tengo idea que es esto pero ayuda a jsonify-ar las bases de datos.
# creo que usa marshmallow

class RecetaSchema(ma.Schema):
    class Meta:
        fields=('id','nombre','imagen','instrucciones','ingredientes','tiene_alcohol')

class ImagenSchema(ma.Schema):
    class Meta:
        fields=('id','directorio')
    




receta_schema=RecetaSchema()            
recetas_schema=RecetaSchema(many=True)
Imagen_schema=ImagenSchema()            
Imagenes_schema=ImagenSchema(many=True) 

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
            nombre = ""
            nueva = Imagen(archivo,nombre,True)
            db.session.add(nueva)
            db.session.commit()
    for imagen in lista: # itera sobre la lista en memoria que contiene los directorios
                         # de la tabla de imágenes.
        if imagen not in lista2: # si la imagen NO existe en la lista2, que es la lista con
                                 # los archivos actuales, eliminarla de la base de datos.
            imagen = Imagen.query.filter_by(directorio=str(imagen)).one()
            db.session.delete(imagen)
            db.session.commit()

def delete_image(id):
    imagen = Imagen.query.filter_by(id=id).one()
    if imagen:
        db.session.delete(imagen)
        db.session.commit()

def get_image(id):
    return Imagen.query.filter_by(id=id).one()

def get_images():
    imagenes = Imagen.query.all()
    imagenes_lista = [(i.directorio,i.directorio) for i in imagenes]
    return imagenes_lista

# def get_ingredientes(id_receta): ahora es un metodo de la clase Receta.
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
    result = recetas_schema.dump(all_Recetas)
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
    receta=Receta.query.get(id)
    return receta_schema.jsonify(receta)

@app.route('/recetas/<id>/instrucciones',methods=['GET'])
def get_instrucciones(id):
    receta=Receta.query.get(id)
    return receta.get_instrucciones()

@app.route('/recetas/<id>',methods=['DELETE'])
def delete_receta(id):
    receta=Receta.query.get(id)
    db.session.delete(receta)
    db.session.commit()
    return receta_schema.jsonify(receta)

@app.route('/recetas', methods=['POST'])
def create_receta():
    # print(request.json)  # request.json contiene el json que envio el cliente
    nombre=request.form['nombre']
    tiene_alcohol=request.form['alcohol']
    imagen=request.files['imagen']
    instrucciones=request.form['instrucciones']
    ingredientes=request.form['ingredientes']
    # new_imagen=Imagen(imagen,nombre,False)
    # db.session.add(new_imagen)
    # db.session.commit()
    nombre_imagen = secure_filename(imagen.filename)
    imagen.save(os.path.join(app.config['FOLDER_IMG'], nombre_imagen))
    new_receta=Receta(nombre,1,instrucciones,ingredientes,tiene_alcohol)
    db.session.add(new_receta)
    db.session.commit()
    return receta_schema.jsonify(new_receta)

@app.route('/recetas/<id>' ,methods=['PUT'])
def update_receta(id):
    receta=Receta.query.get(id)
 
    nombre=request.form['nombre']
    instrucciones=request.form['instrucciones']
    ingredientes=request.form['ingredientes']
    tiene_alcohol=request.form['alcohol']
    imagen=request.file['imagen']
    delete_image(receta.imagen)
    new_imagen=Imagen(imagen,nombre,False)
    receta.nombre=nombre
    receta.instrucciones=instrucciones
    receta.ingredientes=ingredientes
    receta.tiene_alcohol=tiene_alcohol
    
    receta.imagen=new_imagen.get_id()

    db.session.add(new_imagen)
    db.session.commit()
    return receta_schema.jsonify(receta)
 


# main
if __name__=='__main__':  
    app.run(debug=True, port=5000)