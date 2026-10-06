# TRALALADOPT 🐾

Plataforma web para facilitar la adopción responsable de animales, conectar adoptantes con fundaciones y centralizar la gestión de animales, solicitudes de adopción, favoritos, donaciones y administración del sistema.

---

## 1. Descripción del problema

La adopción de animales suele involucrar información dispersa entre redes sociales, refugios y diferentes medios de contacto. Esto dificulta que las personas encuentren animales disponibles, conozcan su información y puedan realizar un proceso de adopción organizado.

**TRALALADOPT** busca centralizar este proceso mediante una plataforma web donde los adoptantes pueden consultar animales disponibles, guardar favoritos y enviar solicitudes de adopción. Las fundaciones pueden gestionar los animales que tienen a su cargo y consultar la información relacionada con sus donaciones. Los administradores supervisan el funcionamiento general y la aprobación de fundaciones.

El sistema busca mejorar la organización y trazabilidad del proceso de adopción, manteniendo una separación de responsabilidades según el rol de cada usuario.

### Objetivos principales

- Centralizar el catálogo de animales disponibles para adopción.
- Facilitar la búsqueda y consulta de información de los animales.
- Permitir el envío y seguimiento de solicitudes de adopción.
- Permitir a los adoptantes gestionar favoritos.
- Permitir el registro y aprobación de fundaciones.
- Gestionar donaciones e historial de donaciones.
- Proporcionar un panel administrativo para supervisar el sistema.
- Mantener control de acceso según el rol del usuario.

---

## 2. Límites del proyecto

TRALALADOPT está orientado a la gestión de información y procesos relacionados con la adopción. El sistema no pretende sustituir la evaluación presencial de una adopción ni los procedimientos legales o veterinarios propios de cada fundación.

Entre sus límites se encuentran:

- No realiza diagnósticos veterinarios.
- No sustituye contratos o procesos legales de adopción.
- No garantiza por sí mismo que una persona sea apta para adoptar.
- La información de los animales depende de los datos registrados por las fundaciones.
- La aprobación de una fundación depende del administrador.
- El sistema gestiona el registro de donaciones, pero no constituye una pasarela bancaria completa de procesamiento de pagos.
- Los permisos y funcionalidades disponibles dependen del rol del usuario.

---

## 3. Roles del sistema

### Adoptante

Puede:

- Registrarse e iniciar sesión.
- Consultar el catálogo de animales.
- Ver el detalle de un animal.
- Agregar animales disponibles o en proceso a favoritos según las reglas del sistema.
- Enviar solicitudes de adopción.
- Consultar sus solicitudes.
- Consultar fundaciones registradas.
- Realizar donaciones a fundaciones activas.
- Consultar el historial correspondiente a sus donaciones.
- Gestionar su perfil.

No puede:

- Registrar animales.
- Eliminar animales.
- Aprobar o rechazar fundaciones.
- Registrar una fundación desde las funciones administrativas.

### Fundación

Puede:

- Iniciar sesión como fundación.
- Registrar y administrar los animales asociados a su fundación.
- Editar información de sus animales.
- Eliminar animales que pertenecen a su fundación.
- Consultar el historial de donaciones de su propia fundación.
- Gestionar información relacionada con sus animales.

No puede:

- Donar como fundación.
- Aprobar o rechazar fundaciones.
- Administrar otras fundaciones.
- Consultar el historial de donaciones de otras fundaciones.
- Registrar otra fundación como si fuera un administrador.

El registro de una fundación queda pendiente de aprobación por parte del administrador.

### Administrador

Puede:

- Acceder al panel administrativo.
- Consultar estadísticas del sistema.
- Consultar fundaciones pendientes de aprobación.
- Aprobar o rechazar fundaciones.
- Gestionar funciones administrativas del sistema.
- Supervisar información general relacionada con la plataforma.

El administrador no utiliza las funciones de donación destinadas a los adoptantes.

---

## 4. Requisitos funcionales

### RF01 - Registro de usuarios
El sistema debe permitir el registro de usuarios y almacenar la información correspondiente.

### RF02 - Inicio de sesión
El sistema debe permitir a los usuarios autenticarse y mantener una sesión activa.

### RF03 - Gestión de roles
El sistema debe diferenciar entre los roles:

- Adoptante
- Fundación
- Administrador

### RF04 - Catálogo de animales
El sistema debe permitir consultar los animales registrados y mostrar información relevante como:

- Nombre
- Especie
- Raza
- Edad
- Género
- Tamaño
- Color
- Ubicación
- Vulnerabilidad
- Estado
- Descripción
- Personalidad
- Estado de salud
- Necesidades especiales
- Fotografías

### RF05 - Detalle del animal
El sistema debe permitir consultar una ficha individual de cada animal.

### RF06 - Gestión de animales
Las fundaciones deben poder administrar los animales asociados a ellas.

### RF07 - Restricción por estado de adopción
Los animales adoptados no deben permitir nuevas solicitudes de adopción ni ser agregados a favoritos.

### RF08 - Favoritos
Los adoptantes deben poder administrar una lista de animales favoritos de acuerdo con las reglas del sistema.

