from flask import Flask, jsonify, request, render_template, g, abort, session, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import *
from jinja2 import *
import os
app = Flask(__name__)  
 



app.config[ 'SQLALCHEMY_DATABASE_URI' ]='mysql+pymysql://root:root@localhost/db_brindis'
# URI de la BBDD                          driver de la BD  user:clave@URLBBDD/nombreBBDD
app.config[ 'SQLALCHEMY_TRACK_MODIFICATIONS' ] = False #none
db = SQLAlchemy(app)   
ma = Marshmallow(app)
app.config['FOLDER_IMG'] = "Static/img/"
app.config['SECRET_KEY'] = 'laspatatassonhechasconquesodepapas'
login_manager = LoginManager()
login_manager.init_app(app)
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
        return self.ingredientes.split("*")
    def get_instrucciones(self):
        return self.instrucciones.split("*")
    def get_imagen(self):
        return f"/img/{self.imagen}"
    def get_itself(self):
        return jsonify(receta_schema.dump(self))

class Usuario(UserMixin, db.Model):
    __tablename__ = "Usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(60), unique=True)
    codigo = db.Column(db.String(128), nullable=False) 
    email = db.Column(db.String(150), unique=True)
    rol = db.Column(db.Integer, nullable=False)

    @property
    def password(self):
        return AttributeError("La contraseña no es visible")
    @password.setter
    def password(self, password):
        self.codigo = generate_password_hash(password)
    def checkPassword(self, password):
        return check_password_hash(self.codigo, password) #es asi?
        



with app.app_context():
    db.create_all()  

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
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

# rutas de la página

@app.route('/')
def index():
    recetas = Receta.query.all()
    ultimas = []
    i = 1
    for receta in recetas:
        if i <= 4:
            ultimas.append(receta)
            # print(receta.get_itself())
            print(receta.nombre)
        i += 1
    return render_template('index.html', ultimas=ultimas)

@app.route('/recetas/<id>')
def detalles_receta(id):
    return render_template('receta.html', receta=get_receta(id))

@app.route('/recetas')
def show_all_recetas():
    return render_template('recetas_todas.html', recetas=get_recetas())



# rutas del API 

@app.route('/api/recetas',methods=['GET'])
def get_recetas():
    all_Recetas = Receta.query.all()
    result = recetas_schema.dump(all_Recetas)
    return all_Recetas

@app.route('/api/ingredientes/<id>',methods=['GET'])
def display_ingredientes(id):
    receta = Receta.query.filter_by(id=id).one()
    return receta.get_ingredientes()

@app.route('/api/recetas/<id>',methods=['GET'])
def get_receta(id):
    receta=Receta.query.get(id)
    return receta

@app.route('/api/recetas/<id>/instrucciones',methods=['GET'])
def get_instrucciones(id):
    receta=Receta.query.get(id)
    return receta.get_instrucciones()

@app.route('/api/recetas/<id>',methods=['DELETE'])
def delete_receta(id):
    receta=Receta.query.get(id)
    db.session.delete(receta)
    db.session.commit()
    return receta_schema.jsonify(receta)

@app.route('/api/recetas', methods=['POST'])
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

@app.route('/api/recetas/<id>' ,methods=['PUT'])
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