# 🧪 Guía Rápida de Tests - FastAPI Ecommerce

## ⚡ Instalación y Configuración Rápida

### 1. Instalar dependencias de testing

```bash
# Opción 1: Con el script
./run_tests.sh install

# Opción 2: Con pip directamente  
pip install -r requirements-test.txt

# Opción 3: Con make
make test-install
```

### 2. Verificar instalación

```bash
# Ejecutar test de configuración
pytest tests/test_setup.py -v
```

## 🚀 Ejecución de Tests

### Comandos Básicos

```bash
# Todos los tests
./run_tests.sh

# Tests específicos
./run_tests.sh unit           # Modelos, schemas, servicios
./run_tests.sh api            # Endpoints HTTP
./run_tests.sh integration    # Flujos completos
```

### Con Cobertura

```bash
# Generar reporte de cobertura
./run_tests.sh coverage

# Ver reporte HTML
open htmlcov/index.html
```

### Modo Desarrollo

```bash
# Auto-ejecutar al cambiar archivos
./run_tests.sh watch
```

## 📊 Estructura de Tests Creada

```
tests/
├── conftest.py              ✅ Configuración de pytest y fixtures
├── factories.py             ✅ Generadores de datos de prueba
├── test_setup.py            ✅ Verificación de configuración
├── test_models/             ✅ Tests de modelos SQLAlchemy
│   ├── test_user.py         ✅ Usuario: creación, validación, propiedades
│   ├── test_category.py     ✅ Categoría: jerarquías, validaciones
│   └── test_product.py      ✅ Producto: precios, stock, relaciones
├── test_schemas/            ✅ Tests de esquemas Pydantic
│   ├── test_user.py         ✅ Validaciones de entrada de usuario
│   ├── test_category.py     ✅ Validaciones de categoría
│   └── test_product.py      ✅ Validaciones de producto y búsqueda
├── test_services/           ✅ Tests de servicios de negocio
│   ├── test_user_service.py ✅ Autenticación, CRUD de usuarios
│   └── test_product_service.py ✅ Gestión de productos, stock, búsqueda
├── test_api/               ✅ Tests de endpoints HTTP
│   ├── test_health.py      ✅ Health checks y documentación
│   ├── test_auth.py        ✅ Login, registro, tokens, permisos
│   ├── test_users.py       ✅ CRUD usuarios, permisos admin
│   └── test_products.py    ✅ CRUD productos, búsqueda, stock
└── test_integration/       ✅ Tests de flujos completos
    └── test_ecommerce_workflow.py ✅ Workflows E2E
```

## 🎯 Cobertura de Testing

### ✅ Funcionalidades Probadas

**Modelos (SQLAlchemy)**
- ✅ Usuario: creación, validaciones, propiedades computed
- ✅ Categoría: jerarquías padre-hijo, validaciones
- ✅ Producto: precios, stock, relaciones con categoría

**Esquemas (Pydantic)**  
- ✅ Validaciones de entrada para todos los modelos
- ✅ Validaciones de negocio (precios, emails, etc.)
- ✅ Serialización y deserialización

**Servicios**
- ✅ UserService: autenticación, CRUD, validaciones
- ✅ ProductService: gestión completa de productos
- ✅ Validaciones de negocio y manejo de errores

**API Endpoints**
- ✅ Autenticación: login, registro, refresh tokens
- ✅ Usuarios: CRUD, permisos, perfil
- ✅ Productos: CRUD, búsqueda, gestión de stock
- ✅ Health checks y documentación

**Integración**
- ✅ Flujos completos de usuario
- ✅ Gestión completa de productos
- ✅ Manejo de errores y casos edge

## 🔧 Configuración Incluida

### Fixtures Principales
- `db_session`: Base de datos limpia por test
- `client`: Cliente HTTP FastAPI
- `superuser`, `regular_user`: Usuarios de prueba
- `category`, `product`: Datos de productos
- `auth_headers`, `user_auth_headers`: Autenticación

### Factories (Factory Boy)
- `UserFactory`: Genera usuarios realistas
- `ProductFactory`: Genera productos con datos válidos
- `CategoryFactory`: Genera categorías
- `OrderFactory`, `CartFactory`: Para futuras expansiones

### Base de Datos de Testing
- SQLite en memoria (rápido y aislado)
- Esquema completo de la aplicación
- Limpieza automática entre tests

## 📈 Métricas de Calidad

**Configuración para CI/CD**
- ✅ Pytest configurado con coverage
- ✅ HTML reports para coverage
- ✅ Marcadores para tipos de test
- ✅ Configuración de timeouts

**Performance**
- Tests unitarios: <1s cada uno
- Tests de API: <5s cada uno  
- Tests de integración: <30s cada uno

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error de dependencias**
   ```bash
   ./run_tests.sh install
   ```

2. **Base de datos bloqueada**
   ```bash
   ./run_tests.sh clean
   ```

3. **Tests fallan por permisos**
   ```bash
   chmod +x run_tests.sh
   ```

4. **Import errors**
   ```bash
   # Verificar que estás en el directorio correcto
   ls app/main.py
   ```

## 🚀 Comandos de Desarrollo

```bash
# Desarrollo día a día
./run_tests.sh watch          # Auto-ejecutar tests
./run_tests.sh unit           # Solo tests rápidos
./run_tests.sh coverage       # Verificar cobertura

# Antes de commit
./run_tests.sh                # Todos los tests
./run_tests.sh coverage       # Verificar cobertura >80%

# CI/CD
pytest tests/ --cov=app --cov-report=xml --junitxml=junit.xml
```

## 📚 Documentación Adicional

- **README.md principal**: Configuración del proyecto
- **tests/README.md**: Documentación detallada de tests
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Pytest**: https://docs.pytest.org/

## ✨ Próximos Pasos

Para expandir los tests:

1. **Agregar tests para Cart y Order**
2. **Tests de performance con pytest-benchmark**
3. **Tests E2E con Playwright**
4. **Tests de seguridad**
5. **Tests de carga con Locust**

---

¡Los tests están listos para usar! 🎉