### RF09 - Solicitudes de adopción
Los adoptantes deben poder enviar solicitudes de adopción y consultar su información.

### RF10 - Registro de fundaciones
Las fundaciones deben poder enviar su información para registro, quedando pendientes de aprobación.

### RF11 - Aprobación de fundaciones
El administrador debe poder aprobar o rechazar fundaciones pendientes.

### RF12 - Donaciones
Los adoptantes deben poder registrar donaciones destinadas a fundaciones activas.

### RF13 - Historial de donaciones
El sistema debe permitir consultar el historial de donaciones según los permisos del usuario.

### RF14 - Panel administrativo
El administrador debe disponer de un panel para consultar estadísticas y gestionar fundaciones pendientes.

### RF15 - Perfil
Los usuarios autenticados deben poder consultar su perfil.

### RF16 - Control de acceso
El sistema debe impedir que un usuario ejecute funciones que no correspondan a su rol.

---

## 5. Stack tecnológico

| Tecnología | Uso |
|---|---|
| **Python 3.10+** | Lenguaje principal del backend |
| **Flask** | Framework web |
| **Jinja2** | Renderizado de plantillas HTML |
| **Supabase** | Base de datos y servicios backend |
| **PostgreSQL** | Motor de base de datos utilizado por Supabase |
| **HTML5** | Estructura de las interfaces |
| **CSS3** | Diseño visual y responsive |
| **python-dotenv** | Gestión de variables de entorno |
| **Git** | Control de versiones |
| **GitHub** | Repositorio y colaboración |
| **GitHub Projects** | Gestión del tablero del proyecto |
| **GitHub Actions** | Automatización de tareas CI/CD |
| **Ruff** | Análisis y linting del código Python |
| **Snyk** | Análisis de seguridad y vulnerabilidades |

> **Versión de Python:** el proyecto requiere una versión compatible con las anotaciones modernas utilizadas por el código, como `Client | None`; se recomienda **Python 3.10 o superior**. Para el entorno definitivo del equipo, conviene fijar una única versión en la configuración del proyecto para evitar el clásico deporte universitario de "en mi PC sí funciona".

---

## 6. Estructura general del proyecto

Tralaladopt/
│
├── app.py
├── .env
├── .env.example
├── requirements.txt
│
├── modules/
│   ├── admin.py
│   ├── auth.py
│   ├── animals.py
│   ├── adoption_requests.py
│   ├── favorites.py
│   └── fundaciones.py
│
├── templates/
│   ├── Administrador/
│   ├── Animals/
│   ├── Adoptions/
│   ├── Favorites/
│   ├── Fundations/
│   └── Login/
│
├── static/
│   └── css/
│       └── styles.css
│
├── docs/
│   └── Flujo_trabajo.md
│   ├──README.md
│
└── .github/
│   └── workflows/
│   │      ├── security-snyk.yml
│   │      ├──python-lint.yml
│   │── ISSUE_TEMPLATE/
│                  ├── bug_report.md
│                  ├── feature_request.md


---

## 7. Instalación

### Requisitos previos

Se necesita tener instalado:

- Python 3.10 o superior.
- Git.
- Una cuenta/proyecto de Supabase.
- Acceso al repositorio de GitHub.

