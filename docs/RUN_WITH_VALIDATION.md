# 🚀 Ejecución de Aplicación con Validación de Tests

## Descripción

Este documento describe cómo ejecutar la aplicación FastAPI con validación automática de tests, asegurando que solo se ejecute código que haya pasado las pruebas correspondientes.

## 🎯 Filosofía

> **"No Code Ships Without Tests"** - Ningún código se ejecuta sin haber pasado tests

Esta infraestructura implementa diferentes niveles de validación según el contexto:
- **Desarrollo diario**: Tests unitarios rápidos
- **Validación completa**: Tests con PostgreSQL
- **Deployment**: Validación exhaustiva con cobertura

## 🚀 Comandos Principales

### Makefile (Recomendado para uso frecuente)

```bash
# Desarrollo diario con validación rápida
make dev-safe                 # Tests SQLite + desarrollo completo
make quick-start              # Solo tests unitarios + inicio rápido
make run-safe                 # Tests SQLite + solo up (sin logs)

# Validación completa
make dev-postgres-safe        # Tests PostgreSQL + desarrollo
make run-postgres-safe        # Tests PostgreSQL + solo up

# Deployment con validación exhaustiva
make deploy-safe              # Tests SQLite + PostgreSQL + cobertura + prod
```

### Script Avanzado (Máxima flexibilidad)

```bash
# Modos principales
./scripts/run-with-tests.sh quick      # ⚡ Súper rápido (solo tests unitarios)
./scripts/run-with-tests.sh safe       # 🧪 Seguro (tests SQLite completos)
./scripts/run-with-tests.sh postgres   # 🐘 Completo (tests PostgreSQL)
./scripts/run-with-tests.sh deploy     # 🛡️ Exhaustivo (todos los tests)
./scripts/run-with-tests.sh coverage   # 📊 Con métricas de cobertura

# Opciones adicionales
./scripts/run-with-tests.sh safe --up-only        # Solo up, sin logs
./scripts/run-with-tests.sh postgres --prod       # Modo producción
./scripts/run-with-tests.sh quick --no-tests      # Emergencia (saltar tests)
```

## 📊 Niveles de Validación

### 1. Quick (⚡ Súper Rápido)
- **Tests**: Solo unitarios (models, schemas, services)
- **Tiempo**: ~10 segundos
- **Uso**: Desarrollo diario, iteración rápida
- **Base de datos**: SQLite en memoria

### 2. Safe (🧪 Seguro)
- **Tests**: Todos los tests con SQLite
- **Tiempo**: ~30 segundos
- **Uso**: Antes de commits, validación general
- **Base de datos**: SQLite

### 3. Postgres (🐘 Completo)
- **Tests**: Todos los tests con PostgreSQL
- **Tiempo**: ~45 segundos
- **Uso**: Validación pre-merge, tests de integración
- **Base de datos**: PostgreSQL Docker

### 4. Deploy (🛡️ Exhaustivo)
- **Tests**: SQLite + PostgreSQL + Cobertura
- **Tiempo**: ~90 segundos
- **Uso**: Antes de deployment, validación completa
- **Base de datos**: Ambas

### 5. Coverage (📊 Con Métricas)
- **Tests**: Con reporte de cobertura
- **Tiempo**: ~40 segundos
- **Uso**: Verificar calidad del código
- **Requisito**: Mínimo 80% de cobertura

## 🎯 Casos de Uso Recomendados

### Desarrollo Diario
```bash
# Inicio de día - verificación rápida
make quick-start

# Durante desarrollo - validación frecuente
make dev-safe

# Antes de commits
./scripts/run-with-tests.sh safe
```

### Validación Pre-Merge
```bash
# Validación completa antes de merge
./scripts/run-with-tests.sh postgres

# Con métricas de calidad
./scripts/run-with-tests.sh coverage
```

### Deployment
```bash
# Validación exhaustiva antes de deployment
make deploy-safe

# O usando el script
./scripts/run-with-tests.sh deploy
```

## 🔧 Configuración Adicional

### Hook de Pre-Commit (Opcional)

Para evitar commits con código roto:

```bash
# Instalar el hook
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Ahora cada commit ejecutará tests automáticamente
git commit -m "feat: nueva funcionalidad"
# -> Se ejecutan tests antes del commit
```

### Variables de Entorno

```bash
# Forzar uso de PostgreSQL para todos los tests
export USE_POSTGRES_FOR_TESTS=true

# Ejecutar cualquier comando de tests
make test  # Ahora usará PostgreSQL automáticamente
```

## 🚦 Flujo de Trabajo Recomendado

### 1. Inicio de Desarrollo
```bash
# Verificación rápida al iniciar
make quick-start
```

### 2. Durante Desarrollo
```bash
# Tests frecuentes durante desarrollo
make test-unit

# Validación periódica
make dev-safe
```

### 3. Antes de Commit
```bash
# Validación completa
./scripts/run-with-tests.sh safe

# O instalar el pre-commit hook para automatizar
```

### 4. Antes de Merge/Deploy
```bash
# Validación exhaustiva
./scripts/run-with-tests.sh deploy
```

## 🎨 Características del Script

### UI Amigable
- **Colores**: Información clara con códigos de color
- **Emojis**: Identificación visual rápida de estados
- **Progress**: Indicadores de progreso paso a paso

### Robustez
- **Validación de Docker**: Verifica que Docker esté corriendo
- **Manejo de errores**: Detiene ejecución si tests fallan
- **Cleanup automático**: PostgreSQL se limpia automáticamente

### Flexibilidad
- **Múltiples modos**: Desde rápido hasta exhaustivo
- **Opciones**: Personalización del comportamiento
- **Escape hatches**: Opción --no-tests para emergencias

## 🐛 Troubleshooting

### Tests fallan al iniciar aplicación
```bash
# Ver detalles de los tests que fallan
make test

# Ejecutar solo tests específicos
python -m pytest tests/test_api/test_auth.py -v

# Saltar tests temporalmente (solo emergencias)
./scripts/run-with-tests.sh safe --no-tests
```

### Docker no está disponible
```bash
# Verificar Docker
docker info

# Iniciar Docker si es necesario
sudo systemctl start docker  # Linux
# o iniciar Docker Desktop en macOS/Windows
```

### PostgreSQL no inicia
```bash
# Limpiar PostgreSQL de tests
make test-postgres-clean

# Verificar puertos
lsof -i :5433

# Ver logs de Docker
docker compose -f docker-compose.test.yml logs postgres-test
```

## 🔮 Próximas Mejoras

- [ ] Integración con GitHub Actions
- [ ] Tests paralelos para mayor velocidad
- [ ] Métricas de performance de tests
- [ ] Notificaciones automáticas
- [ ] Cache inteligente de tests

## 📚 Referencias

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [Docker Compose Testing](https://docs.docker.com/compose/)
- [Git Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
