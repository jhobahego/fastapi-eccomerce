# Backend eccomerce con FastAPI

Este proyecto es el backend de una aplicación de comercio electrónico desarrollado utilizando el framework FastAPI en Python.

## 🚀 Inicio Rápido (Recomendado)

**¿Primera vez usando este proyecto?** Sigue nuestra guía de inicio rápido multiplataforma:

### Para cualquier sistema operativo:
```bash
# Clonar e inicializar con Python (funciona en Windows, macOS y Linux)
git clone <tu-repositorio>
cd backend-fastapi
python scripts/init-project.py
```

### Alternativas por sistema operativo:
- **Linux/macOS**: `make init` o `./scripts/init-project.sh`
- **Windows PowerShell**: `.\scripts\init-project.ps1`
- **Windows CMD**: `.\scripts\init-project.bat`

📖 **Guía completa**: Ver [docs/SETUP.md](docs/SETUP.md) para instrucciones detalladas.

---

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

## 🧪 Testing

Este proyecto incluye una suite completa de tests unitarios, de integración y de API siguiendo las mejores prácticas de FastAPI.

### ⚡ Inicio Rápido con Testing

```bash
# Desarrollo diario con validación
make dev-safe                    # Tests SQLite + desarrollo completo
make quick-start                 # Tests unitarios + inicio rápido

# Validación completa  
make dev-postgres-safe           # Tests PostgreSQL + desarrollo
./scripts/run-with-tests.sh postgres  # Validación exhaustiva
```

### 🎯 Comandos de Testing Disponibles

```bash
# Testing básico
make test                        # Tests rápidos (SQLite)
make test-unit                   # Solo tests unitarios
make test-api                    # Solo tests de API
make test-integration            # Solo tests de integración

# Testing avanzado
make test-postgres              # Tests con PostgreSQL
make test-coverage              # Tests con reporte de cobertura
make test-coverage-postgres     # Cobertura con PostgreSQL

# Scripts especializados
./scripts/run-with-tests.sh quick      # ⚡ Súper rápido
./scripts/run-with-tests.sh safe       # 🧪 Validación estándar
./scripts/run-with-tests.sh postgres   # 🐘 Validación completa
./scripts/run-with-tests.sh deploy     # 🛡️ Validación exhaustiva
```

### 📊 Tipos de Tests Incluidos

- **Tests Unitarios**: Modelos, schemas y servicios (78 tests)
- **Tests de API**: Endpoints HTTP y autenticación (47 tests)
- **Tests de Integración**: Flujos completos de la aplicación (20 tests)
- **Total**: 145+ tests con >95% de cobertura

### 🎨 Características Avanzadas

- **🐘 PostgreSQL Testing**: Tests con base de datos de producción
- **🔄 Validación Automática**: Aplicación solo se ejecuta si tests pasan
- **📊 Métricas de Calidad**: Cobertura objetivo >80%
- **⚡ Testing Rápido**: SQLite en memoria para desarrollo diario
- **🛡️ Testing Robusto**: PostgreSQL Docker para validación completa

### 🚀 Filosofía "No Code Ships Without Tests"

```bash
# El sistema garantiza calidad ejecutando tests antes de la aplicación
make dev-safe                    # ✅ Solo se ejecuta si tests pasan
./scripts/run-with-tests.sh safe # ✅ Validación automática incluida
```

📖 **Documentación completa**: Ver [docs/TESTING.md](docs/TESTING.md) para guía detallada de tests.

---

## 🚀 Despliegue en Render

