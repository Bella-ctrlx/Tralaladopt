import os
from dotenv import load_dotenv
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from supabase import Client, create_client

from modules.admin import (
    cambiar_estado_fundacion,
    obtener_estadisticas_panel,
    obtener_fundaciones_pendientes,
)
from modules.auth import iniciar_sesion, obtener_perfil, registrar_usuario

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Clave secreta necesaria para que Flask gestione las sesiones de usuario
app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave_secreta_desarrollo_123")
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
    return redirect(url_for("login"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        resultado = registrar_usuario(request.form)
        if resultado["exito"]:
            return redirect(url_for("login"))
        return render_template("registro.html", error=resultado.get("error"))

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        resultado = iniciar_sesion(email)

        if resultado["exito"]:
            # Guarda los datos claves del usuario en la sesión de Flask
            session["user_id"] = resultado["usuario"]["id"]
            session["user_role"] = resultado["usuario"]["rol"]

            # Redirección según el rol de la cuenta
            if resultado["usuario"]["rol"] == "administrador":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("perfil"))

        return render_template("login.html", error=resultado.get("error"))

    return render_template("login.html")


@app.route("/perfil")
def perfil():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    usuario = obtener_perfil(user_id)
    return render_template("profile.html", usuario=usuario)


@app.route("/logout")
def logout():
    # Limpia la sesión actual
    session.clear()
    return redirect(url_for("login"))


# --- RUTAS MÓDULO ADMINISTRACIÓN (INTEGRANTE 5) ---


@app.route("/admin")
def admin_dashboard():
    # Protección de ruta: Solo administradores pueden ingresar
    if session.get("user_role") != "administrador":
        return redirect(url_for("login"))

    stats = obtener_estadisticas_panel()
    fundaciones = obtener_fundaciones_pendientes()
    return render_template(
        "admin_dashboard.html", stats=stats, fundaciones=fundaciones
    )


@app.route("/admin/aprobar-fundacion/<id_fundacion>", methods=["POST"])
def aprobar_fundacion(id_fundacion):
    if session.get("user_role") != "administrador":
        return redirect(url_for("login"))

    cambiar_estado_fundacion(id_fundacion, "activo")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)