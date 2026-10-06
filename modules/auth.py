"""
Módulo de Autenticación para Tralaladopt
Alineado con la tabla public.users de Supabase
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
    except Exception as e:
        print(f"Error al conectar Supabase en auth.py: {e}")


def registrar_usuario(datos_usuario):
    try:
        email = datos_usuario.get("email", "").strip()
        nombre = datos_usuario.get("name", "").strip()
        rol = datos_usuario.get("role", "adoptante")

        if not email or not nombre:
            return {
                "exito": False,
                "error": "El nombre y el correo son obligatorios.",
            }

        estado_inicial = "activo" if rol == "adoptante" else "pendiente"

    
        payload = {
            "nombre": nombre,
            "email": email,
            "rol": rol,
            "estado": estado_inicial,
        }

        response = supabase.table("users").insert(payload).execute()
        return {"exito": True, "data": response.data}
    except Exception as e:
        return {"exito": False, "error": str(e)}


def iniciar_sesion(email):
    try:
        response = (
            supabase.table("users").select("*").eq("email", email).execute()
        )
        if response.data:
            usuario = response.data[0]
            if usuario.get("estado") == "suspendido":
                return {
                    "exito": False,
                    "error": "Tu cuenta se encuentra suspendida.",
                }
            if usuario.get("estado") == "pendiente":
                return {
                    "exito": False,
                    "error": "Tu cuenta de fundación está pendiente de aprobación.",
                }
            if usuario.get("estado") == "rechazado":
                return {
                    "exito": False,
                    "error": "La solicitud de esta fundación fue rechazada.",
                }
            return {"exito": True, "usuario": usuario}
        return {
            "exito": False,
            "error": "El correo no se encuentra registrado.",
        }
    except Exception as e:
        return {"exito": False, "error": str(e)}


def obtener_perfil(usuario_id):
    try:
        response = (
            supabase.table("users")
            .select("*")
            .eq("id", usuario_id)
            .single()
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error al obtener perfil: {e}")
        return None