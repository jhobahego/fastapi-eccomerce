# 📚 Documentación del Proyecto

Bienvenido al centro de documentación del FastAPI Ecommerce Backend. Aquí encontrarás todas las guías necesarias para configurar, desarrollar y hacer testing del proyecto.

## 📋 Índice de Documentación

### 🚀 Configuración y Setup
- **[SETUP.md](SETUP.md)** - Guía detallada de configuración inicial
  - Instalación paso a paso multiplataforma
  - Configuración de variables de entorno
  - Setup de base de datos y migraciones
  - Troubleshooting común

### 🧪 Testing
- **[TESTING.md](TESTING.md)** - Guía completa de testing
  - Suite de tests unitarios, de API e integración
  - Comandos de testing y configuración
  - Factories y fixtures
  - Métricas de cobertura

- **[TESTING_POSTGRESQL.md](TESTING_POSTGRESQL.md)** - Testing avanzado con PostgreSQL
  - Infraestructura Docker para testing
  - Testing con base de datos de producción
  - Comandos específicos de PostgreSQL
  - Comparación SQLite vs PostgreSQL

### 🔧 Desarrollo y Ejecución
- **[RUN_WITH_VALIDATION.md](RUN_WITH_VALIDATION.md)** - Ejecución con validación automática
  - Sistema de validación con tests previos
  - Diferentes niveles de validación
  - Scripts avanzados de ejecución
  - Workflow de desarrollo recomendado

## 🎯 Flujo de Documentación Recomendado

### Para nuevos desarrolladores:
1. **Inicio**: Leer `README.md` principal para visión general
2. **Configuración**: Seguir `SETUP.md` para configuración inicial
3. **Testing**: Familiarizarse con `TESTING.md`
4. **Desarrollo**: Usar `RUN_WITH_VALIDATION.md` para workflow diario

### Para desarrolladores experimentados:
- **Testing avanzado**: `TESTING_POSTGRESQL.md`
- **Validación continua**: `RUN_WITH_VALIDATION.md`
- **Configuración específica**: `SETUP.md` secciones avanzadas

## 🔗 Enlaces Rápidos

### Comandos más usados:
```bash
# Configuración inicial
make init                        # o python scripts/init-project.py

# Testing
make test                        # Tests rápidos (SQLite)
make test-postgres              # Tests con PostgreSQL
make test-coverage              # Tests con cobertura

# Desarrollo con validación
make dev-safe                   # Desarrollo con tests SQLite
make dev-postgres-safe          # Desarrollo con tests PostgreSQL
make quick-start                # Inicio rápido
```

### Herramientas disponibles:
- **Scripts de automatización**: `scripts/` directory
- **Comandos Makefile**: `make help` para lista completa
- **Docker**: `docker-compose.yml` y `docker-compose.test.yml`

## 📖 Contribuir a la Documentación

Si encuentras algo que falta o que se puede mejorar:

1. La documentación sigue el formato Markdown
2. Mantén la consistencia con el estilo existente
3. Incluye ejemplos prácticos cuando sea posible
4. Actualiza este índice cuando agregues nueva documentación

## 🚀 ¿Necesitas ayuda?

- **Configuración inicial**: Ver `SETUP.md`
- **Testing**: Ver `TESTING.md`
- **Problemas específicos**: Revisar secciones de troubleshooting
- **Comandos disponibles**: `make help`
