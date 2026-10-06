from flask import (
    redirect,
    render_template,
    session,
    url_for,
)


def registrar_rutas_favoritos(app, supabase):

    # MIS FAVORITOS
    @app.route("/favoritos")
    def mis_favoritos():

        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("login"))

        if not supabase:
            return "Base de datos no disponible", 500

        try:

            respuesta = (
                supabase
                .table("favoritos")
                .select(
                    """
                    usuario_id,
                    animal_id,
                    animales (
                        id,
                        nombre,
                        especie,
                        raza,
                        edad,
                        genero,
                        tamano,
                        fotos,
                        ubicacion,
                        estado,
                        vulnerabilidad
                    )
                    """
                )
                .eq("usuario_id", user_id)
                .execute()
            )

            return render_template(
                "favorites/favoritos.html",
                favoritos=respuesta.data,
            )

        except Exception as e:

            return (
                f"Error cargando favoritos: {e}",
                500
            )

    # AGREGAR A FAVORITOS
    @app.route(
        "/favoritos/<animal_id>",
        methods=["POST"]
    )
    def agregar_favorito(animal_id):

        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("login"))

        if not supabase:
            return "Base de datos no disponible", 500

        try:

            # Verificar que el animal existe
            animal = (
                supabase
                .table("animales")
                .select("id")
                .eq("id", animal_id)
                .execute()
            )

            if not animal.data:
                return "Animal no encontrado", 404

            # Verificar si ya está guardado
            favorito_existente = (
                supabase
                .table("favoritos")
                .select("usuario_id, animal_id")
                .eq("usuario_id", user_id)
                .eq("animal_id", animal_id)
                .execute()
            )

            if favorito_existente.data:

                # Ya existe, simplemente volvemos
                # a la ficha del animal.

                return redirect(
                    url_for(
                        "detalle_animal",
                        animal_id=animal_id
                    )
                )


            # Guardar favorito
            (
                supabase
                .table("favoritos")
                .insert({
                    "usuario_id": user_id,
                    "animal_id": animal_id,
                })
                .execute()
            )

            return redirect(
                url_for(
                    "detalle_animal",
                    animal_id=animal_id
                )
            )

        except Exception as e:

            return (
                f"Error agregando favorito: {e}",
                500
            )

    # ELIMINAR DE FAVORITOS
    @app.route(
        "/favoritos/<animal_id>/eliminar",
        methods=["POST"]
    )
    def eliminar_favorito(animal_id):

        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("login"))

        if not supabase:
            return "Base de datos no disponible", 500

        try:

            (
                supabase
                .table("favoritos")
                .delete()
                .eq("usuario_id", user_id)
                .eq("animal_id", animal_id)
                .execute()
            )

            return redirect(
                url_for("mis_favoritos")
            )

        except Exception as e:

            return (
                f"Error eliminando favorito: {e}",
                500
            )