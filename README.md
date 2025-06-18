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
    Crea un archivo `.env` en la raíz del proyecto basándote en la configuración requerida en `app/config.py`. (Toma el archivo `.env.example` como guia). Como mínimo, necesitarás configurar las siguientes:
    ```env
    DATABASE_URL=postgresql://user:password@host:port/database_name
    SECRET_KEY=tu_super_secreto_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ADMIN_EMAIL=admin@example.com
    ADMIN_PASSWORD=admin_secure_password
    ```

5.  **Configurar y ejecutar las migraciones de la base de datos (Alembic):**
    Asegúrate de que tu base de datos esté en funcionamiento y que las variables de entorno estén configuradas.
    
    **Primera vez (crear migración inicial):**
    ```bash
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
    ```
    
    **Ejecuciones posteriores (aplicar migraciones):**
    ```bash
    alembic upgrade head
    ```

6.  **Poblar la base de datos con datos iniciales:**
    Ejecuta el script de seeding para crear el superusuario inicial:
    ```bash
    python -m app.utils.seed_database
    ```

7.  **Iniciar la aplicación FastAPI:**
    El servidor de desarrollo Uvicorn se utilizará para ejecutar la aplicación.
    ```bash
    uvicorn app.main:app --reload
    ```
    La opción `--reload` permite que el servidor se reinicie automáticamente tras detectar cambios en el código.

8.  **Acceder a la API:**
    Una vez que el servidor esté en funcionamiento, podrás acceder a la documentación interactiva de la API (Swagger UI) en tu navegador en la siguiente URL:
    [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

    Y a la documentación alternativa (ReDoc):
    [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Configuración de Alembic

Este proyecto usa Alembic para gestionar las migraciones de la base de datos de forma segura y versionada.

### Archivos de configuración:
- `alembic.ini`: Configuración principal de Alembic
- `alembic/env.py`: Script de entorno que carga dinámicamente la `DATABASE_URL` desde tu archivo `.env`

### Variables de entorno requeridas:
Asegúrate de que tu archivo `.env` contenga al menos:
```env
DATABASE_URL=postgresql://user:password@host:port/database_name
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin_secure_password
```

## Scripts de utilidad

El proyecto incluye scripts de utilidad en el directorio `app/utils/`. Para ejecutar estos scripts, asegúrate de tener el entorno virtual activado.

### Crear superusuario
El script `app/utils/make_superuser.py` asigna permisos de superusuario a un usuario existente (útil para desarrollo).

**Pasos:**
1.  Asegúrate de que el usuario ya esté registrado en la aplicación.
2.  Establece la variable de entorno `ADMIN_EMAIL` en tu archivo `.env` con el correo del usuario.
3.  Ejecuta el script:
    ```bash
    python app/utils/make_superuser.py
    ```

### Poblar base de datos inicial
El script `app/utils/seed_database.py` crea datos iniciales esenciales (superusuario, categorías, etc.) para el funcionamiento de la aplicación.

Para ejecutarlo:
```bash
python -m app.utils.seed_database
```

**Nota:** Este script se ejecuta automáticamente en el flujo de configuración inicial descrito anteriormente.

## Estructura del Proyecto (resumen)

```
.
├── alembic.ini         # Configuración principal de Alembic
├── alembic/            # Configuración y scripts de migración de Alembic
│   ├── env.py          # Script de entorno (carga DATABASE_URL dinámicamente)
│   └── versions/       # Archivos de migración generados automáticamente
├── app/                # Directorio principal de la aplicación FastAPI
│   ├── api/            # Módulos de los endpoints de la API
│   ├── core/           # Configuración central, seguridad
│   ├── models/         # Modelos de SQLAlchemy (tablas de la base de datos)
│   ├── repositories/   # Lógica de acceso a datos
│   ├── schemas/        # Modelos Pydantic (validación y serialización de datos)
│   ├── services/       # Lógica de negocio
│   ├── utils/          # Scripts de utilidad (make_superuser.py, seed_database.py)
│   ├── config.py       # Configuración de la aplicación (variables de entorno)
│   ├── database.py     # Configuración de la base de datos y sesión de SQLAlchemy
│   └── main.py         # Punto de entrada de la aplicación FastAPI
├── tests/              # Pruebas unitarias e de integración
├── .env                # Variables de entorno (DATABASE_URL, ADMIN_EMAIL, etc.)
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Este archivo
```