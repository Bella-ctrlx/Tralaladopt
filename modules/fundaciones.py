"""Módulo de fundaciones y donaciones de Tralaladopt.

Incluye el registro de fundaciones (quedan pendientes de aprobación), la
aprobación o rechazo por parte del administrador, el registro de donaciones
y la consulta del historial. La conexión a Supabase se reutiliza de
``modules.admin``.
"""

import re
from decimal import Decimal, InvalidOperation
from uuid import UUID

from flask import Blueprint, render_template, request

from modules.admin import supabase

fundaciones_bp = Blueprint("fundaciones", __name__, url_prefix="/fundaciones")

TABLA_USUARIOS = "users"
TABLA_DONACIONES = "donaciones"
TABLA_NOTIFICACIONES = "notificaciones"

MONTO_MAXIMO = Decimal("99999999.99")  # límite de NUMERIC(10, 2)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MSG_SIN_BD = "El servicio de base de datos no está disponible."
MSG_ERROR_BD = "No se pudo completar la operación. Inténtalo más tarde."
ESTADOS_ACCION = {"aprobar": "activo", "rechazar": "rechazado"}


def _texto(datos, campo: str) -> str:
    """Devuelve el valor del campo sin espacios sobrantes (o cadena vacía)."""
    return str(datos.get(campo) or "").strip()


def _es_uuid(valor: str) -> bool:
    """Indica si el texto tiene formato UUID válido."""
    try:
        UUID(valor)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def validar_fundacion(datos) -> tuple[dict, list[str]]:
    """Valida y limpia los datos de registro de una fundación.

    Args:
        datos: Mapa con nombre, email, biografia, ubicacion, telefono
            y sitio_web.

    Returns:
        Tupla (datos_limpios, errores). Si ``errores`` está vacía los datos
        son válidos.
    """
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
    """Valida y limpia los datos de una donación.

    Args:
        datos: Mapa con fundacion_id, monto, mensaje y correo_donante.

    Returns:
        Tupla (datos_limpios, errores). ``monto`` se devuelve como Decimal.
    """
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
    """Registra una fundación con estado 'pendiente'.

    Args:
        datos: Datos ya validados con ``validar_fundacion``.

    Returns:
        Diccionario con ``exito`` y, si falla, ``error`` con un mensaje
        apto para mostrar a la persona usuaria.
    """
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
    except Exception as err:  # error de red, permisos o esquema
        print(f"Error al registrar fundación: {err}")
        return {"exito": False, "error": MSG_ERROR_BD}


def _listar_fundaciones(estado: str, columnas: str) -> list[dict]:
    """Devuelve las fundaciones en el estado indicado, ordenadas por nombre."""
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
    """Devuelve las fundaciones aprobadas."""
    return _listar_fundaciones(
        "activo", "id, nombre, ubicacion, biografia, sitio_web"
    )


def listar_fundaciones_pendientes() -> list[dict]:
    """Devuelve las fundaciones que esperan aprobación."""
    return _listar_fundaciones("pendiente", "id, nombre, email, ubicacion")


def cambiar_estado_fundacion(id_fundacion: str, accion: str) -> dict:
    """Aprueba o rechaza una fundación pendiente y le envía una notificación.

    Args:
        id_fundacion: UUID de la fundación.
        accion: ``"aprobar"`` o ``"rechazar"``.

    Returns:
        Diccionario con ``exito`` y, si falla, ``error``.

    Raises:
        ValueError: Si la acción no es válida o el id no es un UUID.
    """
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
    """Guarda una notificación; si falla solo se registra en consola."""
    try:
        supabase.table(TABLA_NOTIFICACIONES).insert(
            {"usuario_id": usuario_id, "mensaje": mensaje, "tipo": tipo}
        ).execute()
    except Exception as err:
        print(f"No se pudo guardar la notificación: {err}")


def registrar_donacion(datos: dict) -> dict:
    """Guarda una donación después de comprobar fundación y donante.

    Args:
        datos: Datos ya validados con ``validar_donacion``.

    Returns:
        Diccionario con ``exito`` y, si falla, ``error``.
    """
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
            .select("id")
            .eq("email", datos["correo_donante"])
            .execute()
        )
        if not donante.data:
            return {
                "exito": False,
                "error": "No hay una cuenta con el correo del donante.",
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
    """Devuelve un diccionario id -> nombre para los usuarios dados."""
    if not ids:
        return {}
    respuesta = (
        supabase.table(TABLA_USUARIOS)
        .select("id, nombre")
        .in_("id", list(set(ids)))
        .execute()
    )
    return {fila["id"]: fila["nombre"] for fila in respuesta.data or []}


def obtener_historial(email: str = "", fundacion_id: str = "") -> dict:
    """Consulta el historial de donaciones por donante o por fundación.

    Args:
        email: Correo del donante (opcional).
        fundacion_id: UUID de la fundación (opcional).

    Returns:
        Diccionario con ``exito`` y ``datos`` (lista) o ``error``.
    """
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
    """Renderiza la plantilla única con valores por defecto."""
    base = {
        "seccion": seccion,
        "errores": [],
        "mensaje": "",
        "form": {},
        "fundaciones": [],
        "pendientes": [],
        "historial": None,
    }
    base.update(contexto)
    return render_template("Fundations/fundaciones.html", **base)


@fundaciones_bp.route("/")
def listado():
    """Muestra las fundaciones activas."""
    return _pagina("listado", fundaciones=listar_fundaciones_activas())


@fundaciones_bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Formulario de registro de una fundación (queda pendiente)."""
    if request.method == "GET":
        return _pagina("registro")
    limpio, errores = validar_fundacion(request.form)
    if not errores:
        resultado = registrar_fundacion(limpio)
        if resultado["exito"]:
            return _pagina(
                "registro",
                mensaje="Registro recibido. Un administrador lo revisará.",
            )
        errores.append(resultado["error"])
    return _pagina("registro", errores=errores, form=limpio)


@fundaciones_bp.route("/donar", methods=["GET", "POST"])
def donar():
    """Formulario para donar a una fundación activa."""
    fundaciones = listar_fundaciones_activas()
    if request.method == "GET":
        return _pagina("donar", fundaciones=fundaciones)
    limpio, errores = validar_donacion(request.form)
    if not errores:
        resultado = registrar_donacion(limpio)
        if resultado["exito"]:
            return _pagina(
                "donar", fundaciones=fundaciones, mensaje="¡Donación registrada!"
            )
        errores.append(resultado["error"])
    return _pagina(
        "donar", fundaciones=fundaciones, errores=errores, form=request.form
    )


@fundaciones_bp.route("/historial")
def historial():
    """Historial de donaciones filtrado por donante o fundación."""
    fundaciones = listar_fundaciones_activas()
    email = _texto(request.args, "email")
    fundacion_id = _texto(request.args, "fundacion_id")
    if not email and not fundacion_id:
        return _pagina("historial", fundaciones=fundaciones)
    resultado = obtener_historial(email, fundacion_id)
    errores = [] if resultado["exito"] else [resultado["error"]]
    return _pagina(
        "historial",
        fundaciones=fundaciones,
        errores=errores,
        form=request.args,
        historial=resultado.get("datos"),
    )


@fundaciones_bp.route("/pendientes")
def pendientes():
    """Lista las fundaciones pendientes para aprobar o rechazar."""
    return _pagina("pendientes", pendientes=listar_fundaciones_pendientes())


@fundaciones_bp.route("/pendientes/<id_fundacion>/<accion>", methods=["POST"])
def resolver_pendiente(id_fundacion: str, accion: str):
    """Aprueba o rechaza una fundación pendiente."""
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