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

# MÓDULOS DEL PROYECTO

# Administración - Integrante 5
from modules.admin import (
    cambiar_estado_fundacion,
    obtener_estadisticas_panel,
    obtener_fundaciones_pendientes,
)

# Autenticación
from modules.auth import (
    iniciar_sesion,
    obtener_perfil,
    registrar_usuario,
)

# Animales - Integrante 2
from modules.animals import registrar_rutas_animales

# Solicitudes de adopción - Integrante 2
from modules.adoption_requests import registrar_rutas_adopciones

# Favoritos - Integrante 2
from modules.favorites import registrar_rutas_favoritos


# CONFIGURACIÓN
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "clave_secreta_desarrollo_123"
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client | None = None


# CONEXIÓN A SUPABASE
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

        print("Supabase conectado correctamente.")

    except Exception as err:
        print(
            f"Advertencia: No se pudo conectar "
            f"a Supabase en app.py: {err}"
        )

else:
    print(
        "Advertencia: Faltan credenciales "
        "de Supabase en el archivo .env"
    )


# REGISTRAR MÓDULOS - INTEGRANTE 2
registrar_rutas_animales(app, supabase)
registrar_rutas_adopciones(app, supabase)
registrar_rutas_favoritos(app, supabase)


# INICIO
@app.route("/")
def inicio():
    return redirect(
        url_for("login")
    )


# REGISTRO
@app.route(
    "/registro",
    methods=["GET", "POST"]
)
def registro():

    if request.method == "POST":

        resultado = registrar_usuario(
            request.form
        )

        if resultado["exito"]:
            return redirect(
                url_for("login")
            )

        return render_template(
            "Login/register.html",
            error=resultado.get("error")
        )

    return render_template(
        "Login/register.html"
    )


# LOGIN+
@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get("email")

        resultado = iniciar_sesion(
            email
        )

        if resultado["exito"]:

            session["user_id"] = (
                resultado["usuario"]["id"]
            )

            session["user_role"] = (
                resultado["usuario"]["rol"]
            )

            if (
                resultado["usuario"]["rol"]
                == "administrador"
            ):
                return redirect(
                    url_for("admin_dashboard")
                )

            return redirect(
                url_for("perfil")
            )

        return render_template(
            "Login/login.html",
            error=resultado.get("error")
        )

    return render_template(
        "Login/login.html"
    )

# PERFIL
@app.route("/perfil")
def perfil():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(
            url_for("login")
        )

    usuario = obtener_perfil(
        user_id
    )

    return render_template(
        "Login/profile.html",
        usuario=usuario
    )

# CERRAR SESIÓN
@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )

# ADMINISTRACIÓN - INTEGRANTE 5
@app.route("/admin")
def admin_dashboard():

    if (
        session.get("user_role")
        != "administrador"
    ):
        return redirect(
            url_for("login")
        )

    stats = obtener_estadisticas_panel()

    fundaciones = (
        obtener_fundaciones_pendientes()
    )

    return render_template(
        "Administrador/admin_dashboard.html",
        stats=stats,
        fundaciones=fundaciones
    )


@app.route(
    "/admin/aprobar-fundacion/<id_fundacion>",
    methods=["POST"]
)
def aprobar_fundacion(id_fundacion):

    if (
        session.get("user_role")
        != "administrador"
    ):
        return redirect(
            url_for("login")
        )

    cambiar_estado_fundacion(
        id_fundacion,
        "activo"
    )

    return redirect(
        url_for("admin_dashboard")
    )
    
    

if __name__ == "__main__":
    app.run(debug=True)