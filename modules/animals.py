import uuid

from flask import (
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

CAMPOS_PERMITIDOS = {
    "nombre",
    "especie",
    "raza",
    "edad",
    "genero",
    "tamano",
    "color",
    "descripcion",
    "personalidad",
    "estado_salud",
    "necesidades_especiales",
    "vulnerabilidad",
    "fotos",
    "ubicacion",
    "estado",
    "fundacion_id",
}

VULNERABILIDADES = {
    "baja",
    "media",
    "alta",
}

ESTADOS = {
    "disponible",
    "en_proceso",
    "adoptado",
}


# ============================================================
# SUBIR FOTO A SUPABASE STORAGE
# ============================================================

def subir_foto_animal(supabase, archivo):

    if not archivo or not archivo.filename:
        return None

    extensiones_permitidas = {
        "jpg",
        "jpeg",
        "png",
        "webp",
    }

    if "." not in archivo.filename:
        raise ValueError(
            "La imagen no tiene una extensión válida."
        )

    extension = (
        archivo.filename
        .rsplit(".", 1)[1]
        .lower()
    )

    if extension not in extensiones_permitidas:
        raise ValueError(
            "Formato no permitido. "
            "Usa JPG, JPEG, PNG o WEBP."
        )

    nombre_archivo = f"{uuid.uuid4()}.{extension}"

    contenido = archivo.read()

    content_type = (
        archivo.content_type
        or "application/octet-stream"
    )

    supabase.storage.from_("animales").upload(
        nombre_archivo,
        contenido,
        {
            "content-type": content_type
        }
    )

    url_foto = (
        supabase.storage
        .from_("animales")
        .get_public_url(nombre_archivo)
    )

    return url_foto


# ============================================================
# PREPARAR DATOS DEL ANIMAL
# ============================================================

def preparar_datos_animal(datos):

    edad = datos.get("edad")

    if edad in ("", None):
        edad = None
    else:
        try:
            edad = int(edad)

            if edad < 0:
                raise ValueError

        except (ValueError, TypeError):
            raise ValueError(
                "La edad debe ser un número entero "
                "mayor o igual a 0."
            )

    vulnerabilidad = (
        datos.get("vulnerabilidad")
        or "baja"
    ).lower()

    if vulnerabilidad not in VULNERABILIDADES:
        raise ValueError(
            "La vulnerabilidad debe ser "
            "baja, media o alta."
        )

    estado = (
        datos.get("estado")
        or "disponible"
    ).lower()

    if estado not in ESTADOS:
        raise ValueError(
            "El estado debe ser disponible, "
            "en_proceso o adoptado."
        )

    return {
        "nombre":
            datos.get("nombre"),

        "especie":
            datos.get("especie"),

        "raza":
            datos.get("raza") or None,

        "edad":
            edad,

        "genero":
            datos.get("genero") or None,

        "tamano":
            datos.get("tamano") or None,

        "color":
            datos.get("color") or None,

        "descripcion":
            datos.get("descripcion") or None,

        "personalidad":
            datos.get("personalidad") or None,

        "estado_salud":
            datos.get("estado_salud") or None,

        "necesidades_especiales":
            datos.get(
                "necesidades_especiales"
            ) or None,

        "vulnerabilidad":
            vulnerabilidad,

        "ubicacion":
            datos.get("ubicacion") or None,

        "estado":
            estado,

        "fundacion_id":
            datos.get("fundacion_id"),
    }


# ============================================================
# REGISTRAR RUTAS
# ============================================================

def registrar_rutas_animales(app, supabase):


    # ========================================================
    # API - LISTAR ANIMALES
    # ========================================================

    @app.route(
        "/api/animales",
        methods=["GET"]
    )
    def api_listar_animales():

        if not supabase:
            return jsonify({
                "error":
                    "Servicio de base de datos "
                    "no disponible"
            }), 500

        try:

            especie = request.args.get(
                "especie"
            )

            vulnerabilidad = request.args.get(
                "vulnerabilidad"
            )

            estado = request.args.get(
                "estado"
            )

            consulta = (
                supabase
                .table("animales")
                .select("*")
            )

            if especie:

                consulta = consulta.ilike(
                    "especie",
                    especie.strip()
                )

            if vulnerabilidad:

                vulnerabilidad = (
                    vulnerabilidad
                    .strip()
                    .lower()
                )

                if (
                    vulnerabilidad
                    not in VULNERABILIDADES
                ):
                    return jsonify({
                        "error":
                            "Vulnerabilidad inválida"
                    }), 400

                consulta = consulta.eq(
                    "vulnerabilidad",
                    vulnerabilidad
                )

            if estado:

                estado = (
                    estado
                    .strip()
                    .lower()
                )

                if estado not in ESTADOS:
                    return jsonify({
                        "error":
                            "Estado inválido"
                    }), 400

                consulta = consulta.eq(
                    "estado",
                    estado
                )

            respuesta = (
                consulta
                .order(
                    "fecha_creacion",
                    desc=True
                )
                .execute()
            )

            return jsonify({
                "animales":
                    respuesta.data,

                "total":
                    len(respuesta.data),
            }), 200

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # API - OBTENER ANIMAL
    # ========================================================

    @app.route(
        "/api/animales/<animal_id>",
        methods=["GET"]
    )
    def api_obtener_animal(animal_id):

        if not supabase:
            return jsonify({
                "error":
                    "Servicio de base de datos "
                    "no disponible"
            }), 500

        try:

            respuesta = (
                supabase
                .table("animales")
                .select("*")
                .eq("id", animal_id)
                .execute()
            )

            if not respuesta.data:
                return jsonify({
                    "error":
                        "Animal no encontrado"
                }), 404

            return jsonify(
                respuesta.data[0]
            ), 200

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # API - CREAR ANIMAL
    # ========================================================

    @app.route(
        "/api/animales",
        methods=["POST"]
    )
    def api_crear_animal():

        if not supabase:
            return jsonify({
                "error":
                    "Servicio de base de datos "
                    "no disponible"
            }), 500

        try:

            datos = (
                request.get_json(
                    silent=True
                )
                or {}
            )

            obligatorios = [
                "nombre",
                "especie",
                "fundacion_id",
            ]

            faltantes = [
                campo
                for campo in obligatorios
                if not datos.get(campo)
            ]

            if faltantes:

                return jsonify({
                    "error":
                        "Faltan campos obligatorios",

                    "campos":
                        faltantes,
                }), 400

            animal = preparar_datos_animal(
                datos
            )

            fotos = datos.get("fotos", [])

            if fotos is None:
                fotos = []

            if not isinstance(fotos, list):
                return jsonify({
                    "error":
                        "fotos debe ser "
                        "una lista de URLs"
                }), 400

            animal["fotos"] = fotos

            respuesta = (
                supabase
                .table("animales")
                .insert(animal)
                .execute()
            )

            return jsonify({
                "mensaje":
                    "Animal creado correctamente",

                "animal":
                    respuesta.data[0],
            }), 201

        except ValueError as e:

            return jsonify({
                "error": str(e)
            }), 400

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # API - ACTUALIZAR ANIMAL
    # ========================================================

    @app.route(
        "/api/animales/<animal_id>",
        methods=["PUT", "PATCH"]
    )
    def api_actualizar_animal(animal_id):

        if not supabase:
            return jsonify({
                "error":
                    "Servicio de base de datos "
                    "no disponible"
            }), 500

        try:

            datos = (
                request.get_json(
                    silent=True
                )
                or {}
            )

            cambios = {
                k: v
                for k, v in datos.items()
                if k in CAMPOS_PERMITIDOS
            }

            if not cambios:

                return jsonify({
                    "error":
                        "No hay campos válidos "
                        "para actualizar"
                }), 400

            if "edad" in cambios:

                edad = cambios["edad"]

                if edad in ("", None):
                    cambios["edad"] = None

                else:

                    try:
                        edad = int(edad)

                        if edad < 0:
                            raise ValueError

                    except (
                        ValueError,
                        TypeError
                    ):
                        return jsonify({
                            "error":
                                "Edad inválida"
                        }), 400

                    cambios["edad"] = edad

            if "vulnerabilidad" in cambios:

                vulnerabilidad = str(
                    cambios["vulnerabilidad"]
                ).lower()

                if (
                    vulnerabilidad
                    not in VULNERABILIDADES
                ):
                    return jsonify({
                        "error":
                            "Vulnerabilidad inválida"
                    }), 400

                cambios[
                    "vulnerabilidad"
                ] = vulnerabilidad

            if "estado" in cambios:

                estado = str(
                    cambios["estado"]
                ).lower()

                if estado not in ESTADOS:

                    return jsonify({
                        "error":
                            "Estado inválido"
                    }), 400

                cambios["estado"] = estado

            if "fotos" in cambios:

                if (
                    cambios["fotos"] is not None
                    and not isinstance(
                        cambios["fotos"],
                        list
                    )
                ):

                    return jsonify({
                        "error":
                            "fotos debe ser "
                            "una lista de URLs"
                    }), 400

            existe = (
                supabase
                .table("animales")
                .select("id")
                .eq("id", animal_id)
                .execute()
            )

            if not existe.data:

                return jsonify({
                    "error":
                        "Animal no encontrado"
                }), 404

            respuesta = (
                supabase
                .table("animales")
                .update(cambios)
                .eq("id", animal_id)
                .execute()
            )

            return jsonify({
                "mensaje":
                    "Animal actualizado correctamente",

                "animal":
                    respuesta.data[0],
            }), 200

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # API - ELIMINAR ANIMAL
    # ========================================================

    @app.route(
        "/api/animales/<animal_id>",
        methods=["DELETE"]
    )
    def api_eliminar_animal(animal_id):

        if not supabase:
            return jsonify({
                "error":
                    "Servicio de base de datos "
                    "no disponible"
            }), 500

        try:

            existe = (
                supabase
                .table("animales")
                .select("id")
                .eq("id", animal_id)
                .execute()
            )

            if not existe.data:

                return jsonify({
                    "error":
                        "Animal no encontrado"
                }), 404

            (
                supabase
                .table("animales")
                .delete()
                .eq("id", animal_id)
                .execute()
            )

            return jsonify({
                "mensaje":
                    "Animal eliminado correctamente"
            }), 200

        except Exception as e:

            return jsonify({
                "error": str(e)
            }), 500


    # ========================================================
    # WEB - CATÁLOGO
    # ========================================================

    @app.route("/animales")
    def catalogo_animales():

        if not supabase:
            return (
                "Servicio de base de datos "
                "no disponible",
                500
            )

        try:

            especie = request.args.get(
                "especie",
                ""
            )

            vulnerabilidad = request.args.get(
                "vulnerabilidad",
                ""
            )

            consulta = (
                supabase
                .table("animales")
                .select("*")
            )

            if especie:

                consulta = consulta.ilike(
                    "especie",
                    especie
                )

            if vulnerabilidad:

                consulta = consulta.eq(
                    "vulnerabilidad",
                    vulnerabilidad
                )

            respuesta = consulta.execute()

            return render_template(
                "Animals/catalogo.html",
                animales=respuesta.data,
                especie=especie,
                vulnerabilidad=vulnerabilidad,
            )

        except Exception as e:

            return (
                f"Error cargando catálogo: {e}",
                500
            )


    # ========================================================
    # WEB - NUEVO ANIMAL
    # ========================================================

    @app.route(
        "/animales/nuevo",
        methods=["GET", "POST"]
    )
    def nuevo_animal():

        if not supabase:
            return (
                "Servicio de base de datos "
                "no disponible",
                500
            )

        try:

            fundaciones = (
                supabase
                .table("users")
                .select("id,nombre")
                .eq("rol", "fundacion")
                .eq("estado", "activo")
                .execute()
                .data
            )

            if request.method == "POST":

                datos = {
                    "nombre":
                        request.form.get(
                            "nombre"
                        ),

                    "especie":
                        request.form.get(
                            "especie"
                        ),

                    "raza":
                        request.form.get(
                            "raza"
                        ),

                    "edad":
                        request.form.get(
                            "edad"
                        ),

                    "genero":
                        request.form.get(
                            "genero"
                        ),

                    "tamano":
                        request.form.get(
                            "tamano"
                        ),

                    "color":
                        request.form.get(
                            "color"
                        ),

                    "descripcion":
                        request.form.get(
                            "descripcion"
                        ),

                    "personalidad":
                        request.form.get(
                            "personalidad"
                        ),

                    "estado_salud":
                        request.form.get(
                            "estado_salud"
                        ),

                    "necesidades_especiales":
                        request.form.get(
                            "necesidades_especiales"
                        ),

                    "vulnerabilidad":
                        request.form.get(
                            "vulnerabilidad"
                        ),

                    "ubicacion":
                        request.form.get(
                            "ubicacion"
                        ),

                    "estado":
                        request.form.get(
                            "estado"
                        ),

                    "fundacion_id":
                        request.form.get(
                            "fundacion_id"
                        ),
                }

                if (
                    not datos["nombre"]
                    or not datos["especie"]
                    or not datos["fundacion_id"]
                ):
                    return (
                        "Nombre, especie y fundación "
                        "son obligatorios.",
                        400
                    )

                foto = request.files.get(
                    "foto"
                )

                url_foto = None

                if foto and foto.filename:

                    url_foto = subir_foto_animal(
                        supabase,
                        foto
                    )

                datos = preparar_datos_animal(
                    datos
                )

                if url_foto:

                    datos["fotos"] = [
                        url_foto
                    ]

                else:

                    datos["fotos"] = []

                (
                    supabase
                    .table("animales")
                    .insert(datos)
                    .execute()
                )

                return redirect(
                    url_for(
                        "catalogo_animales"
                    )
                )

            return render_template(
                "Animals/formulario.html",
                animal=None,
                fundaciones=fundaciones,
                modo="crear",
            )

        except ValueError as e:

            return str(e), 400

        except Exception as e:

            return (
                f"Error registrando animal: {e}",
                500
            )


    # ========================================================
    # WEB - DETALLE
    # ========================================================

    @app.route(
        "/animales/<animal_id>"
    )
    def detalle_animal(animal_id):

        if not supabase:
            return (
                "Servicio de base de datos "
                "no disponible",
                500
            )

        try:

            respuesta = (
                supabase
                .table("animales")
                .select("*")
                .eq("id", animal_id)
                .execute()
            )

            if not respuesta.data:

                return (
                    "Animal no encontrado",
                    404
                )

            return render_template(
                "Animals/detalle.html",
                animal=respuesta.data[0],
            )

        except Exception as e:

            return (
                f"Error cargando animal: {e}",
                500
            )


    # ========================================================
    # WEB - EDITAR
    # ========================================================

    @app.route(
        "/animales/<animal_id>/editar",
        methods=["GET", "POST"]
    )
    def editar_animal(animal_id):

        if not supabase:
            return (
                "Servicio de base de datos "
                "no disponible",
                500
            )

        try:

            animal_respuesta = (
                supabase
                .table("animales")
                .select("*")
                .eq("id", animal_id)
                .execute()
            )

            if not animal_respuesta.data:

                return (
                    "Animal no encontrado",
                    404
                )

            animal = (
                animal_respuesta.data[0]
            )

            fundaciones = (
                supabase
                .table("users")
                .select("id,nombre")
                .eq("rol", "fundacion")
                .eq("estado", "activo")
                .execute()
                .data
            )

            if request.method == "POST":

                datos = {
                    "nombre":
                        request.form.get(
                            "nombre"
                        ),

                    "especie":
                        request.form.get(
                            "especie"
                        ),

                    "raza":
                        request.form.get(
                            "raza"
                        ),

                    "edad":
                        request.form.get(
                            "edad"
                        ),

                    "genero":
                        request.form.get(
                            "genero"
                        ),

                    "tamano":
                        request.form.get(
                            "tamano"
                        ),

                    "color":
                        request.form.get(
                            "color"
                        ),

                    "descripcion":
                        request.form.get(
                            "descripcion"
                        ),

                    "personalidad":
                        request.form.get(
                            "personalidad"
                        ),

                    "estado_salud":
                        request.form.get(
                            "estado_salud"
                        ),

                    "necesidades_especiales":
                        request.form.get(
                            "necesidades_especiales"
                        ),

                    "vulnerabilidad":
                        request.form.get(
                            "vulnerabilidad"
                        ),

                    "ubicacion":
                        request.form.get(
                            "ubicacion"
                        ),

                    "estado":
                        request.form.get(
                            "estado"
                        ),

                    "fundacion_id":
                        request.form.get(
                            "fundacion_id"
                        ),
                }

                if (
                    not datos["nombre"]
                    or not datos["especie"]
                    or not datos["fundacion_id"]
                ):
                    return (
                        "Nombre, especie y fundación "
                        "son obligatorios.",
                        400
                    )

                datos = preparar_datos_animal(
                    datos
                )

                foto = request.files.get(
                    "foto"
                )

                if foto and foto.filename:

                    url_foto = subir_foto_animal(
                        supabase,
                        foto
                    )

                    fotos_actuales = (
                        animal.get("fotos")
                        or []
                    )

                    fotos_actuales.append(
                        url_foto
                    )

                    datos["fotos"] = (
                        fotos_actuales
                    )

                (
                    supabase
                    .table("animales")
                    .update(datos)
                    .eq("id", animal_id)
                    .execute()
                )

                return redirect(
                    url_for(
                        "detalle_animal",
                        animal_id=animal_id,
                    )
                )

            return render_template(
                "Animals/formulario.html",
                animal=animal,
                fundaciones=fundaciones,
                modo="editar",
            )

        except ValueError as e:

            return str(e), 400

        except Exception as e:

            return (
                f"Error editando animal: {e}",
                500
            )


    # ========================================================
    # WEB - ELIMINAR
    # ========================================================

    @app.route(
        "/animales/<animal_id>/eliminar",
        methods=["POST"]
    )
    def eliminar_animal_web(animal_id):

        if not supabase:
            return (
                "Servicio de base de datos "
                "no disponible",
                500
            )

        try:

            (
                supabase
                .table("animales")
                .delete()
                .eq("id", animal_id)
                .execute()
            )

            return redirect(
                url_for(
                    "catalogo_animales"
                )
            )

        except Exception as e:

            return (
                f"Error eliminando animal: {e}",
                500
            )