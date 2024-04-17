from openai import OpenAI
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector


# Obtener la clave de API desde la variable de entorno
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    print("No se encontró la clave de API. Asegúrate de que la variable de entorno OPENAI_API_KEY esté configurada.")
else:
    print("Clave de API encontrada: ", api_key)

client= OpenAI()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
dino_web = Flask(__name__)
conexion_db = mysql.connector.connect(user="root", password="root", host="localhost", database="dino_web", port="3306")
query = conexion_db.cursor()

if conexion_db.is_connected():
    print("CONEXION OK")

dino_web.secret_key= 'key'

#query.execute("SELECT * FROM dino ORDER BY Nombre")
#dinos = query.fetchall()
#for d in dinos:
#   query.execute(f"UPDATE dino SET imagen = '../static/Imagenes/{d[1]}.jpg' WHERE id = {d[0]}")
#   conexion_db.commit()

    

################################################################################################
# CLASE

class Dino:
    def __init__(self, nombre, descripcion, id):
        self.nombre = nombre
        self.descripcion = descripcion
        self.id = id
        
        
    def obtener_nombre(id):
        query.execute(f'SELECT nombre FROM dino WHERE id = {id};')
        nombre = query.fetchone()
        nombre = nombre[0]
        
    def obtener_descripcion(id):
        query.execute(f'SELECT descripcion FROM dino WHERE id = {id};')
        descripcion = query.fetchone()
        descripcion = descripcion[0]      
  

    def conversar(self, nombre, descripcion, pregunta):
        system_rol = f"""Hace de cuenta que sos un dinosaurio {nombre} y 
             estás interactuando con usuarios de una web de información de dinosaurios.
             Te voy a hacer una pregunta respecto a ti (por ejemplo que comes, donde vives) 
             y me tenés que responder como si fueras el {nombre}.
             Puedes usar esta información como referencia: {descripcion}
             No puedes excederte de los 150 tokens, ni hablar de temas que no estén relacionados al {nombre}"""
        mensajes = [{"role": "system", "content": system_rol}]
        user_prompt = pregunta 
        mensajes.append({"role": "user", "content": user_prompt})
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=mensajes, 
            max_tokens=150
        )
        respuesta = "🦖🦕➜ " + completion.choices[0].message.content
        mensajes.append({"role": "assistant", "content": respuesta})
        
        return respuesta

##################################################################################
# CONTROLADORES

conversacion=[] #Lo dejo afuera para que guarde y muestre la conversacion sin reiniciarse vacía
@dino_web.route("/", methods=['GET','POST'])
def dinoWeb():
    query.execute("SELECT * FROM dino ORDER BY Nombre")
    dinos = query.fetchall()
    if "nombreDino" in request.form:
        nombre = request.form['nombreDino']
        query.execute(f"SELECT * FROM dino WHERE nombre='{nombre}'")
        info_dino = query.fetchall()# Obtiene el valor seleccionado en el formulario
        if info_dino:
            id_dino= info_dino[0][0]
            conversacion.clear() #Se vacía la conversación cuando se elige otro dino
            return redirect(url_for("chatear", id=id_dino))
        else:
            flash(f'No se encontró el dinosaurio {nombre} ☹ Inténtalo de nuevo!')
            conversacion.clear() #Se vacía la conversación cuando se elige otro dino
    return render_template("dinoWeb.html", dinos=dinos)
        
conversacion=[] #Lo dejo afuera para que guarde y muestre la conversacion sin reiniciarse vacía   
@dino_web.route('/dinochat', methods=['GET','POST'])
def elegir_dino():   
    query.execute("SELECT * FROM dino ORDER BY Nombre")
    dinos = query.fetchall()
    
    if "id" in request.form:
        id_dino = int(request.form['id'])  # Obtiene el valor seleccionado en el formulario
        conversacion.clear() #Se vacía la conversación cuando se elige otro dino
        return redirect(url_for("chatear", id=id_dino))
    if "nombreDino" in request.form:
        nombre = request.form['nombreDino']
        query.execute(f"SELECT * FROM dino WHERE nombre='{nombre}'")
        info_dino = query.fetchall()# Obtiene el valor seleccionado en el formulario
        if info_dino:
            id_dino= info_dino[0][0]
            #conversacion.clear() #Se vacía la conversación cuando se elige otro dino
            return redirect(url_for("chatear", id=id_dino))
        else:
            flash(f'No se encontró el dinosaurio {nombre} ☹ Inténtalo de nuevo!')
            #conversacion.clear() #Se vacía la conversación cuando se elige otro dino
    return render_template("dinoChat.html", dinos=dinos)

@dino_web.route('/dinochat/<int:id>', methods=['GET','POST'])
def chatear(id):   
    query.execute("SELECT * FROM dino ORDER BY Nombre")
    dinos = query.fetchall()  
    info_dino = [] 
    query.execute(f"SELECT * FROM dino WHERE id = {id}")
    info_dino = query.fetchall()
    dino = Dino(info_dino[0][1], info_dino[0][2], id)
    
    
    if "pregunta" in request.form:        
        pregunta = "😃➜ " + request.form.get('pregunta')  # Obtiene la pregunta del formulario        
        respuesta = dino.conversar(dino.nombre, dino.descripcion, pregunta)
        conversacion.append(pregunta)  # Agrega la pregunta a la conversación
        conversacion.append(respuesta)  # Agrega la respuesta a la conversación
    else:
        conversacion.clear()
            
    return render_template("dinoChat.html", id=id, chat=conversacion, info=info_dino, dinos=dinos)
        

if __name__ == "__main__":
    dino_web.run(port="5500", debug=True)
    
    
