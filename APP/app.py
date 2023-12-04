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
app.config['FOLDER_IMG'] = "Static/img/"
CORS(app)


# tablas
class Receta(db.Model):   
    __tablename__ = "Receta"   
    id = db.Column(db.Integer, primary_key=True)   
    # imagen = db.Column(ForeignKey())
    imagen = db.Column(db.String(100), nullable=False) 
    nombre = db.Column(db.String(100), nullable=False)
    ingredientes = db.Column(db.String(1000), nullable=False)
    instrucciones = db.Column(db.String(1000), nullable=False)
    tiene_alcohol = db.Column(db.String(2), nullable=False)
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
    def get_imagen(self):
        return self.imagen

        



with app.app_context():
    db.create_all()  

# honestamente no tengo idea que es esto pero ayuda a jsonify-ar las bases de datos.
# creo que usa marshmallow

class RecetaSchema(ma.Schema):
    class Meta:
        fields=('id','nombre','imagen','instrucciones','ingredientes','tiene_alcohol')

    




receta_schema=RecetaSchema()            
recetas_schema=RecetaSchema(many=True)

# funciones globales. necesarias para cosas que haremos luego


def delete_image_file(nombre):
    for archivo in os.scandir("./Static/img"):
        if archivo.name == nombre:
            os.remove(archivo)
            return True
    return False
            
def add_imagen(imagen,nombre_cocktail,mantener_original):
    nombre_imagen = secure_filename(imagen.filename)
    original, extension = os.path.splitext(nombre_imagen)
    if mantener_original:
        directorio = f"{nombre_imagen}"
    else:
        directorio = f"cocktail_{nombre_cocktail}{extension}"
    nombre_imagen = directorio
    imagen.save(os.path.join(app.config['FOLDER_IMG'], nombre_imagen))
    return directorio

# rutas
@app.route('/recetas',methods=['GET'])
def get_recetas():
    all_Recetas = Receta.query.all()
    result = recetas_schema.dump(all_Recetas)
    # result = jsonify(result)
    print(result)
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
    new_receta=Receta(nombre,1,instrucciones,ingredientes,tiene_alcohol)
    db.session.add(new_receta)
    db.session.commit()
    new_imagen=add_imagen(imagen,new_receta.id,False)
    new_receta.imagen = new_imagen
    db.session.commit()
    return receta_schema.jsonify(new_receta)

@app.route('/recetas/<id>' ,methods=['PUT'])
def update_receta(id):
    print("Intentando editar receta.")
    receta=Receta.query.get(id)
    nombre=request.form['nombre']
    instrucciones=request.form['instrucciones']
    ingredientes=request.form['ingredientes']
    tiene_alcohol=request.form['alcohol']
    imagen=request.files['imagen']
    old_imagen = receta.imagen
    new_imagen = old_imagen
    try:
        print("Intentando borrar imagen vieja.")
        delete_image_file(f"/app/Static/img/{old_imagen}")
        try:
            print("Intentando agregar nueva imagen.")
            new_imagen=add_imagen(imagen,id,False)
        except Exception as error:
            print(f"Error. Imagen no pudo ser creada.\n{error}")
            return f"Error. Imagen no pudo ser creada.\n{error}"
        
    except Exception as error:
        print(f"Error. Imagen no válida.{error}")
    
    print("Aún intentando editar la receta.")
    receta.imagen=new_imagen
    receta.nombre=nombre
    receta.instrucciones=instrucciones
    receta.ingredientes=ingredientes
    receta.tiene_alcohol=tiene_alcohol
    db.session.commit()
    return receta_schema.jsonify(receta)
 


# main
if __name__=='__main__':  
    app.run(debug=True, port=5000)