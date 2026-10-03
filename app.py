import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("Advertencia: Faltan credenciales de Supabase en el archivo .env")


@app.route('/')
def inicio():
    return jsonify({"mensaje": "Bienvenido al API de Tralaladopt"})


@app.route('/registro', methods=['POST'])
def registro():
    datos = request.get_json()
    email = datos.get('email')
    password = datos.get('password')

    if not email or not password:
        return jsonify({"error": "Por favor, envía email y contraseña"}), 400

    try:
        respuesta = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return jsonify({
            "mensaje": "¡Usuario registrado con éxito!", 
            "usuario": respuesta.user.email
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    email = datos.get('email')
    password = datos.get('password')

    if not email or not password:
        return jsonify({"error": "Por favor, envía email y contraseña"}), 400

    try:
        respuesta = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return jsonify({
            "mensaje": "¡Inicio de sesión exitoso!",
            "token": respuesta.session.access_token
        }), 200
    except Exception as e:
        return jsonify({"error": "Correo o contraseña incorrectos"}), 401

if __name__ == '__main__':
    app.run(debug=True)