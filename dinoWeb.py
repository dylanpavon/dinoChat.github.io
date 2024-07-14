from openai import OpenAI
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify  
#import mysql.connector
import json

# Obtener la clave de API desde la variable de entorno
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    print("No se encontró la clave de API. Asegúrate de que la variable de entorno OPENAI_API_KEY esté configurada.")
else:
    print("Clave de API encontrada: ", api_key)

client= OpenAI()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
dino_web = Flask(__name__)
# conexion_db = mysql.connector.connect(user="root", password="root", host="localhost", database="dino_web", port="3306")
# query = conexion_db.cursor()

# if conexion_db.is_connected():
#     print("CONEXION OK")

dino_web.secret_key= 'key'

#query.execute("SELECT * FROM dino ORDER BY Nombre")
#dinos = query.fetchall()
#for d in dinos:
#   query.execute(f"UPDATE dino SET imagen = '../static/Imagenes/{d[1]}.jpg' WHERE id = {d[0]}")
#   conexion_db.commit()

def cargar_datos():
    with open('Dinos.json', 'r', encoding='utf-8') as file:
        return json.load(file)   

################################################################################################
# CLASE

class Dino:
    def __init__(self, nombre, descripcion, id):
        self.nombre = nombre
        self.descripcion = descripcion
        self.id = id
        
        
    def conversar(self, nombre, descripcion, pregunta):
        system_rol = f"""Hace de cuenta que sos un dinosaurio {nombre} y 
             estás interactuando con niños, de 6 a 10 años, usuarios de una web de información de dinosaurios.
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
        respuesta = "🦖🦕➜ " + completion.choices[0].message.content.upper()
        mensajes.append({"role": "assistant", "content": respuesta})
        
        return respuesta

##################################################################################
# CONTROLADORES

@dino_web.route("/", methods=['GET','POST'])
def dinoWeb():
    salida = "dinoWeb.html"
    dinos = cargar_datos()
    respuesta = buscar_dino(salida)
    if respuesta:
        return respuesta
    return render_template(salida,dinos=dinos)
        
conversacion=[] #Lo dejo afuera para que guarde y muestre la conversacion sin reiniciarse vacía   
@dino_web.route('/dinochat', methods=['GET','POST'])
def dinoChat():
    salida = "dinoChat.html"
    dinos = cargar_datos()
    respuesta = buscar_dino(salida)
    if respuesta:
        return respuesta
    return render_template(salida,dinos=dinos)

def buscar_dino(salida):
    dinos = cargar_datos()

    if "id" in request.form:
        id_dino = int(request.form['id'])  # Obtiene el valor seleccionado en el formulario
        conversacion.clear() #Se vacía la conversación cuando se elige otro dino
        return redirect(url_for("chatear", id=id_dino))
    if "nombreDino" in request.form:
        nombre = request.form['nombreDino'].title()
        dino = next((d for d in dinos if d['Nombre'] == nombre), None)
        if dino:
            id = int(dino['id'])
            conversacion.clear() #Se vacía la conversación cuando se elige otro dino
            return redirect(url_for("chatear", id=id))
        else:
            flash(f'NO SE ENCONTRÓ EL DINOSAURIO {nombre} ☹ INTÉNTALO DE NUEVO!')
            return render_template(salida)

@dino_web.route('/dinochat/<int:id>', methods=['GET','POST'])
def chatear(id):   
    dinos = cargar_datos()
    dino = next((d for d in dinos if d['id'] == id), None)
    dinox = Dino(dino['Nombre'],dino['Descripcion'],id)
    
    
    if "pregunta" in request.form:        
        pregunta = "😃➜ " + request.form.get('pregunta')  # Obtiene la pregunta del formulario        
        respuesta = dinox.conversar(dinox.nombre, dinox.descripcion, pregunta)
        conversacion.append(pregunta)  # Agrega la pregunta a la conversación
        conversacion.append(respuesta)  # Agrega la respuesta a la conversación
    else:
        conversacion.clear()
            
    return render_template("dinoChat.html", id=id, chat=conversacion, info=dino, dinos=dinos)
        

if __name__ == "__main__":
    dino_web.run(host='0.0.0.0',port="5500", debug=True)    
    
    
