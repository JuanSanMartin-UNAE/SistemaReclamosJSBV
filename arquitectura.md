# Arquitectura del Software - SistemaReclamamos

Este documento describe la estructura arquitectónica, organización de componentes y mecanismos de comunicación externa para el prototipo de sistema de atención y gestión de reclamos de la Junta de Saneamiento de Bella Vista.

---

## 🏗️ 1. Patrón Arquitectónico

El sistema está estructurado bajo el patrón **Model-View-Controller (MVC)** (Arquitectura en Capas) proporcionado por el framework **Django**:

**Modelo (Model - Capa de Datos):** Define las entidades de la base de datos (Usuarios, Reclamos, Categorías, Historial/Comentarios, Notificaciones) e interactúa mediante el ORM de Django con la base de datos PostgreSQL.
**Vista (View / Template - Capa de Presentación):** Renderiza la interfaz de usuario web responsiva utilizando HTML5, CSS3, JavaScript y Bootstrap para la interacción tanto del ciudadano como de los funcionarios administrativos.
**Controlador (Controller / View Logic - Capa de Negocio):** Procesa las peticiones HTTP, ejecuta la lógica de validación, gestiona el estado de los reclamos, procesa comentarios internos y coordina las llamadas a servicios externos (APIs).

---

## 📁 2. Estructura de Directorios del Proyecto

SistemaReclamamos/
│
├── config/                  # Configuración principal del proyecto Django (settings, urls, wsgi)
│
├── apps/                    # Módulos principales de la aplicación
│   ├── authentication/      # Gestión de usuarios, roles (Admin, Funcionario, Usuario) y autenticación
│   ├── reclamos/            # Gestión de reclamos, estados, geolocalización y bitácora
│   ├── notificaciones/      # Integración con servicios de envío de SMS/Email
│   └── reportes/            # Lógica para generación e impresión de informes
│
├── static/                  # Archivos estáticos globales (CSS, JavaScript, imágenes)
├── templates/               # Plantillas HTML base e interfaces del sistema
├── media/                   # Archivos adjuntos subidos por usuarios (evidencias/fotos)
│
├── arquitectura.md          # Documentación técnica de la arquitectura del software
├── README.md                # Descripción general del proyecto y entorno
└── manage.py                # Script de gestión de comandos Django
