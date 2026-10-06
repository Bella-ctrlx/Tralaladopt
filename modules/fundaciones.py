"""Módulo de fundaciones y donaciones de Tralaladopt.

Reglas de acceso:
- Visitante: puede enviar una solicitud para registrar una fundación.
- Adoptante: puede ver fundaciones activas y donar.
- Fundación: puede ver fundaciones y solo el historial de donaciones de su cuenta.
- Administrador: puede ver fundaciones y aprobar/rechazar solicitudes; no dona.
"""

import re
from decimal import Decimal, InvalidOperation
from uuid import UUID

from flask import Blueprint, redirect, render_template, request, session, url_for

from modules.admin import supabase

fundaciones_bp = Blueprint("fundaciones", __name__, url_prefix="/fundaciones")

TABLA_USUARIOS = "users"
TABLA_DONACIONES = "donaciones"
TABLA_NOTIFICACIONES = "notificaciones"

MONTO_MAXIMO = Decimal("99999999.99")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MSG_SIN_BD = "El servicio de base de datos no está disponible."
MSG_ERROR_BD = "No se pudo completar la operación. Inténtalo más tarde."
ESTADOS_ACCION = {"aprobar": "activo", "rechazar": "rechazado"}


def _texto(datos, campo: str) -> str:
    return str(datos.get(campo) or "").strip()


def _es_uuid(valor: str) -> bool:
    try:
        UUID(valor)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def _rol_actual() -> str:
    rol = str(session.get("user_role") or "").strip().lower()
    return "administrador" if rol == "admin" else rol


def _usuario_actual() -> dict | None:
    """Obtiene la fila del usuario conectado a partir de session['user_id']."""
    user_id = session.get("user_id")
    if not user_id or not supabase:
        return None
    try:
        respuesta = (
            supabase.table(TABLA_USUARIOS)
            .select("id,nombre,email,rol,estado")
            .eq("id", user_id)
            .single()
            .execute()
        )
        return respuesta.data
    except Exception as err:
        print(f"Error al obtener usuario actual en fundaciones: {err}")
        return None


def validar_fundacion(datos) -> tuple[dict, list[str]]:
    campos = (
        "nombre", "email", "biografia", "ubicacion", "telefono", "sitio_web"
    )
    limpio = {campo: _texto(datos, campo) for campo in campos}
    errores = []

    if not limpio["nombre"]:
        errores.append("El nombre de la fundación es obligatorio.")
    elif len(limpio["nombre"]) > 100:
        errores.append("El nombre no puede superar los 100 caracteres.")

    if not EMAIL_RE.match(limpio["email"]) or len(limpio["email"]) > 100:
        errores.append("Ingresa un correo electrónico válido (máx. 100).")

    if len(limpio["ubicacion"]) > 100:
        errores.append("La ubicación no puede superar los 100 caracteres.")
    if len(limpio["telefono"]) > 20:
        errores.append("El teléfono no puede superar los 20 caracteres.")
    if len(limpio["sitio_web"]) > 150:
        errores.append("El sitio web no puede superar los 150 caracteres.")
    if len(limpio["biografia"]) > 1000:
        errores.append("La descripción no puede superar los 1000 caracteres.")

    return limpio, errores


def validar_donacion(datos) -> tuple[dict, list[str]]:
    limpio = {
        "fundacion_id": _texto(datos, "fundacion_id"),
        "mensaje": _texto(datos, "mensaje"),
        "correo_donante": _texto(datos, "correo_donante"),
        "monto": None,
    }
    errores = []

    if not _es_uuid(limpio["fundacion_id"]):
        errores.append("Selecciona una fundación válida.")
    if not EMAIL_RE.match(limpio["correo_donante"]):
        errores.append("Ingresa el correo de la cuenta del donante.")
    if len(limpio["mensaje"]) > 500:
        errores.append("El mensaje no puede superar los 500 caracteres.")

    texto_monto = _texto(datos, "monto").replace(",", ".")
    try:
        monto = Decimal(texto_monto).quantize(Decimal("0.01"))
        if not monto.is_finite() or monto <= 0:
            errores.append("El monto debe ser mayor que 0.")
        elif monto > MONTO_MAXIMO:
            errores.append("El monto supera el máximo permitido.")
        else:
            limpio["monto"] = monto
    except (InvalidOperation, ValueError):
        errores.append("El monto debe ser un número (ejemplo: 25.50).")

    return limpio, errores


def registrar_fundacion(datos: dict) -> dict:
    if not supabase:
        return {"exito": False, "error": MSG_SIN_BD}

    try:
        existe = (
            supabase.table(TABLA_USUARIOS)
            .select("id")
            .eq("email", datos["email"])
            .execute()
        )
        if existe.data:
            return {"exito": False, "error": "Ese correo ya está registrado."}

        fila = {clave: valor or None for clave, valor in datos.items()}
        fila.update({"rol": "fundacion", "estado": "pendiente"})
        supabase.table(TABLA_USUARIOS).insert(fila).execute()
        return {"exito": True}
    except Exception as err:
        print(f"Error al registrar fundación: {err}")
        return {"exito": False, "error": MSG_ERROR_BD}


