# Backend eccomerce con FastAPI

Este proyecto es el backend de una aplicación de comercio electrónico desarrollado utilizando el framework FastAPI en Python.

## Descripción

El backend proporciona una API RESTful para gestionar diversas funcionalidades de una tienda en línea, incluyendo:

*   Gestión de usuarios y autenticación (JWT).
*   Gestión de productos y categorías.
*   Gestión de carritos de compra.
*   Gestión de pedidos.

Utiliza SQLAlchemy como ORM para la interacción con la base de datos y Pydantic para la validación de datos y la definición de esquemas. Alembic se encarga de las migraciones de la base de datos.

## Requisitos

Para ejecutar este proyecto localmente, necesitarás tener instalado Python 3.8 o superior. Las dependencias del proyecto se listan en el archivo `requirements.txt`. Las principales dependencias incluyen:

*   fastapi
*   uvicorn
*   SQLAlchemy
*   psycopg2-binary (para PostgreSQL)
*   alembic
*   python-jose[cryptography] (para JWT)
*   passlib[bcrypt] (para hashing de contraseñas)
*   pydantic
*   python-dotenv

Se recomienda utilizar un entorno virtual para gestionar las dependencias.

## Instrucciones para arrancar el proyecto en la máquina local

1.  **Clonar el repositorio (si aplica):**
    ```bash
    git clone <url-del-repositorio>
    cd backend-fastapi
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar las variables de entorno:**
    Crea un archivo `.env` en la raíz del proyecto a partir del archivo `.env.example` (si existe) o basándote en la configuración requerida en `app/config.py`. Como mínimo, necesitarás configurar la URL de la base de datos (`DATABASE_URL`).
    Ejemplo de contenido para `.env`:
    ```env
    DATABASE_URL=postgresql://user:password@host:port/database_name
    SECRET_KEY=tu_super_secreto_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  **Ejecutar las migraciones de la base de datos (Alembic):**
    Asegúrate de que tu base de datos esté en funcionamiento.
    ```bash
    alembic upgrade head
    ```

6.  **Iniciar la aplicación FastAPI:**
    El servidor de desarrollo Uvicorn se utilizará para ejecutar la aplicación.
    ```bash
    uvicorn app.main:app --reload
    ```
    La opción `--reload` permite que el servidor se reinicie automáticamente tras detectar cambios en el código.

7.  **Acceder a la API:**
    Una vez que el servidor esté en funcionamiento, podrás acceder a la documentación interactiva de la API (Swagger UI) en tu navegador en la siguiente URL:
    [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

    Y a la documentación alternativa (ReDoc):
    [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Estructura del Proyecto (resumen)

```
.
├── alembic/            # Configuración y scripts de migración de Alembic
├── app/                # Directorio principal de la aplicación FastAPI
│   ├── api/            # Módulos de los endpoints de la API
│   ├── core/           # Configuración central, seguridad
│   ├── models/         # Modelos de SQLAlchemy (tablas de la base de datos)
│   ├── repositories/   # Lógica de acceso a datos
│   ├── schemas/        # Modelos Pydantic (validación y serialización de datos)
│   ├── services/       # Lógica de negocio (si es necesario)
│   ├── utils/          # Funciones de utilidad
│   ├── config.py       # Configuración de la aplicación (variables de entorno)
│   ├── database.py     # Configuración de la base de datos y sesión de SQLAlchemy
│   └── main.py         # Punto de entrada de la aplicación FastAPI
├── tests/              # Pruebas unitarias e de integración
├── .env.example        # Ejemplo de archivo de variables de entorno (si se proporciona)
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Este archivo
```