## TRALALADOPT
## Flujo de desarrollo basado en Issues, ramas por funcionalidad y Pull Requests.

Este flujo se utiliza para organizar el desarrollo de Tralaladopt, permitiendo que cada integrante trabaje en funcionalidades específicas sin modificar directamente la rama principal.

El objetivo es mantener un desarrollo ordenado, facilitar la revisión del código y reducir conflictos antes de integrar los cambios al proyecto.

---

## 2. Justificación del flujo

El proyecto Tralaladopt es desarrollado por varios integrantes que trabajan en diferentes módulos, entre ellos:

- Autenticación y usuarios.
- Animales y catálogo.
- Solicitudes de adopción.
- Favoritos.
- Fundaciones y donaciones.
- Administración e integración.

Debido a que varias personas trabajan simultáneamente sobre el mismo proyecto, se utiliza un flujo basado en ramas para separar los cambios de cada funcionalidad.

Este flujo permite:

- Evitar trabajar directamente sobre la rama principal.
- Asociar cada cambio con un Issue.
- Separar las funcionalidades desarrolladas por cada integrante.
- Facilitar la revisión del código.
- Detectar errores antes de integrar los cambios.
- Reducir conflictos entre integrantes.
- Mantener un historial organizado de los cambios.
- Aplicar reglas de revisión antes del merge.


# 3. Ramas del proyecto

El proyecto utiliza diferentes tipos de ramas según el propósito del cambio.

## 3.1 Rama principal

### Rama `main`

Es la rama principal del proyecto.

Contiene las versiones que han sido integradas y consideradas estables.

No se debe trabajar directamente sobre esta rama para desarrollar nuevas funcionalidades.

Los cambios deben llegar a `main` mediante un Pull Request después de completar el proceso de revisión.

---

## Ramas de funcionalidades

### Rama `feature/*`

Se utilizan para desarrollar nuevas funcionalidades.

La estructura utilizada es:

