from openai import OpenAI
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify  
import json


# Obtener la clave de API desde la variable de entorno
api_key = os.getenv("OPENAI_API_KEY")
client= OpenAI()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
app = Flask(__name__)

app.secret_key= 'key'

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

        
#####################################################################       
# CONDICIONES OPENAI
def generar_rol(nombre, descripcion):
    system_rol = f"""Hace de cuenta que sos un dinosaurio {nombre} y 
             estás interactuando con niños, de 6 a 10 años, usuarios de una web de información de dinosaurios.
             Te voy a hacer una pregunta respecto a ti (por ejemplo que comes, donde vives) 
             y me tenés que responder como si fueras el {nombre}.
             Puedes usar esta información como referencia: {descripcion}
             No puedes excederte de los 150 tokens, ni hablar de temas que no estén relacionados al {nombre}"""
    return system_rol

def generar_completion(mensajes):
    completion = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=mensajes, 
            max_tokens=150
        )
    return completion

mensajes = []

##################################################################################
# CONTROLADORES

@app.route("/", methods=['GET','POST'])
def dinoWeb():
    mensajes.clear()
    salida = "dinoWeb.html"
    dinos = cargar_datos()
    respuesta = buscar_dino(salida)
    if respuesta:
        return respuesta
    return render_template(salida,dinos=dinos)
        
@app.route('/mostrar/<int:id>', methods=['GET'])
def dinoChat(id):
    salida = "dinoChat.html"
    dinos = cargar_datos()
    dino = next((d for d in dinos if d['id'] == id), None)
    respuesta = buscar_dino(salida)
    if respuesta:
        return respuesta
    return render_template("dinoChat.html", id=id, chat=mensajes, info=dino, dinos=dinos)


def buscar_dino(salida):
    dinos = cargar_datos()
    global mensajes

    if "id" in request.form:
         id_dino = int(request.form['id'])  # Obtiene el valor seleccionado en el formulario
         return redirect(url_for("dinoChat", id=id_dino))
    if "nombreDino" in request.form:
        nombre = request.form['nombreDino'].title()
        dino = next((d for d in dinos if d['Nombre'] == nombre), None)
        if dino:
            id = int(dino['id'])
            system_rol = generar_rol(dino['Nombre'],dino['Descripcion'])
            mensajes = [{"role": "system", "content": system_rol}]
            return redirect(url_for("dinoChat", id=id))
        else:
            flash(f'NO SE ENCONTRÓ EL DINOSAURIO {nombre} ☹ INTÉNTALO DE NUEVO!')
            return render_template(salida)

@app.route('/chatear/<int:id>', methods=['GET','POST'])
def chatear(id):   
    dinos = cargar_datos()
    dino = next((d for d in dinos if d['id'] == id), None)
    global mensajes
    
    if request.method == 'POST':
        data = request.get_json()
        pregunta = data.get('pregunta', '')
        if not mensajes:
            system_rol = generar_rol(dino['Nombre'],dino['Descripcion'])
            mensajes = [{"role": "system", "content": system_rol}]

        mensajes.append({"role": "user", "content": pregunta }) # Agrega la pregunta a la conversación
        completion = generar_completion(mensajes)
        respuesta = completion.choices[0].message.content.upper()
        mensajes.append({"role": "assistant", "content": respuesta})# Agrega la respuesta a la conversación

        return jsonify({"pregunta": pregunta, "respuesta": respuesta})
            
    return jsonify({"error": "Método no permitido"}), 405
        

if __name__ == "__main__":
    app.run(host='0.0.0.0',port="5500", debug=True)   
    
