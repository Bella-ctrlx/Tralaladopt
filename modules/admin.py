"""Módulo de Administración e Integración para Tralaladopt.

Maneja el panel de control, aprobación de fundaciones y métricas del sistema.
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


def obtener_estadisticas_panel():
    """Obtiene métricas y conteos generales para el panel administrativo."""
    if not supabase:
        return {
            "total_usuarios": 0,
            "total_animales": 0,
            "solicitudes_pendientes": 0,
            "fundaciones_pendientes": 0,
        }

    try:
        total_usuarios = (
            supabase.table("users")
            .select("id", count="exact")
            .execute()
            .count
        )
        total_animales = (
            supabase.table("animals")
            .select("id", count="exact")
            .execute()
            .count
        )
        solicitudes_pendientes = (
            supabase.table("adoption_requests")
            .select("id", count="exact")
            .eq("status", "Pendiente")
            .execute()
            .count
        )
        fundaciones_pendientes = (
            supabase.table("users")
            .select("id", count="exact")
            .eq("role", "fundacion")
            .eq("status", "pendiente")
            .execute()
            .count
        )

        return {
            "total_usuarios": total_usuarios or 0,
            "total_animales": total_animales or 0,
            "solicitudes_pendientes": solicitudes_pendientes or 0,
            "fundaciones_pendientes": fundaciones_pendientes or 0,
        }
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
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
        response = (
            supabase.table("users")
            .select("*")
            .eq("role", "fundacion")
            .eq("status", "pendiente")
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error al obtener fundaciones pendientes: {e}")
        return []


def cambiar_estado_fundacion(fundacion_id: str, nuevo_estado: str):
    """Aprueba ('activo'), rechaza o suspende una cuenta de fundación."""
    if not supabase:
        return {"exito": False, "error": "Sin conexión a Supabase"}

    estados_validos = ["activo", "rechazado", "suspendido", "pendiente"]
    if nuevo_estado not in estados_validos:
        raise ValueError("Estado no válido para la fundación.")

    try:
        response = (
            supabase.table("users")
            .update({"status": nuevo_estado})
            .eq("id", fundacion_id)
            .execute()
        )

        supabase.table("notifications").insert(
            {
                "user_id": fundacion_id,
                "message": (
                    "El estado de tu cuenta de fundación ha sido"
                    f" actualizado a: {nuevo_estado}."
                ),
                "type": "admin",
            }
        ).execute()

        return {"exito": True, "data": response.data}
    except Exception as e:
        return {"exito": False, "error": str(e)}
    