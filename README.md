# 🏨 Hotel Management — Backend API

> API REST para el sistema de gestión hotelera, construida con Django y Django REST Framework sobre PostgreSQL.

---

## 📋 Tabla de contenidos

- [Tecnologías](#-tecnologías)
- [Inicio rápido](#-inicio-rápido)
- [Variables de entorno](#-variables-de-entorno)
- [Comandos útiles](#-comandos-útiles)
- [Contribuir](#-contribuir)

---

## 🛠️ Tecnologías

| Tecnología            | Versión | Propósito              |
| --------------------- | ------- | ---------------------- |
| Python                | 3.x     | Lenguaje base          |
| Django                | latest  | Framework principal    |
| Django REST Framework | latest  | Construcción de la API |
| PostgreSQL            | latest  | Motor de base de datos |
| python-dotenv         | latest  | Variables de entorno   |

---

## 🚀 Inicio rápido

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>
```

### 2. Crear y activar el entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar — macOS / Linux / Git Bash
source venv/bin/activate

# Activar — Windows PowerShell
.\venv\Scripts\Activate.ps1
```

> 💡 Verifica que el entorno esté activo: debe aparecer `(venv)` al inicio de tu terminal.

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

Edita `.env` con tus credenciales de base de datos. Ver sección [Variables de entorno](#-variables-de-entorno).

### 5. Aplicar migraciones e iniciar el servidor

```bash
python manage.py migrate
python manage.py runserver
```

✅ La API estará disponible en: **http://127.0.0.1:8000/**

---

## 🔐 Variables de entorno

Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example`:

```env
# Base de datos
DB_NAME=hotel_db
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=tu_secret_key
DEBUG=True
```

> ⚠️ **Nunca** subas el archivo `.env` al repositorio. Está incluido en `.gitignore`.

---

## ⚙️ Comandos útiles

```bash
# Crear nuevas migraciones tras modificar modelos
python manage.py makemigrations

# Aplicar migraciones pendientes
python manage.py migrate

# Crear superusuario para el admin de Django
python manage.py createsuperuser

# Ejecutar tests
python manage.py test
```

---

## ⚠️ Notas importantes

> [!IMPORTANT]
> **Base de datos en producción:** Se planea usar una instancia de PostgreSQL en Render.
> Para desarrollo local, configura una base de datos PostgreSQL propia o solicita las credenciales del entorno compartido al equipo.

> [!NOTE]
> Si no tienes PostgreSQL instalado localmente, puedes usar [Docker](https://docs.docker.com/get-docker/):
>
> ```bash
> docker run --name hotel-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
> ```

---

## 🤝 Contribuir

1. Crea una rama para tu funcionalidad:

   ```bash
   git checkout -b feat/nombre-de-la-mejora
   ```

2. Realiza tus cambios y haz commit siguiendo [Conventional Commits](https://www.conventionalcommits.org/):

   ```bash
   git commit -m "feat: descripción breve del cambio"
   ```

3. Sube tu rama:

   ```bash
   git push origin feat/nombre-de-la-mejora
   ```

4. Abre un **Pull Request** hacia `main` describiendo los cambios realizados.

### Tipos de commit

| Prefijo     | Uso                                          |
| ----------- | -------------------------------------------- |
| `feat:`     | Nueva funcionalidad                          |
| `fix:`      | Corrección de bug                            |
| `docs:`     | Cambios en documentación                     |
| `refactor:` | Refactorización sin cambio de comportamiento |
| `test:`     | Añadir o modificar tests                     |

---

_Proyecto desarrollado con ❤️ — cualquier duda, abre un issue._