### 7.1 Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Tralaladopt
```

### 7.2 Crear un entorno virtual

En Windows:

```powershell
python -m venv .venv
```

Activarlo:

```powershell
.venv\Scripts\Activate.ps1
```

En Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 7.3 Instalar dependencias

`requirements.txt`:

```bash
pip install -r requirements.txt
```

```bash
pip install flask supabase python-dotenv
```

---

## 8. Configuración de variables de entorno

Crear un archivo `.env` en la raíz del proyecto.

Ejemplo:

```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase
FLASK_SECRET_KEY=tu_clave_secreta
```

No se debe subir el archivo `.env` al repositorio.

Para facilitar la configuración de otros integrantes, puede utilizarse `.env.example`:

```env
SUPABASE_URL=
SUPABASE_KEY=
FLASK_SECRET_KEY=
```
Cada uno debe crear su propio `.env` a partir de este archivo.

---

## 9. Ejecución del proyecto

Con el entorno virtual activo:

```bash
python app.py
```

También puede ejecutarse mediante Flask:

```powershell
$env:FLASK_APP="app.py"
flask run
```

El servidor mostrará la dirección local disponible, normalmente:

```text
http://127.0.0.1:5000
```

---

## 10. Base de datos

TRALALADOPT utiliza **Supabase** como servicio de backend y almacenamiento de datos.

Entre las entidades utilizadas por el sistema se encuentran datos relacionados con:

- Usuarios.
- Animales.
- Fundaciones.
- Solicitudes de adopción.
- Favoritos.
- Donaciones.
- Notificaciones.

Las credenciales no deben almacenarse directamente en el código fuente.

---

## 11. Integrantes y responsabilidades

La siguiente distribución corresponde a la organización mostrada en la planificación del proyecto:

| Integrante | Módulo / Funcionalidades | Responsabilidad técnica en GitHub |
|---|---|---|
| **Isabella Bernal** | **Autenticación y Usuarios:** Auth con Supabase, Login, Registro y Roles (adoptante, fundación, admin). | Configuración de Conventional Commits, Linters (Ruff) y archivo `.env.example`. |
| **Julian Castañeda** | **Animales y Catálogo:** CRUD de animales, filtros por animal/especie/vulnerabilidad, ficha y Supabase Storage. | Creación de plantillas de Issues (`.github/ISSUE_TEMPLATE/`) y etiquetas del proyecto. |
| **Missel Almanza** | **Adopciones y Favoritos:** sistema de favoritos (restricción única) y solicitudes de adopción (`adoption_requests`). | Documentación del flujo de trabajo en `docs/Flujo_trabajo.md` y reglas de Branch Protection. |
| **Kehysmer Hernández** | **Fundaciones y Donaciones:** registro/aprobación de fundaciones, donaciones (`donations`) e historial. | Configuración del tablero en GitHub Projects: pendientes, en proceso, revisión y finalizado. |
| **Noriel Ordoñez** | **Administración e Integración:** panel administrativo, estadísticas, notificaciones| Implementación de GitHub Actions (CI/CD) para Ruff, Snyk o pruebas. |

---

## 12. Flujo de trabajo del equipo

El proyecto utiliza Git y GitHub para controlar el desarrollo colaborativo.

El flujo contempla:

1. Crear o tomar una tarea del tablero.
2. Trabajar en una rama asociada a la funcionalidad.
3. Realizar commits siguiendo una convención.
4. Ejecutar las comprobaciones necesarias.
5. Crear un Pull Request.
6. Realizar revisión.
7. Integrar los cambios a la rama correspondiente.
8. Actualizar el estado de la tarea en GitHub Projects.

Ejemplo de commit:

```text
feat: agregar filtro de animales por especie
```
---

## 13. Tablero del proyecto

El tablero de trabajo se administra mediante **GitHub Projects**.

**Enlace al tablero:**

```text
https://github.com/users/Bella-ctrlx/projects/1
```

Estados utilizados:

- Pendiente
- En proceso
- Revisión
- Finalizado

---

## 14. Documentación del flujo de trabajo

La documentación del flujo se encuentra en:

```text
docs/Flujo_trabajo.md
```

**Enlace a la documentación:**

```text
https://github.com/Bella-ctrlx/Tralaladopt/blob/main/docs/flujo_trabajo.md
```

---

## 15. Análisis de calidad y seguridad

El proyecto contempla herramientas para mejorar la calidad del código y detectar problemas de seguridad.

### Ruff

**Ruff** se utiliza para analizar el código Python, detectar errores y mantener reglas de estilo consistentes.

Ejemplo:

```bash
ruff check .
```

También puede utilizarse para verificar formato:

```bash
ruff format --check .
```

### Snyk

**Snyk** se utiliza como herramienta de análisis de seguridad para detectar vulnerabilidades conocidas en dependencias y componentes del proyecto.

La integración puede ejecutarse desde GitHub Actions para automatizar las comprobaciones.

Objetivos:

- Detectar dependencias vulnerables.
- Identificar riesgos de seguridad.
- Evitar que problemas conocidos lleguen a la versión integrada.
- Complementar las revisiones manuales del equipo.

### GitHub Actions

GitHub Actions permite automatizar las verificaciones del proyecto, incluyendo herramientas como:

- Ruff.
- Snyk.
- Pruebas automatizadas, cuando estén disponibles.

---

## 16. Seguridad

Las credenciales sensibles deben mantenerse fuera del código fuente.

No se deben publicar:

```text
SUPABASE_KEY
FLASK_SECRET_KEY
```

El archivo `.env` debe permanecer fuera del repositorio mediante `.gitignore`.

Se recomienda mantener un archivo:

```text
.env.example
```

sin credenciales reales para documentar las variables necesarias.

---

## 17. Consideraciones de permisos

El sistema aplica reglas según el rol almacenado en la sesión.

### Adoptante

Tiene acceso a las funcionalidades destinadas al proceso de adopción y donación.

### Fundación

Tiene acceso a la administración de sus propios animales y a la información de donaciones correspondiente a su fundación.

### Administrador

Tiene acceso a las funcionalidades administrativas, incluyendo la aprobación o rechazo de fundaciones.

Las operaciones sensibles deben comprobar el rol del usuario en el backend y no depender únicamente de ocultar botones mediante HTML/CSS.

---

## 18. Diseño y experiencia de usuario

La interfaz de TRALALADOPT utiliza una identidad visual cálida y relacionada con la adopción de animales.

Paleta principal:

```css
--color-cream: #F6E2B3;
--color-gold: #E7A84E;
--color-orange: #D96C2C;
--color-teal: #3E8E7E;
--color-dark: #274C56;
```

El diseño contempla:

- Interfaz responsive.
- Tarjetas para animales.
- Estados y badges.
- Formularios accesibles.
- Navegación adaptable.
- Panel administrativo.
- Visualización de perfiles.
- Diseño consistente para fundaciones, adopciones y favoritos.