def _listar_fundaciones(estado: str, columnas: str) -> list[dict]:
    if not supabase:
        return []

    try:
        respuesta = (
            supabase.table(TABLA_USUARIOS)
            .select(columnas)
            .eq("rol", "fundacion")
            .eq("estado", estado)
            .order("nombre")
            .execute()
        )
        return respuesta.data or []
    except Exception as err:
        print(f"Error al listar fundaciones ({estado}): {err}")
        return []


def listar_fundaciones_activas() -> list[dict]:
    return _listar_fundaciones(
        "activo", "id,nombre,email,ubicacion,biografia,sitio_web"
    )


def listar_fundaciones_pendientes() -> list[dict]:
    return _listar_fundaciones(
        "pendiente", "id,nombre,email,ubicacion,fecha_creacion"
    )


def cambiar_estado_fundacion(id_fundacion: str, accion: str) -> dict:
    if accion not in ESTADOS_ACCION or not _es_uuid(id_fundacion):
        raise ValueError("Solicitud no válida.")
    if not supabase:
        return {"exito": False, "error": MSG_SIN_BD}

    estado = ESTADOS_ACCION[accion]
    try:
        respuesta = (
            supabase.table(TABLA_USUARIOS)
            .update({"estado": estado})
            .eq("id", id_fundacion)
            .eq("rol", "fundacion")
            .execute()
        )
        if not respuesta.data:
            return {"exito": False, "error": "No se encontró la fundación."}
    except Exception as err:
        print(f"Error al cambiar estado de fundación: {err}")
        return {"exito": False, "error": MSG_ERROR_BD}

    _notificar(
        id_fundacion,
        f"El estado de tu cuenta de fundación cambió a: {estado}.",
        "admin",
    )
    return {"exito": True}


def _notificar(usuario_id: str, mensaje: str, tipo: str) -> None:
    if not supabase:
        return
    try:
        supabase.table(TABLA_NOTIFICACIONES).insert(
            {"usuario_id": usuario_id, "mensaje": mensaje, "tipo": tipo}
        ).execute()
    except Exception as err:
        print(f"No se pudo guardar la notificación: {err}")


def registrar_donacion(datos: dict) -> dict:
    if not supabase:
        return {"exito": False, "error": MSG_SIN_BD}

    try:
        fundacion = (
            supabase.table(TABLA_USUARIOS)
            .select("id")
            .eq("id", datos["fundacion_id"])
            .eq("rol", "fundacion")
            .eq("estado", "activo")
            .execute()
        )
        if not fundacion.data:
            return {"exito": False, "error": "La fundación no está activa."}

        donante = (
            supabase.table(TABLA_USUARIOS)
            .select("id,rol")
            .eq("email", datos["correo_donante"])
            .execute()
        )
        if not donante.data:
            return {
                "exito": False,
                "error": "No hay una cuenta con el correo del donante.",
            }
        if donante.data[0].get("rol") != "adoptante":
            return {
                "exito": False,
                "error": "Solo las cuentas adoptantes pueden realizar donaciones.",
            }

        supabase.table(TABLA_DONACIONES).insert(
            {
                "donante_id": donante.data[0]["id"],
                "fundacion_id": datos["fundacion_id"],
                "monto": str(datos["monto"]),
                "mensaje": datos["mensaje"] or None,
            }
        ).execute()
    except Exception as err:
        print(f"Error al registrar donación: {err}")
        return {"exito": False, "error": MSG_ERROR_BD}

    _notificar(
        datos["fundacion_id"],
        f"Recibiste una donación de {datos['monto']}.",
        "donacion",
    )
    return {"exito": True}


def _nombres_usuarios(ids: list[str]) -> dict:
    if not ids or not supabase:
        return {}
    respuesta = (
        supabase.table(TABLA_USUARIOS)
        .select("id,nombre")
        .in_("id", list(set(ids)))
        .execute()
    )
    return {fila["id"]: fila["nombre"] for fila in respuesta.data or []}


def obtener_historial(email: str = "", fundacion_id: str = "") -> dict:
    if not supabase:
        return {"exito": False, "error": MSG_SIN_BD}
    if not email and not fundacion_id:
        return {"exito": False, "error": "Indica un correo o una fundación."}
    if fundacion_id and not _es_uuid(fundacion_id):
        return {"exito": False, "error": "La fundación indicada no es válida."}

    try:
        consulta = supabase.table(TABLA_DONACIONES).select("*")

        if email:
            donante = (
                supabase.table(TABLA_USUARIOS)
                .select("id")
                .eq("email", email)
                .execute()
            )
            if not donante.data:
                return {"exito": True, "datos": []}
            consulta = consulta.eq("donante_id", donante.data[0]["id"])

        if fundacion_id:
            consulta = consulta.eq("fundacion_id", fundacion_id)

        filas = (
            consulta.order("fecha_creacion", desc=True).limit(100).execute()
        ).data or []
        ids = [f[c] for f in filas for c in ("fundacion_id", "donante_id")]
        nombres = _nombres_usuarios([i for i in ids if i])
        datos = [
            {
                "fecha": str(f.get("fecha_creacion", ""))[:10],
                "fundacion": nombres.get(f.get("fundacion_id"), "—"),
                "donante": nombres.get(f.get("donante_id"), "—"),
                "monto": f.get("monto"),
                "estado": f.get("estado"),
                "mensaje": f.get("mensaje") or "",
            }
            for f in filas
        ]
        return {"exito": True, "datos": datos}
    except Exception as err:
        print(f"Error al consultar historial: {err}")
        return {"exito": False, "error": MSG_ERROR_BD}


