# Pasos para iniciar el proyecto

python -m venv venv # Crea su propio entorno virtual
source venv\Scripts\activate # Activa el entorno virtual en Windows
pip install -r requirements.txt # Instala las librerías del backend
python manage.py migrate # Crea las tablas en su base de datos local
python manage.py runserver # Inicia la API en el puerto 8000

# NOTA: Usaremos una base de datos postgresql en render, todavía falta configurar