Este proyecto está configurado para desplegarse fácilmente en [Render](https://render.com) usando Docker y PostgreSQL.

### Configuración automática con render.yaml

El archivo `render.yaml` contiene toda la configuración necesaria para el despliegue automático:

1. **PostgreSQL Database**: Base de datos gratuita en Render
2. **Web Service**: Aplicación FastAPI con Docker
3. **Variables de entorno**: Configuración automática y manual

### Pasos para desplegar:

1. **Conectar repositorio a Render**:
   - Ve a [render.com](https://render.com) y crea una cuenta
   - Conecta tu cuenta de GitHub
   - Selecciona este repositorio

2. **Render detectará automáticamente el `render.yaml`**:
   - Confirmará la creación de PostgreSQL database
   - Creará el web service con configuración Docker

3. **Configurar variables de entorno manualmente** en el dashboard de Render:
   ```
   ADMIN_EMAIL=tu_email@example.com
   ADMIN_PASSWORD=tu_password_seguro
   BACKEND_CORS_ORIGINS=["https://tu-frontend.vercel.app"]
   ```

4. **Variables automáticas** (Render las configura):
   - `DATABASE_URL`: Conexión a PostgreSQL
   - `SECRET_KEY`: Clave generada automáticamente
   - `PORT`: Puerto dinámico de Render

### URLs después del despliegue:
- **API**: `https://tu-app.onrender.com`
- **Documentación**: `https://tu-app.onrender.com/docs`
- **API v1**: `https://tu-app.onrender.com/api/v1`

📖 **Guía completa**: Ver `render.yaml` y `scripts/render-deploy.sh` para detalles técnicos.

---

## Estructura del Proyecto

```
.
├── 📁 alembic/                         # Migraciones de base de datos
│   ├── env.py                          # Configuración de entorno Alembic
│   └── versions/                       # Archivos de migración generados
├── 📁 app/                             # Aplicación principal FastAPI
│   ├── 📁 api/                         # Endpoints de la API
│   │   └── api_v1/                     # Versión 1 de la API
│   │       ├── endpoints/              # Controladores HTTP específicos
│   │       │   ├── auth.py             # Autenticación y autorización
│   │       │   ├── users.py            # Gestión de usuarios
│   │       │   ├── products.py         # Gestión de productos
│   │       │   └── categories.py       # Gestión de categorías
│   │       └── api.py                  # Router principal de la API
│   ├── 📁 core/                        # Configuración central
│   │   └── security.py                 # JWT, hashing, autenticación
│   ├── 📁 models/                      # Modelos SQLAlchemy (base de datos)
│   │   ├── user.py                     # Modelo de usuarios
│   │   ├── product.py                  # Modelo de productos
│   │   ├── category.py                 # Modelo de categorías
│   │   ├── cart.py                     # Modelo de carrito
│   │   └── order.py                    # Modelo de pedidos
│   ├── 📁 repositories/                # Lógica de acceso a datos
│   │   ├── base.py                     # Repositorio base
│   │   ├── user_repository.py          # Repositorio de usuarios
│   │   └── product_repository.py       # Repositorio de productos
│   ├── 📁 schemas/                     # Esquemas Pydantic (validación)
│   │   ├── user.py                     # Esquemas de usuario
│   │   ├── product.py                  # Esquemas de producto
│   │   ├── category.py                 # Esquemas de categoría
│   │   └── token.py                    # Esquemas de tokens JWT
│   ├── 📁 services/                    # Lógica de negocio
│   │   ├── base.py                     # Servicio base
│   │   ├── user_service.py             # Servicios de usuario
│   │   └── product_service.py          # Servicios de producto
│   ├── 📁 utils/                       # Scripts de utilidad
│   │   ├── make_superuser.py           # Crear superusuarios
│   │   └── seed_database.py            # Poblar base de datos inicial
│   ├── config.py                       # Configuración (variables de entorno)
│   ├── database.py                     # Configuración de SQLAlchemy
│   └── main.py                         # Punto de entrada FastAPI
├── 📁 tests/                           # Suite completa de testing
│   ├── 📁 test_api/                    # Tests de endpoints HTTP
│   │   ├── test_auth.py                # Tests de autenticación
│   │   ├── test_users.py               # Tests de endpoints de usuarios
│   │   ├── test_products.py            # Tests de endpoints de productos
│   │   └── test_categories.py          # Tests de endpoints de categorías
│   ├── 📁 test_integration/            # Tests de flujos completos
│   │   └── test_ecommerce_workflow.py  # Tests de flujos E2E
│   ├── 📁 test_models/                 # Tests de modelos SQLAlchemy
│   ├── 📁 test_schemas/                # Tests de esquemas Pydantic
│   ├── 📁 test_services/               # Tests de servicios de negocio
│   ├── conftest.py                     # Configuración de pytest y fixtures
│   └── factories.py                    # Factories para generación de datos
├── 📁 scripts/                         # Scripts de automatización
│   ├── init-project.sh                 # Inicialización multiplataforma
│   ├── init-project.ps1               # Script para Windows PowerShell
│   ├── init-project.bat               # Script para Windows CMD
│   ├── init-project.py                # Script Python universal
│   ├── run-with-tests.sh              # Ejecución con validación de tests
│   ├── test-with-postgres.sh          # Testing con PostgreSQL
│   └── pre-commit-hook.sh             # Hook de pre-commit con tests
├── 📁 docs/                            # Documentación completa del proyecto
│   ├── README.md                       # Índice de documentación
│   ├── SETUP.md                        # Guía detallada de configuración inicial
│   ├── TESTING.md                      # Guía completa de testing
│   ├── TESTING_POSTGRESQL.md           # Testing avanzado con PostgreSQL
│   └── RUN_WITH_VALIDATION.md          # Ejecución con validación automática
├── 🐳 docker-compose.yml               # Servicios principales (desarrollo)
├── 🐳 docker-compose.test.yml          # PostgreSQL para testing
├── 🐳 Dockerfile                       # Imagen Docker de la aplicación
├── 📋 Makefile                         # Comandos de automatización y desarrollo
├── 📋 alembic.ini                      # Configuración principal de Alembic
├── 📦 requirements.txt                 # Dependencias principales del proyecto
├── 📦 requirements-postgres-test.txt   # Dependencias específicas para testing
├── 🔧 .env                             # Variables de entorno (no en git)
├── 🔧 .env.example                     # Ejemplo de configuración
├── 🔧 .gitignore                       # Archivos ignorados por Git
├── 🔧 pytest.ini                       # Configuración de pytest
└── 📖 README.md                        # Este archivo
```

### 🏗️ **Arquitectura del proyecto:**

- **📱 Frontend-Ready API**: Diseñada para ser consumida por aplicaciones frontend modernas
- **🧪 Testing Robusto**: Suite completa con SQLite/PostgreSQL, cobertura >95%
- **🐳 Containerización**: Docker Compose para desarrollo y testing
- **🔄 CI/CD Ready**: Scripts automatizados para validación continua
- **📚 Documentación**: Guías detalladas para desarrollo y deployment
- **⚡ Desarrollo Ágil**: Comandos Makefile para todas las operaciones comunes

### 🎯 **Comandos principales:**

```bash
# Desarrollo con validación
make dev-safe                    # Desarrollo con tests SQLite
make dev-postgres-safe           # Desarrollo con tests PostgreSQL
make quick-start                 # Inicio rápido con validación mínima

# Testing
make test                        # Tests rápidos (SQLite)
make test-postgres              # Tests con PostgreSQL
make test-coverage              # Tests con reporte de cobertura

# Docker
make up                         # Levantar aplicación
make down                       # Bajar aplicación
make logs                       # Ver logs en tiempo real

# Scripts avanzados
./scripts/run-with-tests.sh quick      # Desarrollo diario rápido
./scripts/run-with-tests.sh postgres   # Validación completa
./scripts/test-with-postgres.sh test   # Solo testing PostgreSQL
```

### 📚 **Documentación detallada**:
- **[Configuración inicial](docs/SETUP.md)**: Guía paso a paso multiplataforma
- **[Testing completo](docs/TESTING.md)**: Suite de testing y mejores prácticas  
- **[Testing PostgreSQL](docs/TESTING_POSTGRESQL.md)**: Testing con base de datos de producción
- **[Ejecución con validación](docs/RUN_WITH_VALIDATION.md)**: Desarrollo con tests automáticos
- **[Índice de documentación](docs/README.md)**: Navegación completa de guías