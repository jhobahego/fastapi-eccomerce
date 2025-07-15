# 🧪 Infraestructura de Testing con PostgreSQL

## Descripción General

Este proyecto ahora soporta dos modalidades de testing:

1. **SQLite (rápido)**: Para desarrollo y tests unitarios rápidos
2. **PostgreSQL (producción-like)**: Para tests de integración y validación completa

## 🚀 Uso Rápido

### Tests Rápidos con SQLite (recomendado para desarrollo)
```bash
make test
# o
python -m pytest tests/ -v
```

### Tests Completos con PostgreSQL (recomendado para CI/CD)
```bash
make test-postgres
# o
./scripts/test-with-postgres.sh test
```

## 📋 Comandos Disponibles

### Comandos de Makefile

```bash
# Tests con SQLite (rápido)
make test                    # Todos los tests
make test-unit              # Solo tests unitarios
make test-api               # Solo tests de API
make test-integration       # Solo tests de integración
make test-coverage          # Tests con reporte de cobertura

# Tests con PostgreSQL (producción-like)
make test-postgres          # Todos los tests (auto start/stop)
make test-postgres-keep     # Tests manteniendo PostgreSQL activo
make test-postgres-down     # Bajar PostgreSQL de tests
make test-postgres-clean    # Limpiar completamente PostgreSQL
make test-coverage-postgres # Tests con cobertura usando PostgreSQL
```

### Script de Gestión PostgreSQL

```bash
# Gestión básica
./scripts/test-with-postgres.sh start    # Iniciar PostgreSQL
./scripts/test-with-postgres.sh stop     # Detener PostgreSQL
./scripts/test-with-postgres.sh clean    # Limpiar completamente
./scripts/test-with-postgres.sh status   # Ver estado

# Ejecutar tests
./scripts/test-with-postgres.sh test                      # Todos los tests
./scripts/test-with-postgres.sh test tests/test_api/     # Solo API tests
./scripts/test-with-postgres.sh test --cov=app          # Con cobertura
./scripts/test-with-postgres.sh test-keep               # Mantener BD activa
```

## 🐘 Configuración PostgreSQL

### Servicios Docker

El archivo `docker-compose.test.yml` define:

- **Servicio**: `db-test`
- **Puerto**: 5433 (para no conflictar con PostgreSQL de desarrollo)
- **Base de datos**: `ecommerce_test`
- **Usuario**: `test_user`
- **Contraseña**: `test_password`
- **Configuración**: Optimizada para tests (tmpfs, sin persistencia)

### Variables de Entorno

- `USE_POSTGRES_FOR_TESTS=true`: Activa PostgreSQL para tests
- `USE_POSTGRES_FOR_TESTS=false` (default): Usa SQLite

## 🔧 Instalación

### Dependencias Base (ya instaladas)
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Dependencias PostgreSQL para Tests
```bash
pip install -r requirements-postgres-test.txt
```

### Docker (requerido para PostgreSQL)
```bash
# Verificar que Docker está instalado
docker --version
docker-compose --version
```

## 📊 Comparación de Modalidades

| Aspecto | SQLite | PostgreSQL |
|---------|--------|------------|
| **Velocidad** | ⚡ Muy rápido | 🐌 Más lento |
| **Similitud con Producción** | ⚠️ Limitada | ✅ Completa |
| **Dependencias** | 📦 Mínimas | 🐳 Docker requerido |
| **Uso Recomendado** | Desarrollo diario | CI/CD, validación final |
| **Configuración** | 🎯 Automática | 🔧 Manual |
| **Tipos de Datos** | 🔄 Básicos | 🎯 PostgreSQL específicos |
| **Concurrencia** | ❌ Limitada | ✅ Real |

## 🏗️ Arquitectura de Testing

### Configuración Automática (`conftest.py`)

```python
# Detecta automáticamente el tipo de BD basado en variable de entorno
USE_POSTGRES_FOR_TESTS = os.getenv("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

if USE_POSTGRES_FOR_TESTS:
    # PostgreSQL para tests
    SQLALCHEMY_DATABASE_URL = "postgresql://test_user:test_password@localhost:5433/ecommerce_test"
else:
    # SQLite para tests rápidos
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
```

### Flujo de Testing

1. **Preparación**: 
   - SQLite: Automática
   - PostgreSQL: Inicia contenedor Docker

2. **Ejecución**: 
   - Mismos tests, diferentes motores de BD

3. **Limpieza**:
   - SQLite: Elimina archivo temporal
   - PostgreSQL: Destruye contenedor

## 🎯 Casos de Uso Recomendados

### Durante Desarrollo
```bash
# Tests rápidos durante desarrollo
make test

# Tests específicos
make test-unit
python -m pytest tests/test_models/ -v
```

### Antes de Commit
```bash
# Validación completa
make test-postgres
make test-coverage-postgres
```

### En CI/CD
```bash
# Pipeline completo
./scripts/test-with-postgres.sh test --cov=app --cov-report=xml
```

## 🐛 Troubleshooting

### PostgreSQL no inicia
```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar estado
./scripts/test-with-postgres.sh status

# Limpiar y reiniciar
./scripts/test-with-postgres.sh clean
./scripts/test-with-postgres.sh start
```

### Puerto 5433 ocupado
```bash
# Verificar qué está usando el puerto
lsof -i :5433

# Cambiar puerto en docker-compose.test.yml si es necesario
```

### Tests fallan solo con PostgreSQL
```bash
# Comparar resultados
make test                    # SQLite
make test-postgres-keep     # PostgreSQL (mantener activo)

# Debuggear con PostgreSQL activo
USE_POSTGRES_FOR_TESTS=true python -m pytest tests/test_specific.py -v -s
```

## 📈 Mejores Prácticas

### 1. Desarrollo Diario
- Usar SQLite para tests frecuentes
- Ejecutar PostgreSQL solo para validación

### 2. Integración Continua
- Siempre usar PostgreSQL en CI/CD
- Incluir tests de cobertura

### 3. Debugging
- Mantener PostgreSQL activo durante debugging
- Usar logs de Docker para diagnóstico

### 4. Performance
- SQLite para TDD y desarrollo rápido
- PostgreSQL para tests de performance

## 🔮 Próximas Mejoras

- [ ] Soporte para múltiples versiones de PostgreSQL
- [ ] Tests de migración automáticos
- [ ] Integración con GitHub Actions
- [ ] Métricas de performance comparativas
- [ ] Soporte para tests distribuidos

## 📚 Referencias

- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)
- [PostgreSQL Testing Best Practices](https://www.postgresql.org/docs/current/regress-run.html)
- [Docker Compose Testing](https://docs.docker.com/compose/)
