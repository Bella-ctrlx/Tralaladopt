"""CRUD y catálogo de animales para Tralaladopt."""

from flask import Blueprint, jsonify, request

animals_bp = Blueprint("animals", __name__)

CAMPOS_PERMITIDOS = {
    "nombre", "especie", "raza", "edad", "genero", "tamano", "color",
    "descripcion", "personalidad", "estado_salud", "necesidades_especiales",
    "vulnerabilidad", "fotos", "ubicacion", "estado", "fundacion_id",
}
VULNERABILIDADES = {"baja", "media", "alta"}
ESTADOS = {"disponible", "en_proceso", "adoptado"}


def registrar_rutas_animales(app, supabase):
    """Registra las rutas del módulo de animales usando el cliente Supabase de app.py."""

    def db_disponible():
        if supabase is None:
            return jsonify({"error": "Servicio de base de datos no disponible"}), 500
        return None

    @animals_bp.get("/api/animales")
    def listar_animales():
        error = db_disponible()
        if error:
            return error
        try:
            query = supabase.table("animales").select("*")

            especie = request.args.get("especie", type=str)
            vulnerabilidad = request.args.get("vulnerabilidad", type=str)
            estado = request.args.get("estado", type=str)

            if especie:
                query = query.ilike("especie", especie.strip())
            if vulnerabilidad:
                vulnerabilidad = vulnerabilidad.strip().lower()
                if vulnerabilidad not in VULNERABILIDADES:
                    return jsonify({"error": "vulnerabilidad debe ser baja, media o alta"}), 400
                query = query.eq("vulnerabilidad", vulnerabilidad)
            if estado:
                estado = estado.strip().lower()
                if estado not in ESTADOS:
                    return jsonify({"error": "estado no válido"}), 400
                query = query.eq("estado", estado)

            respuesta = query.order("fecha_creacion", desc=True).execute()
            return jsonify({"total": len(respuesta.data), "animales": respuesta.data}), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @animals_bp.get("/api/animales/<animal_id>")
    def obtener_animal(animal_id):
        error = db_disponible()
        if error:
            return error
        try:
            respuesta = (
                supabase.table("animales").select("*").eq("id", animal_id).execute()
            )
            if not respuesta.data:
                return jsonify({"error": "Animal no encontrado"}), 404
            return jsonify(respuesta.data[0]), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @animals_bp.post("/api/animales")
    def crear_animal():
        error = db_disponible()
        if error:
            return error
        datos = request.get_json(silent=True) or {}

        faltantes = [c for c in ("nombre", "especie", "fundacion_id") if not datos.get(c)]
        if faltantes:
            return jsonify({"error": "Faltan campos obligatorios", "campos": faltantes}), 400

        vulnerabilidad = str(datos.get("vulnerabilidad", "baja")).lower()
        estado = str(datos.get("estado", "disponible")).lower()
        if vulnerabilidad not in VULNERABILIDADES:
            return jsonify({"error": "vulnerabilidad debe ser baja, media o alta"}), 400
        if estado not in ESTADOS:
            return jsonify({"error": "estado debe ser disponible, en_proceso o adoptado"}), 400
        if "edad" in datos and datos["edad"] is not None:
            if not isinstance(datos["edad"], int) or datos["edad"] < 0:
                return jsonify({"error": "edad debe ser un entero mayor o igual a 0"}), 400
        if "fotos" in datos and datos["fotos"] is not None and not isinstance(datos["fotos"], list):
            return jsonify({"error": "fotos debe ser una lista de URLs"}), 400

        animal = {k: v for k, v in datos.items() if k in CAMPOS_PERMITIDOS}
        animal["vulnerabilidad"] = vulnerabilidad
        animal["estado"] = estado
        animal.setdefault("fotos", [])

        try:
            respuesta = supabase.table("animales").insert(animal).execute()
            return jsonify({"mensaje": "Animal creado correctamente", "animal": respuesta.data[0]}), 201
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @animals_bp.put("/api/animales/<animal_id>")
    @animals_bp.patch("/api/animales/<animal_id>")
    def actualizar_animal(animal_id):
        error = db_disponible()
        if error:
            return error
        datos = request.get_json(silent=True) or {}
        cambios = {k: v for k, v in datos.items() if k in CAMPOS_PERMITIDOS}

        if not cambios:
            return jsonify({"error": "No hay campos válidos para actualizar"}), 400
        if "vulnerabilidad" in cambios:
            cambios["vulnerabilidad"] = str(cambios["vulnerabilidad"]).lower()
            if cambios["vulnerabilidad"] not in VULNERABILIDADES:
                return jsonify({"error": "vulnerabilidad debe ser baja, media o alta"}), 400
        if "estado" in cambios:
            cambios["estado"] = str(cambios["estado"]).lower()
            if cambios["estado"] not in ESTADOS:
                return jsonify({"error": "estado no válido"}), 400
        if "edad" in cambios and cambios["edad"] is not None:
            if not isinstance(cambios["edad"], int) or cambios["edad"] < 0:
                return jsonify({"error": "edad debe ser un entero mayor o igual a 0"}), 400
        if "fotos" in cambios and cambios["fotos"] is not None and not isinstance(cambios["fotos"], list):
            return jsonify({"error": "fotos debe ser una lista de URLs"}), 400

        try:
            existe = supabase.table("animales").select("id").eq("id", animal_id).execute()
            if not existe.data:
                return jsonify({"error": "Animal no encontrado"}), 404
            respuesta = supabase.table("animales").update(cambios).eq("id", animal_id).execute()
            return jsonify({"mensaje": "Animal actualizado correctamente", "animal": respuesta.data[0]}), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @animals_bp.delete("/api/animales/<animal_id>")
    def eliminar_animal(animal_id):
        error = db_disponible()
        if error:
            return error
        try:
            existe = supabase.table("animales").select("id").eq("id", animal_id).execute()
            if not existe.data:
                return jsonify({"error": "Animal no encontrado"}), 404
            supabase.table("animales").delete().eq("id", animal_id).execute()
            return jsonify({"mensaje": "Animal eliminado correctamente"}), 200
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    app.register_blueprint(animals_bp)
