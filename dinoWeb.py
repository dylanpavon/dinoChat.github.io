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
rol = generar_rol("a definir", "a definir") #Es provisorio para inicializar GPT
mensajes = [{"role": "system", "content": rol}]

completion = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=mensajes, 
            max_tokens=150
        )

##################################################################################
# CONTROLADORES

@app.route("/", methods=['GET','POST'])
def dinoWeb():
    salida = "dinoWeb.html"
    dinos = cargar_datos()
    respuesta = buscar_dino(salida)
    if respuesta:
        return respuesta
    return render_template(salida,dinos=dinos)
        
@app.route('/dinochat', methods=['GET','POST'])
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
        mensajes.clear() #Se vacía la conversación cuando se elige otro dino
        return redirect(url_for("chatear", id=id_dino))
    if "nombreDino" in request.form:
        nombre = request.form['nombreDino'].title()
        dino = next((d for d in dinos if d['Nombre'] == nombre), None)
        if dino:
            mensajes.clear() #Se vacía la conversación cuando se elige otro dino
            id = int(dino['id'])
            system_rol = generar_rol(dino['Nombre'],dino['Descripcion'])
            mensajes = [{"role": "system", "content": system_rol}]
            return redirect(url_for("chatear", id=id))
        else:
            flash(f'NO SE ENCONTRÓ EL DINOSAURIO {nombre} ☹ INTÉNTALO DE NUEVO!')
            return render_template(salida)

@app.route('/dinochat/<int:id>', methods=['GET','POST'])
def chatear(id):   
    dinos = cargar_datos()
    dino = next((d for d in dinos if d['id'] == id), None)
    
    if "pregunta" in request.form:        
        pregunta = "😃➜ " + request.form.get('pregunta')  # Obtiene la pregunta del formulario 
        respuesta = "🦖🦕➜ " + completion.choices[0].message.content.upper()
        mensajes.append({"role": "user", "content": pregunta }) # Agrega la pregunta a la conversación
        mensajes.append({"role": "assistant", "content": respuesta})# Agrega la respuesta a la conversación
    else:
        pass
            
    return render_template("dinoChat.html", id=id, chat=mensajes
                           , info=dino, dinos=dinos)
        

if __name__ == "__main__":
    app.run(host='0.0.0.0',port="5500", debug=True)   
    
