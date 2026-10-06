from flask import (
    redirect,
    render_template,
    request,
    session,
    url_for,
)


def registrar_rutas_adopciones(app, supabase):

    # =========================================================
    # CREAR SOLICITUD DE ADOPCIÓN
    # =========================================================

    @app.route(
        "/adopciones/solicitar/<animal_id>",
        methods=["GET", "POST"]
    )
    def solicitar_adopcion(animal_id):

        # -----------------------------------------
        # Comprobar login
        # -----------------------------------------

        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("login"))

        if session.get("user_role") != "adoptante":
            return redirect(url_for("inicio"))

        if not supabase:
            return "Base de datos no disponible", 500

        try:

            # -----------------------------------------
            # Obtener animal
            # -----------------------------------------

            respuesta_animal = (
                supabase
                .table("animales")
                .select("*")
                .eq("id", animal_id)
                .execute()
            )

            if not respuesta_animal.data:
                return "Animal no encontrado", 404

            animal = respuesta_animal.data[0]

            # -----------------------------------------
            # Solo animales disponibles
            # -----------------------------------------

            if animal["estado"] not in ("disponible", "en_proceso"):
                return (
                    "Este animal actualmente "
                    "no está disponible para adopción.",
                    400
                )

            # -----------------------------------------
            # Comprobar solicitud existente
            # -----------------------------------------

            solicitud_existente = (
                supabase
                .table("solicitudes_adopcion")
                .select("id,estado")
                .eq("solicitante_id", user_id)
                .eq("animal_id", animal_id)
                .in_(
                    "estado",
                    [
                        "pendiente",
                        "en_revision",
                        "aprobada",
                    ]
                )
                .execute()
            )

            if solicitud_existente.data:

                return render_template(
                    "Adoptions/solicitud_existente.html",
                    animal=animal,
                    solicitud=solicitud_existente.data[0],
                )

            # -----------------------------------------
            # Procesar formulario
            # -----------------------------------------

            if request.method == "POST":

                datos = {
                    "solicitante_id": user_id,

                    "animal_id": animal_id,

                    "fundacion_id":
                        animal["fundacion_id"],

                    "estado": "pendiente",

                    "motivacion":
                        request.form.get(
                            "motivacion"
                        ),

                    "tipo_vivienda":
                        request.form.get(
                            "tipo_vivienda"
                        ),

                    "otras_mascotas":
                        request.form.get(
                            "otras_mascotas"
                        ) == "si",

                    "experiencia":
                        request.form.get(
                            "experiencia"
                        ),

                    "tiempo_disponible":
                        request.form.get(
                            "tiempo_disponible"
                        ),

                    "informacion_adicional":
                        request.form.get(
                            "informacion_adicional"
                        ),
                }

                (
                    supabase
                    .table("solicitudes_adopcion")
                    .insert(datos)
                    .execute()
                )

                return redirect(
                    url_for("mis_solicitudes")
                )

            # -----------------------------------------
            # Mostrar formulario
            # -----------------------------------------

            return render_template(
                "Adoptions/solicitar.html",
                animal=animal,
            )

        except Exception as e:

            return (
                f"Error procesando solicitud: {e}",
                500
            )

    # =========================================================
    # MIS SOLICITUDES
    # =========================================================

    @app.route("/mis-solicitudes")
    def mis_solicitudes():

        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("login"))

        if session.get("user_role") != "adoptante":
            return redirect(url_for("inicio"))

        if not supabase:
            return "Base de datos no disponible", 500

        try:

            respuesta = (
                supabase
                .table("solicitudes_adopcion")
                .select(
                    """
                    *,
                    animales (
                        id,
                        nombre,
                        especie,
                        raza,
                        fotos,
                        estado
                    )
                    """
                )
                .eq(
                    "solicitante_id",
                    user_id
                )
                .order(
                    "fecha_creacion",
                    desc=True
                )
                .execute()
            )

            return render_template(
                "Adoptions/solicitudes.html",
                solicitudes=respuesta.data,
            )

        except Exception as e:

            return (
                f"Error cargando solicitudes: {e}",
                500
            )

    # =========================================================
    # CANCELAR SOLICITUD
    # =========================================================

    @app.route(
        "/adopciones/<solicitud_id>/cancelar",
        methods=["POST"]
    )
    def cancelar_solicitud(solicitud_id):

        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("login"))

        if session.get("user_role") != "adoptante":
            return redirect(url_for("inicio"))

        try:

            # Solo puede cancelar solicitudes
            # que pertenecen al usuario actual.

            respuesta = (
                supabase
                .table("solicitudes_adopcion")
                .select("*")
                .eq("id", solicitud_id)
                .eq("solicitante_id", user_id)
                .execute()
            )

            if not respuesta.data:
                return "Solicitud no encontrada", 404

            solicitud = respuesta.data[0]

            if solicitud["estado"] not in [
                "pendiente",
                "en_revision",
            ]:
                return (
                    "Esta solicitud ya no "
                    "puede cancelarse.",
                    400
                )

            (
                supabase
                .table("solicitudes_adopcion")
                .update({
                    "estado": "cancelada"
                })
                .eq("id", solicitud_id)
                .eq("solicitante_id", user_id)
                .execute()
            )

            return redirect(
                url_for("mis_solicitudes")
            )

        except Exception as e:

            return (
                f"Error cancelando solicitud: {e}",
                500
            )