def _pagina(seccion: str, **contexto):
    base = {
        "seccion": seccion,
        "errores": [],
        "mensaje": "",
        "form": {},
        "fundaciones": [],
        "pendientes": [],
        "historial": None,
        "usuario_actual": _usuario_actual(),
        "rol_actual": _rol_actual(),
    }
    base.update(contexto)
    return render_template("Fundations/fundaciones.html", **base)


@fundaciones_bp.route("/")
def listado():
    """Todos los usuarios autenticados pueden ver fundaciones activas."""
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return _pagina("listado", fundaciones=listar_fundaciones_activas())


@fundaciones_bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Solicitud pública de alta de fundación; no disponible con sesión activa."""
    if session.get("user_id"):
        return redirect(url_for("inicio"))

    if request.method == "GET":
        return _pagina("registro")

    limpio, errores = validar_fundacion(request.form)
    if not errores:
        resultado = registrar_fundacion(limpio)
        if resultado["exito"]:
            return _pagina(
                "registro",
                mensaje=(
                    "Registro recibido. Tu cuenta quedó pendiente y un "
                    "administrador deberá aprobarla antes de iniciar sesión."
                ),
            )
        errores.append(resultado["error"])

    return _pagina("registro", errores=errores, form=limpio)


@fundaciones_bp.route("/donar", methods=["GET", "POST"])
def donar():
    """Solo los adoptantes autenticados pueden donar."""
    if not session.get("user_id"):
        return redirect(url_for("login"))
    if _rol_actual() != "adoptante":
        return redirect(url_for("inicio"))

    usuario = _usuario_actual()
    if not usuario:
        return redirect(url_for("login"))

    fundaciones = listar_fundaciones_activas()
    form_inicial = {"correo_donante": usuario.get("email", "")}

    if request.method == "GET":
        return _pagina(
            "donar",
            fundaciones=fundaciones,
            form=form_inicial,
            usuario_actual=usuario,
        )

    datos_form = request.form.to_dict()
    # El correo del donante siempre sale de la sesión, no de un valor editable.
    datos_form["correo_donante"] = usuario.get("email", "")
    limpio, errores = validar_donacion(datos_form)

    if not errores:
        resultado = registrar_donacion(limpio)
        if resultado["exito"]:
            return _pagina(
                "donar",
                fundaciones=fundaciones,
                form=form_inicial,
                usuario_actual=usuario,
                mensaje="¡Donación registrada correctamente!",
            )
        errores.append(resultado["error"])

    return _pagina(
        "donar",
        fundaciones=fundaciones,
        errores=errores,
        form=datos_form,
        usuario_actual=usuario,
    )


@fundaciones_bp.route("/historial")
def historial():
    """Una fundación solo ve las donaciones recibidas por su propia cuenta."""
    if not session.get("user_id"):
        return redirect(url_for("login"))
    if _rol_actual() != "fundacion":
        return redirect(url_for("inicio"))

    fundacion_id = str(session.get("user_id"))
    resultado = obtener_historial(fundacion_id=fundacion_id)
    errores = [] if resultado["exito"] else [resultado["error"]]

    return _pagina(
        "historial",
        errores=errores,
        historial=resultado.get("datos", []),
    )


@fundaciones_bp.route("/pendientes")
def pendientes():
    """Solo el administrador puede revisar fundaciones pendientes."""
    if not session.get("user_id"):
        return redirect(url_for("login"))
    if _rol_actual() != "administrador":
        return redirect(url_for("inicio"))

    return _pagina("pendientes", pendientes=listar_fundaciones_pendientes())


@fundaciones_bp.route("/pendientes/<id_fundacion>/<accion>", methods=["POST"])
def resolver_pendiente(id_fundacion: str, accion: str):
    """Solo el administrador puede aprobar o rechazar una fundación."""
    if not session.get("user_id"):
        return redirect(url_for("login"))
    if _rol_actual() != "administrador":
        return redirect(url_for("inicio"))

    errores, mensaje = [], ""
    try:
        resultado = cambiar_estado_fundacion(id_fundacion, accion)
        if resultado["exito"]:
            mensaje = "La fundación fue actualizada correctamente."
        else:
            errores.append(resultado["error"])
    except ValueError as err:
        errores.append(str(err))

    return _pagina(
        "pendientes",
        errores=errores,
        mensaje=mensaje,
        pendientes=listar_fundaciones_pendientes(),
    )
