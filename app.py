import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask, render_template, redirect, url_for
from modules.admin import (
    obtener_estadisticas_panel,
    obtener_fundaciones_pendientes,
    cambiar_estado_fundacion,
)

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

@app.route("/admin")
def admin_dashboard():
    stats = obtener_estadisticas_panel()
    fundaciones = obtener_fundaciones_pendientes()
    return render_template(
        "admin_dashboard.html", stats=stats, fundaciones=fundaciones
    )


@app.route("/admin/aprobar-fundacion/<id_fundacion>", methods=["POST"])
def aprobar_fundacion(id_fundacion):
    cambiar_estado_fundacion(id_fundacion, "activo")
    return redirect(url_for("admin_dashboard"))
    






if __name__ == '__main__':
    app.run(debug=True) 













