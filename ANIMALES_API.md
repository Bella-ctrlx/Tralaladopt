# Módulo Animales y Catálogo

Rutas disponibles:

- `GET /api/animales` — lista todos.
- `GET /api/animales?especie=Perro` — filtro por especie.
- `GET /api/animales?vulnerabilidad=alta` — filtro por vulnerabilidad.
- `GET /api/animales?especie=Gato&vulnerabilidad=media` — filtros combinados.
- `GET /api/animales/<id>` — ficha de un animal.
- `POST /api/animales` — crea un animal.
- `PUT/PATCH /api/animales/<id>` — actualiza un animal.
- `DELETE /api/animales/<id>` — elimina un animal.

Ejemplo mínimo para crear:

```json
{
  "nombre": "Luna",
  "especie": "Perro",
  "raza": "Mestiza",
  "edad": 3,
  "genero": "hembra",
  "vulnerabilidad": "media",
  "ubicacion": "Panamá",
  "fundacion_id": "UUID-DE-UNA-FUNDACION"
}
```

El `fundacion_id` debe existir en `public.users`, porque la base de datos tiene una llave foránea.

## Ejecutar

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Luego abre `http://127.0.0.1:5000/api/animales`.
