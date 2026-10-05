import os
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from supabase import Client, create_client
from modules.fundaciones import fundaciones_bp

from modules.admin import (
    cambiar_estado_fundacion,
    obtener_estadisticas_panel,
    obtener_fundaciones_pendientes,
)

load_dotenv()

app = Flask(__name__)
app.register_blueprint(fundaciones_bp)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client | None = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as err:
        print(f"Advertencia: No se pudo conectar a Supabase en app.py: {err}")
else:
    print("Advertencia: Faltan credenciales de Supabase en el archivo .env")


@app.route("/")
def inicio():
    return jsonify({"mensaje": "Bienvenido al API de Tralaladopt"})


@app.route("/registro", methods=["POST"])
def registro():
    if not supabase:
        return jsonify({"error": "Servicio de base de datos no disponible"}), 500

    datos = request.get_json() or {}
    email = datos.get("email")
    password = datos.get("password")

    if not email or not password:
        return jsonify({"error": "Por favor, envía email y contraseña"}), 400

    try:
        respuesta = supabase.auth.sign_up(
            {"email": email, "password": password}
        )
        return (
            jsonify(
                {
                    "mensaje": "¡Usuario registrado con éxito!",
                    "usuario": respuesta.user.email if respuesta.user else None,
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/login", methods=["POST"])
def login():
    if not supabase:
        return jsonify({"error": "Servicio de base de datos no disponible"}), 500

    datos = request.get_json() or {}
    email = datos.get("email")
    password = datos.get("password")

    if not email or not password:
        return jsonify({"error": "Por favor, envía email y contraseña"}), 400

    try:
        respuesta = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        token = (
            respuesta.session.access_token if respuesta.session else None
        )
        return (
            jsonify(
                {
                    "mensaje": "¡Inicio de sesión exitoso!",
                    "token": token,
                }
            ),
            200,
        )
    except Exception:
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


if __name__ == "__main__":
    app.run(debug=True)

    