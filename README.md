# Prototipo de Sistema de Atención y Gestión de Reclamos - Junta de Saneamiento de Bella Vista

Prototipo de sistema informático web desarrollado como **Proyecto de Grado** para la carrera de Licenciatura en Análisis de Sistemas Informáticos de la **Universidad Autónoma de Encarnación (UNAE)**.

---

## 📋 Descripción y Objetivo del Proyecto

El proyecto consiste en un prototipo de software web responsivo orientado a optimizar, modernizar y automatizar el flujo de atención, recepción, seguimiento y resolución de reclamos técnicos y comerciales de los usuarios de la **Junta de Saneamiento de la ciudad de Bella Vista - Itapúa**.

### Objetivos Principales

- **Centralizar y dar trazabilidad** a los reclamos desde su recepción hasta su resolución y cierre final.
- **Facilitar el seguimiento en tiempo real** para los usuarios sin depender del horario de atención presencial u oficina.
- **Optimizar la gestión interna** mediante la clasificación de reclamos, asignación de responsables, notas internas y generación de reportes e informes para la toma de decisiones.
- **Integrar herramientas modernas** como geolocalización de incidentes y notificaciones automáticas ante cambios de estado.

---

## 🛠️ Entorno de Programación y Stack Tecnológico

El desarrollo sigue una arquitectura web responsiva basada en el siguiente stack tecnológico:

- **Lenguaje de Programación:** Python 3.14
- **IDE Utilizado:** Visual Studio Code / Cursor
- **Backend Framework:** Django 5.2 (LTS)
- **ORM:** ORM de Django, que permite definir y gestionar las tablas de la base de datos mediante clases de Python en lugar de escribir consultas SQL tradicionales
- **Frontend:** HTML5, CSS3, JavaScript y Bootstrap 5 (diseño responsivo / adaptativo)
- **Base de Datos:** PostgreSQL 16 (conector `psycopg` 3)
- **Contenedores:** Docker y Docker Compose para el entorno de desarrollo
- **APIs & Servicios Externos (planificados):**
  - **Google Maps API:** para geolocalización precisa de los incidentes/reclamos
  - **Twilio API:** para el envío automatizado de notificaciones vía SMS / Correo Electrónico
- **Herramientas de Control de Versiones & Asistencia:**
  - Git & GitHub
  - Asistencia de código y documentación mediante GitHub Copilot, Gemini y Claude (conforme a la Res. CSG Nº 33/2026 UNAE)

---

## 📦 Módulos Principales del Sistema

1. **Módulo de Usuarios y Autenticación:** Registro de usuarios externos, inicio/cierre de sesión seguro y gestión de roles (Administrador, Funcionario y Usuario).
2. **Módulo de Reclamos (Usuario Externo):** Formulario intuitivo de reporte con selección de tipo de reclamo, adjunto de imágenes y localización mediante mapa.
3. **Módulo Administrativo (Funcionario):** Panel general de reclamos con filtros, actualización de estados (Pendiente, En Proceso, Resuelto), asignación de técnicos y bitácora de notas internas.
4. **Módulo de Notificaciones:** Envíos automáticos por SMS/Correo ante cambios de estado o solicitudes de más datos.
5. **Módulo de Reportes e Informes:** Generación de planillas y reportes filtrados por fecha, barrio, tipo de reclamo y medidor.

### Estado actual del desarrollo

- [x] Entorno de desarrollo con Docker (Django + PostgreSQL)
- [x] Estructura MVC de la aplicación (ver [arquitectura.md](arquitectura.md))
- [x] Gestión de Barrios, Roles y Usuarios (alta, listado, edición y baja)
- [x] Panel de administración de Django
- [x] Tabla `Usuarios` como modelo de usuario de Django (inicio de sesión con número de documento)
- [ ] Pantallas de inicio de sesión, registro y recuperación de contraseña
- [ ] Permisos por rol
- [ ] Módulo de Reclamos
- [ ] Notificaciones, geolocalización y reportes

---

## 🚀 Instalación y Ejecución (entorno de desarrollo)

### Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/) o GitHub Desktop

### Pasos

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/JuanSanMartin-UNAE/SistemaReclamosJSBV.git
   cd SistemaReclamosJSBV
   ```
2. Crear el archivo de variables de entorno a partir de la plantilla y completar las contraseñas:
   ```bash
   cp .env.example .env
   ```
3. Levantar los contenedores:
   ```bash
   docker compose up -d --build
   ```
4. Crear las tablas en la base de datos:
   ```bash
   docker compose exec web python manage.py migrate
   ```
5. Crear un usuario administrador (se solicitará número de documento, nombre, apellido, teléfono y contraseña):
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
6. Abrir en el navegador:
   - Aplicación: <http://localhost:8000/>
   - Panel de administración: <http://localhost:8000/admin/>

### Comandos útiles

| Acción | Comando |
|---|---|
| Ver logs de la aplicación | `docker compose logs -f web` |
| Aplicar cambios de modelos | `docker compose exec web python manage.py makemigrations` y luego `migrate` |
| Detener los contenedores | `docker compose down` |
| Respaldar la base de datos | `docker compose exec db pg_dump -U usuario_django db_reclamos > respaldo.sql` |

> La base de datos se conserva en el volumen de Docker `postgres_data`. El comando `docker compose down -v` **elimina** ese volumen y todos sus datos.

---

## 👤 Información del Autor y Tutor

- **Autor / Proyectista:** Juan María San Martín Ayala
- **Tutor de Proyecto:** Lic. Pedro Ramón Danieli Acuña
- **Institución:** Universidad Autónoma de Encarnación (UNAE) - Facultad de Ciencias, Artes y Tecnología (FACAT)
- **Año:** 2026
