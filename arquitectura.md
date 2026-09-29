# Arquitectura del Software - Sistema de Reclamos

Este documento describe la estructura arquitectónica, organización de componentes y mecanismos de comunicación externa para el prototipo de sistema de atención y gestión de reclamos de la Junta de Saneamiento de Bella Vista.

---

## 🏗️ 1. Patrón Arquitectónico

El sistema está estructurado bajo el patrón **Model-View-Controller (MVC)** (Arquitectura en Capas) proporcionado por el framework **Django**, que lo denomina **MTV** (Model - Template - View):

| Capa MVC | Nombre en Django | Ubicación en el proyecto |
|---|---|---|
| Modelo | Model | `reclamos_app/models/` |
| Vista | Template | `reclamos_app/templates/reclamos_app/` |
| Controlador | View | `reclamos_app/views/` |

- **Modelo (Model - Capa de Datos):** Define las entidades de la base de datos (Barrios, Roles, Usuarios y, en próximas etapas, Reclamos, Categorías, Historial/Comentarios y Notificaciones) e interactúa mediante el ORM de Django con la base de datos PostgreSQL.
- **Vista (Template - Capa de Presentación):** Renderiza la interfaz de usuario web responsiva utilizando HTML5, CSS3, JavaScript y Bootstrap para la interacción tanto del ciudadano como de los funcionarios administrativos.
- **Controlador (View - Capa de Negocio):** Procesa las peticiones HTTP, ejecuta la lógica de validación, gestiona el estado de los reclamos, procesa comentarios internos y coordina las llamadas a servicios externos (APIs).

### Flujo de una petición

```text
Navegador ──► reclamos/urls.py ──► reclamos_app/urls.py ──► Controlador (views/)
                                                               │
                                          consulta/guarda ◄────┤────► Modelo (models/) ◄──► PostgreSQL
                                                               │
Navegador ◄──────────── HTML ◄──────────── Vista (templates/) ◄┘
```

---

## 📁 2. Estructura de Directorios del Proyecto

```text
SistemaReclamosJSBV/
│
├── reclamos/                    # Configuración principal del proyecto Django
│   ├── settings.py              # Configuración (BD, idioma, apps instaladas)
│   ├── urls.py                  # Rutas principales
│   ├── wsgi.py / asgi.py        # Puntos de entrada del servidor
│
├── reclamos_app/                # Aplicación principal
│   ├── models/                  # MODELO: una entidad por archivo
│   │   ├── barrio.py
│   │   ├── rol.py
│   │   └── usuario.py
│   ├── views/                   # CONTROLADOR: lógica por entidad
│   │   ├── base.py              # Comportamiento común (crear, editar, eliminar)
│   │   ├── inicio.py
│   │   ├── barrios.py
│   │   ├── roles.py
│   │   └── usuarios.py
│   ├── templates/reclamos_app/  # VISTA: plantillas HTML
│   │   ├── base.html            # Plantilla base (menú, mensajes, Bootstrap)
│   │   ├── comun/               # Formularios, confirmaciones y paginación reutilizables
│   │   ├── barrios/
│   │   ├── roles/
│   │   └── usuarios/
│   ├── forms.py                 # Validación de formularios
│   ├── urls.py                  # Rutas de la aplicación
│   ├── admin.py                 # Configuración del panel de administración
│   └── migrations/              # Historial de cambios del esquema de la BD
│
├── docker-compose.yml           # Servicios: web (Django) y db (PostgreSQL)
├── Dockerfile                   # Imagen de la aplicación (Python 3.14)
├── requirements.txt             # Dependencias de Python
├── .env.example                 # Plantilla de variables de entorno
├── arquitectura.md              # Documentación técnica de la arquitectura del software
├── README.md                    # Descripción general del proyecto y entorno
└── manage.py                    # Script de gestión de comandos Django
```

### Módulos planificados

A medida que avance el desarrollo, cada módulo del sistema se incorporará siguiendo la misma organización (modelo, controlador y plantillas por entidad):

| Módulo | Contenido previsto |
|---|---|
| Usuarios y Autenticación | Inicio/cierre de sesión y permisos por rol (Administrador, Funcionario, Usuario) |
| Reclamos | Gestión de reclamos, estados, geolocalización y bitácora |
| Notificaciones | Integración con servicios de envío de SMS/Email |
| Reportes | Generación e impresión de informes |

También se incorporarán las carpetas `static/` (archivos CSS, JavaScript e imágenes propios) y `media/` (archivos adjuntos subidos por los usuarios, como evidencias o fotos).

---

## 🗄️ 3. Base de Datos

- **Motor:** PostgreSQL 16, ejecutado en un contenedor Docker (servicio `db`).
- **Base de datos:** `db_reclamos`.
- **Gestión del esquema:** las tablas se definen como modelos de Django y se crean mediante migraciones (`python manage.py migrate`). Los nombres de tablas y columnas respetan el diseño original (`"Barrios"`, `"Roles"`, `"Usuarios"`, `"Id_barrio"`, etc.) e incluyen los comentarios de cada columna.
- **Persistencia:** los datos se guardan en el volumen de Docker `postgres_data`.
- **Credenciales:** se leen de variables de entorno definidas en el archivo `.env`, que no se incluye en el repositorio.
