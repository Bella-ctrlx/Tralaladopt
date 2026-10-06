"""Módulo de administración para Tralaladopt.

Maneja las métricas del panel y la aprobación de cuentas de fundación usando
el esquema actual de Supabase (users, animales y solicitudes_adopcion).
"""

import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client | None = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as err:
        print(f"Advertencia: No se pudo conectar a Supabase: {err}")


def _contar(tabla: str, filtros: list[tuple[str, str]] | None = None) -> int:
    """Cuenta filas de una tabla aplicando filtros de igualdad opcionales."""
    if not supabase:
        return 0

    consulta = supabase.table(tabla).select("id", count="exact")
    for campo, valor in filtros or []:
        consulta = consulta.eq(campo, valor)

    respuesta = consulta.execute()
    return respuesta.count or 0


def obtener_estadisticas_panel():
    """Obtiene métricas generales para el panel administrativo."""
    if not supabase:
        return {
            "total_usuarios": 0,
            "total_animales": 0,
            "solicitudes_pendientes": 0,
            "fundaciones_pendientes": 0,
        }

    try:
        return {
            "total_usuarios": _contar("users"),
            "total_animales": _contar("animales"),
            "solicitudes_pendientes": _contar(
                "solicitudes_adopcion",
                [("estado", "pendiente")],
            ),
            "fundaciones_pendientes": _contar(
                "users",
                [("rol", "fundacion"), ("estado", "pendiente")],
            ),
        }
    except Exception as err:
        print(f"Error al obtener estadísticas: {err}")
        return {
            "total_usuarios": 0,
            "total_animales": 0,
            "solicitudes_pendientes": 0,
            "fundaciones_pendientes": 0,
        }


def obtener_fundaciones_pendientes():
    """Lista las fundaciones que están esperando aprobación."""
    if not supabase:
        return []

    try:
        respuesta = (
            supabase.table("users")
            .select("id,nombre,email,ubicacion,estado")
            .eq("rol", "fundacion")
            .eq("estado", "pendiente")
            .order("nombre")
            .execute()
        )
        return respuesta.data or []
    except Exception as err:
        print(f"Error al obtener fundaciones pendientes: {err}")
        return []


def cambiar_estado_fundacion(fundacion_id: str, nuevo_estado: str):
    """Actualiza el estado de una fundación y registra una notificación."""
    if not supabase:
        return {"exito": False, "error": "Sin conexión a Supabase"}

    estados_validos = ["activo", "rechazado", "suspendido", "pendiente"]
    if nuevo_estado not in estados_validos:
        raise ValueError("Estado no válido para la fundación.")

    try:
        respuesta = (
            supabase.table("users")
            .update({"estado": nuevo_estado})
            .eq("id", fundacion_id)
            .eq("rol", "fundacion")
            .execute()
        )

        if not respuesta.data:
            return {"exito": False, "error": "No se encontró la fundación."}

        try:
            supabase.table("notificaciones").insert(
                {
                    "usuario_id": fundacion_id,
                    "mensaje": (
                        "El estado de tu cuenta de fundación cambió a: "
                        f"{nuevo_estado}."
                    ),
                    "tipo": "admin",
                }
            ).execute()
        except Exception as err:
            # La aprobación no debe fallar solo porque falle la notificación.
            print(f"No se pudo guardar la notificación: {err}")

        return {"exito": True, "data": respuesta.data}
    except Exception as err:
        return {"exito": False, "error": str(err)}
