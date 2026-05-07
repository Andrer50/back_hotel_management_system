🏨 Hotel Management - Backend (Django API)
Este es el repositorio del backend para el proyecto de gestión hotelera. Está construido con Django y Django REST Framework, utilizando PostgreSQL como base de datos.

🚀 Guía de Inicio Rápido
Sigue estos pasos para configurar tu entorno local y empezar a desarrollar.

1. Clonar el repositorio y preparar el entorno
   Bash

# Crear el entorno virtual

python -m venv venv

# Activar el entorno virtual (Git Bash / macOS / Linux)

source venv/Scripts/activate

# Activar el entorno virtual (PowerShell)

# .\venv\Scripts\Activate.ps1

2. Instalar dependencias
   Asegúrate de tener el entorno virtual activo ((venv) debe aparecer en tu terminal).

Bash
pip install -r requirements.txt 3. Configuración de Base de Datos
Actualmente, el proyecto está preparado para conectarse a PostgreSQL.

Crea un archivo .env en la raíz basándote en el archivo .env.example.

Asegúrate de tener los accesos de la base de datos configurados.

4. Migraciones y Ejecución
   Una vez configurada la base de datos, prepara las tablas e inicia el servidor:

Bash

# Aplicar migraciones

python manage.py migrate

# Iniciar servidor de desarrollo

python manage.py runserver
La API estará disponible en: http://127.0.0.1:8000/

🛠️ Tecnologías utilizadas
Python 3.x

Django (Framework principal)

Django REST Framework (Para la creación de la API)

PostgreSQL (Motor de base de datos)

python-dotenv (Gestión de variables de entorno)

⚠️ Notas Importantes
[!IMPORTANT]
Base de Datos: Actualmente se planea usar una instancia de PostgreSQL en Render. Por ahora, asegúrate de tener una base de datos local para pruebas o solicita las credenciales del entorno de desarrollo.

¿Cómo contribuir?
Crea una nueva rama para tu funcionalidad: git checkout -b feat/nombre-de-la-mejora.

Realiza tus cambios y haz commit: git commit -m "feat: descripción del cambio".

Sube tus cambios: git push origin feat/nombre-de-la-mejora.
