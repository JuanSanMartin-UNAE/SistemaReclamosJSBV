# Prototipo de Sistema de Atención y Gestión de Reclamos - Junta de Saneamiento de Bella Vista.

Prototipo de sistema informático web desarrollado como **Proyecto de Grado** para la carrera de Licenciatura en Análisis de Sistemas Informáticos de la **Universidad Autónoma de Encarnación (UNAE)**

---

## 📋 Descripción y Objetivo del Proyecto

El proyecto consiste en un prototipo de software web responsivo orientado a optimizar, modernizar y automatizar el flujo de atención, recepción, seguimiento y resolución de reclamos técnicos y comerciales de los usuarios de la **Junta de Saneamiento de la ciudad de Bella Vista - Itapúa**.

### Objetivos Principales:
**Centralizar y dar trazabilidad** a los reclamos desde su recepción hasta su resolución y cierre final.
**Facilitar el seguimiento en tiempo real** para los usuarios sin depender del horario de atención presencial u oficina.
**Optimizar la gestión interna** mediante la clasificación de reclamos, asignación de responsables, notas internas y generación de reportes e informes para la toma de decisiones.
**Integrar herramientas modernas** como geolocalización de incidentes y notificaciones automáticas ante cambios de estado.

---

## 🛠️ Entorno de Programación y Stack Tecnológico

El desarrollo sigue una arquitectura web responsiva basada en el siguiente stack tecnológico:

**Lenguaje de Programación:** Python 3.14.6
**IDE Utilizado:** Visual Studio Code / Cursor
**Backend Framework:** Django 5.2
**Frontend:** HTML5, CSS3, JavaScript y Bootstrap (diseño responsivo / adaptativo)
**Base de Datos:** PostgreSQL
**SQLAlchemy** biblioteca de código abierto para Python que permite conectar y gestionar bases de datos relacionales usando código en lugar de escribir consultas SQL tradicionales
**APIs & Servicios Externos:**
**Google Maps API:** Para geolocalización precisa de los incidentes/reclamos
**Twilio API:** Para el envío automatizado de notificaciones vía SMS / Correo Electrónico
**Herramientas de Control de Versiones & Asistencia:**
  * Git & GitHub
  * Asistencia de código y documentación mediante GitHub Copilot, Gemini y Claude (conforme a la Res. CSG Nº 33/2026 UNAE)

---

## 📦 Módulos Principales del Sistema

1. **Módulo de Usuarios y Autenticación:** Registro de usuarios externos, inicio/cierre de sesión seguro y gestión de roles (Administrador, Funcionario y Usuario)
2. **Módulo de Reclamos (Usuario Externo):** Formulario intuitivo de reporte con selección de tipo de reclamo, adjunto de imágenes y localización mediante mapa.
3. **Módulo Administrativo (Funcionario):** Panel general de reclamos con filtros, actualización de estados (Pendiente, En Proceso, Resuelto), asignación de técnicos y bitácora de notas internas.
4. **Módulo de Notificaciones:** Envíos automáticos por SMS/Correo ante cambios de estado o solicitudes de más datos.
5. **Módulo de Reportes e Informes:** Generación de planillas y reportes filtrados por fecha, barrio, tipo de reclamo y medidor.

---

## 👤 Información del Autor y Tutor

**Autor / Proyectista:** Juan María San Martín Ayala
**Tutor de Proyecto:** Lic. Pedro Ramón Danieli Acuña
**Institución:** Universidad Autónoma de Encarnación (UNAE) - Facultad de Ciencias, Artes y Tecnología (FACAT)
**Año:** 2026