```text
feature/nombre-de-la-funcionalidad
````

Ejemplos:

```
feature/animales-catalogo
feature/favoritos
feature/solicitudes-adopcion
feature/fundaciones-donaciones
feature/panel-administrativo
```

Cada rama debe estar relacionada con una funcionalidad o Issue específico.

Por ejemplo:

```
Issue #15 - Implementar catálogo de animales
```

puede desarrollarse mediante:

```
feature/animales-catalogo
```

##Ramas de documentación

### `docs/*`

Se utilizan para cambios relacionados exclusivamente con documentación.

Ejemplos:

```
docs/readme
docs/flujo-trabajo
```

# 4. Recorrido desde un Issue hasta su integración

El flujo completo de trabajo es el siguiente:

```
Issue
  │
  ▼
Asignación
  │
  ▼
Creación de rama
  │
  ▼
Desarrollo
  │
  ▼
Commit
  │
  ▼
Push
  │
  ▼
Pull Request
  │
  ▼
Revisión
  │
  ├── Cambios solicitados
  │       │
  │       ▼
  │   Correcciones
  │       │
  │       └──────────────► Revisión
  │
  ▼
Aprobación
  │
  ▼
Merge
  │
  ▼
main
```

# 5. Creación del Issue

Antes de comenzar una funcionalidad, se debe crear un Issue en GitHub.

El Issue debe describir claramente:

* Qué problema se quiere resolver.

* Qué funcionalidad se necesita.

* Qué resultado se espera.

* Criterios básicos para considerar terminado el trabajo.

Creamos un template para poder organizar el reporte de issues.

Ejemplo:

```
---
name: Reporte de Defecto
about: Reportar un error usando historias de usuario.
title: '[DEFECTO] '
labels: 'defecto'
assignees: ''
---

Como usuario / desarrollador
Quiero [indicar qué funcionalidad o pantalla falló]

Para que
El sistema de Tralaladopt no presente errores inesperados.

Descripción del problema
Explícanos brevemente qué está pasando.

Pasos para reproducir
1. Ir a...
2. Hacer clic en...
3. Ver el fallo.
```

# 6. Asignación del Issue

El Issue debe asignarse al integrante responsable de implementar la funcionalidad.

Cada integrante trabaja principalmente en los módulos que le fueron asignados.

La distribución del proyecto incluye:

| Integrante        | Área principal               |
| ------------      | ---------------------------- |
| Isabella Bernal   | Autenticación y usuarios     |
| Julian Castañeda  | Animales y catálogo          |
| Missel Almanza    | Adopciones y favoritos       |
| Kehysmer Hernandez| Fundaciones y donaciones     |
| Noriel Ordoñez    | Administración e integración |

La asignación permite identificar quién es responsable de cada cambio.

# 7. Creación de la rama

Una vez asignado el Issue, se crea una rama específica para trabajar en él.

Ejemplo:

Bash

```
git checkout main
git pull origin main
git checkout -b feature/animales-catalogo
```

La rama debe tener un nombre descriptivo y relacionado con la funcionalidad.

# 8. Desarrollo

El integrante realiza los cambios necesarios dentro de su rama.

Durante esta etapa se deben respetar las siguientes reglas:

* No modificar funcionalidades ajenas sin justificación.

* Mantener la estructura existente del proyecto.

* Evitar código duplicado.

* Mantener nombres claros para funciones y variables.

* No subir credenciales ni información sensible.

* Probar los cambios antes de crear el Pull Request.

# 9. Commits

Los cambios deben registrarse mediante commits claros y descriptivos.

Ejemplos:

Bash

```
git add -A

git commit -m "feat: agregar catálogo de animales"
```

Para correcciones:

Bash

```
git commit -m "fix: corregir eliminación de animales"
```

Para documentación:

Bash

```
git commit -m "docs: agregar flujo de trabajo"
```

Se recomienda evitar mensajes poco descriptivos como:

```
cambios
arreglo
final
prueba
cosas
```

# 10. Subida de la rama

Después de realizar y probar los cambios, la rama se sube al repositorio:

Bash

```
git push origin nombre-de-la-rama
```

Ejemplo:

Bash

```
git push origin feature/animales-catalogo
```

# 11. Pull Request

Después de subir la rama, se crea un Pull Request hacia:

```
main
```

El Pull Request debe incluir:

* Título descriptivo.

* Descripción de los cambios.

* Issue relacionado.

* Pruebas realizadas.

* Información sobre posibles cambios adicionales.

Ejemplo:

```
Título:

feat: implementar catálogo de animales

Descripción:

Se implementó el catálogo de animales con:
- listado de animales;
- filtros;
- acceso al detalle;
- imágenes;
- estados de adopción;
- control de favoritos.

Relacionado con:
#15
```

# 12. Revisión del código

Antes de realizar el merge, el Pull Request debe ser revisado por otro integrante del equipo.

La revisión debe comprobar principalmente:

* Que la funcionalidad solicitada esté implementada.

* Que no se hayan eliminado funcionalidades existentes.

* Que el código sea comprensible.

* Que no existan errores evidentes.

* Que las rutas funcionen correctamente.

* Que los permisos por rol sean respetados.

* Que los cambios no rompan otros módulos.

* Que las plantillas HTML/Jinja funcionen correctamente.

* Que el código mantenga la estructura del proyecto.

* Que no se hayan agregado credenciales o datos sensibles.

# 13. Pruebas antes del merge

Antes de aprobar el Pull Request se deben realizar las pruebas correspondientes.

Para módulos Python se puede comprobar que no existan errores de sintaxis mediante:

Bash

```
python -m py_compile modules/animals.py
```

También deben realizarse pruebas funcionales desde la aplicación.

Dependiendo del módulo modificado, se debe comprobar:

### Autenticación

* Registro.

* Inicio de sesión.

* Cierre de sesión.

* Permisos por rol.

### Animales

* Registro.

* Edición.

* Visualización.

* Eliminación.

* Filtros.

* Estado de adopción.

### Favoritos

* Agregar favorito.

* Eliminar favorito.

* Restricciones para animales adoptados.

### Adopciones

* Crear solicitud.

* Consultar solicitudes.

* Cambiar estados.

* Restricciones según el rol.

### Fundaciones

* Registro.

* Aprobación.

* Rechazo.

* Donaciones.

* Historial.

### Administración

* Acceso al panel.

* Estadísticas.

* Gestión de fundaciones.

* Permisos administrativos.

# 14. Análisis de seguridad

Antes de integrar los cambios se deben revisar las herramientas de análisis configuradas para el proyecto.

Entre ellas se encuentra:

Snyk

Snyk se utiliza para detectar posibles vulnerabilidades relacionadas con las dependencias y componentes utilizados por el proyecto.

Los resultados encontrados deben revisarse antes de integrar cambios cuando correspondan al código o dependencias modificadas.

También se deben evitar:

* Claves de Supabase dentro del código.

* Contraseñas.

* Tokens.

* Secretos.

* Archivos `.env`.

Las credenciales deben mantenerse mediante variables de entorno.

# 15. Reglas de aprobación

Un Pull Request puede ser aprobado únicamente cuando:

1. La funcionalidad solicitada está implementada.

2. Las pruebas correspondientes fueron realizadas.

3. No existen errores conocidos que bloqueen la funcionalidad.

4. Los cambios respetan la arquitectura existente.

5. Se respetan los permisos de los diferentes roles.

6. No se eliminan funcionalidades sin justificación.

7. No se incluyen credenciales o información sensible.

8. La revisión del código fue completada.

9. Las herramientas de análisis configuradas no presentan problemas críticos relacionados con el cambio.

10. El Pull Request cumple las reglas de Branch Protection establecidas para el repositorio.

# 16. Cambios solicitados durante la revisión

Si el revisor encuentra problemas, el Pull Request no debe integrarse inmediatamente.

Se solicitan cambios.

El integrante responsable realiza las correcciones en la misma rama.

Ejemplo:

Bash

```
git add -A

git commit -m "fix: corregir validación del catálogo"

git push origin feature/animales-catalogo
```

El Pull Request se actualiza automáticamente.

Después se realiza nuevamente la revisión.

El ciclo continúa hasta que los problemas encontrados sean corregidos.

# 17. Aprobación

Cuando el código cumple los requisitos establecidos, el revisor aprueba el Pull Request.

La aprobación significa que:

* La funcionalidad fue revisada.

* Los cambios son aceptables.

* Las pruebas necesarias fueron realizadas.

* No existen problemas bloqueantes conocidos.

La aprobación no sustituye las pruebas automáticas ni las comprobaciones de seguridad.

# 18. Merge

Una vez aprobado el Pull Request y cumplidas las reglas del repositorio, se realiza el merge hacia:

```
main
```

El proceso queda:

```
feature/*
      │
      ▼
Pull Request
      │
      ▼
Revisión
      │
      ▼
Aprobación
      │
      ▼
Merge
      │
      ▼
main
```

Después del merge se debe verificar que la rama principal continúe funcionando correctamente.

# 19. Resolución de conflictos

Si GitHub indica que existen conflictos antes del merge, el integrante responsable debe resolverlos.

Primero debe actualizar su rama con los cambios recientes de `main`.

Ejemplo:

Bash

```
git checkout feature/animales-catalogo

git pull origin main
```

Si existen conflictos, se deben resolver manualmente.

Después:

Bash

```
git add -A

git commit -m "fix: resolver conflictos de integración"

git push origin feature/animales-catalogo
```

Una vez resueltos los conflictos, el Pull Request debe volver a revisarse.

# 20. Reglas generales del equipo

Para mantener un flujo organizado se establecen las siguientes reglas:

* No realizar desarrollo directamente sobre `main`.

* Cada funcionalidad debe estar asociada a un Issue.

* Cada Issue debe desarrollarse en una rama correspondiente.

* Los nombres de las ramas deben ser descriptivos.

* Los commits deben explicar claramente el cambio realizado.

* Los Pull Requests deben describir qué se modificó.

* Los cambios deben ser revisados antes del merge.

* No se deben integrar cambios con errores conocidos que bloqueen la funcionalidad.

* No se deben subir credenciales ni secretos.

* Se deben respetar los permisos establecidos para cada rol.

* Los cambios que afecten varios módulos deben ser revisados cuidadosamente.

* Los conflictos deben resolverse antes del merge.

* La documentación debe actualizarse cuando cambie significativamente el funcionamiento del sistema.

# 21. Resumen del flujo

El flujo de trabajo de Tralaladopt queda definido de la siguiente manera:

```
┌──────────────┐
│    ISSUE     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  ASIGNACIÓN  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    RAMA      │
│ feature/fix  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  DESARROLLO  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    PRUEBAS   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     PUSH     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PULL REQUEST │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   REVISIÓN   │
└──────┬───────┘
       │
       ├───────────────┐
       │               │
       ▼               ▼
  CORRECCIONES     APROBACIÓN
       │               │
       └───────┐       │
               │       ▼
               │    ┌───────┐
               └───►│ MERGE │
                    └───┬───┘
                        │
                        ▼
                    ┌──────┐
                    │ main │
                    └──────┘
```
