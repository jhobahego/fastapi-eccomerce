# Tests - FastAPI Ecommerce Backend

Este directorio contiene todos los tests para el backend de la aplicación de ecommerce desarrollada con FastAPI.

## 📁 Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py                 # Configuración y fixtures de pytest
├── factories.py                # Factory classes para generar datos de prueba
├── test_models/               # Tests para modelos de SQLAlchemy
│   ├── test_user.py
│   ├── test_category.py
│   └── test_product.py
├── test_schemas/              # Tests para esquemas de Pydantic
│   ├── test_user.py
│   ├── test_category.py
│   └── test_product.py
├── test_services/             # Tests para servicios de negocio
│   ├── test_user_service.py
│   └── test_product_service.py
├── test_api/                  # Tests para endpoints de la API
│   ├── test_auth.py
│   ├── test_health.py
│   ├── test_users.py
│   └── test_products.py
└── test_integration/          # Tests de integración
    └── test_ecommerce_workflow.py
```

## 🛠️ Configuración de Testing

### Dependencias

Las dependencias de testing están definidas en `requirements-test.txt`:

- **pytest**: Framework de testing principal
- **pytest-asyncio**: Soporte para tests asíncronos
- **pytest-cov**: Reporte de cobertura de código
- **pytest-mock**: Utilidades de mocking
- **httpx**: Cliente HTTP para tests de API
- **faker**: Generación de datos falsos
- **factory-boy**: Factory classes para crear objetos de prueba

### Base de Datos de Testing

Los tests utilizan una base de datos SQLite en memoria para garantizar:
- **Aislamiento**: Cada test tiene su propia base de datos limpia
- **Velocidad**: SQLite en memoria es muy rápido
- **Independencia**: No afecta la base de datos de desarrollo

## 🚀 Ejecución de Tests

### Método 1: Script de Testing (Recomendado)

```bash
# Instalar dependencias de testing
./run_tests.sh install

# Ejecutar todos los tests
./run_tests.sh

# Ejecutar tests específicos
./run_tests.sh unit           # Solo tests unitarios
./run_tests.sh api            # Solo tests de API
./run_tests.sh integration    # Solo tests de integración
./run_tests.sh coverage       # Tests con reporte de cobertura
./run_tests.sh watch          # Modo watch (re-ejecuta al cambiar archivos)

# Limpiar archivos de test
./run_tests.sh clean
```

### Método 2: Makefile

```bash
# Instalar dependencias
make test-install

# Ejecutar tests
make test                # Todos los tests
make test-unit          # Tests unitarios
make test-api           # Tests de API
make test-integration   # Tests de integración
make test-coverage      # Tests con cobertura
make test-watch         # Modo watch

# Limpiar
make test-clean
```

### Método 3: pytest directamente

```bash
# Instalar dependencias
pip install -r requirements-test.txt

# Ejecutar tests
pytest tests/ -v                                    # Todos los tests
pytest tests/test_models -v                         # Solo modelos
pytest tests/test_api -v                           # Solo API
pytest tests/test_integration -v -m integration    # Solo integración
pytest tests/ --cov=app --cov-report=html         # Con cobertura
```

## 📊 Reporte de Cobertura

Para generar un reporte de cobertura de código:

```bash
./run_tests.sh coverage
```

Esto generará:
- Reporte en terminal
- Reporte HTML en `htmlcov/index.html`

El objetivo es mantener una cobertura mínima del 80%.

## 🔧 Fixtures Principales

### Fixtures de Base de Datos

- `db_engine`: Motor de base de datos SQLite para tests
- `db_session`: Sesión de base de datos que se limpia después de cada test

### Fixtures de Cliente

- `client`: Cliente de testing FastAPI con override de dependencias

### Fixtures de Datos

- `superuser`: Usuario administrador para tests
- `regular_user`: Usuario regular para tests
- `category`: Categoría de productos para tests
- `product`: Producto para tests

### Fixtures de Autenticación

- `auth_headers`: Headers de autorización para superusuario
- `user_auth_headers`: Headers de autorización para usuario regular

## 🏭 Factory Classes

Se utilizan factories para generar datos de prueba consistentes:

```python
from tests.factories import UserFactory, ProductFactory, CategoryFactory

# Crear un usuario de prueba
user = UserFactory()

# Crear un producto con categoría específica
product = ProductFactory(category_id=1)

# Crear categoría con valores específicos
category = CategoryFactory(name="Electronics")
```

## 📝 Tipos de Tests

### Tests Unitarios

Prueban componentes individuales en aislamiento:
- **Modelos**: Validaciones, propiedades, relaciones
- **Schemas**: Validaciones de Pydantic, serialización
- **Servicios**: Lógica de negocio, operaciones CRUD

### Tests de API

Prueban endpoints HTTP:
- **Autenticación**: Login, registro, tokens
- **CRUD operations**: Crear, leer, actualizar, eliminar
- **Autorización**: Permisos de usuario/admin
- **Validación**: Datos de entrada incorrectos

### Tests de Integración

Prueban flujos completos:
- **Workflow de usuario**: Registro → Login → Operaciones
- **Gestión de productos**: Crear categoría → Crear producto → Búsqueda
- **Manejo de errores**: Escenarios de error realistas

## 🎯 Mejores Prácticas

### Nomenclatura

```python
def test_should_create_user_when_valid_data_provided():
    """Test que un usuario se crea correctamente con datos válidos"""
    pass

def test_should_raise_400_when_duplicate_email():
    """Test que se lanza error 400 con email duplicado"""
    pass
```

### Estructura de Tests

Sigue el patrón **AAA (Arrange, Act, Assert)**:

```python
def test_create_user(self, db_session: Session):
    # Arrange - Preparar datos
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    
    # Act - Ejecutar acción
    user_service = UserService(db_session)
    user = user_service.create(user_data)
    
    # Assert - Verificar resultado
    assert user.email == "test@example.com"
    assert user.id is not None
```

### Marcadores de Tests

Usa marcadores para categorizar tests:

```python
@pytest.mark.unit
def test_user_model():
    pass

@pytest.mark.integration  
def test_complete_workflow():
    pass

@pytest.mark.slow
def test_performance():
    pass
```

## 🐛 Debugging Tests

### Ejecutar un test específico

```bash
pytest tests/test_models/test_user.py::TestUserModel::test_create_user -v
```

### Ver output detallado

```bash
pytest tests/ -v -s  # -s para ver prints
```

### Parar en el primer error

```bash
pytest tests/ -x
```

### Modo debug con pdb

```python
def test_something():
    import pdb; pdb.set_trace()
    # resto del test
```

## 🔄 Integración Continua

Los tests están configurados para ejecutarse automáticamente en:
- **Pre-commit hooks**: Tests rápidos antes de commit
- **CI/CD pipeline**: Tests completos en pull requests
- **Deployment**: Tests de smoke en producción

## 📈 Métricas de Calidad

### Cobertura de Código
- **Objetivo**: >80% de cobertura
- **Crítico**: >95% para servicios de negocio
- **Líneas críticas**: 100% para funciones de seguridad

### Performance
- **Tests unitarios**: <1s por test
- **Tests de API**: <5s por test
- **Tests de integración**: <30s por test

## 🤝 Contribución

Al agregar nuevas funcionalidades:

1. **Escribe tests primero** (TDD)
2. **Mantén alta cobertura** (>80%)
3. **Sigue las convenciones** de nomenclatura
4. **Documenta casos edge** 
5. **Ejecuta todos los tests** antes de commit

```bash
# Antes de hacer commit
./run_tests.sh coverage
```

## 🔍 Troubleshooting

### Error de base de datos

```bash
# Limpiar archivos de test
./run_tests.sh clean
```

### Dependencias faltantes

```bash
# Reinstalar dependencias
./run_tests.sh install
```

### Tests lentos

```bash
# Ejecutar solo tests rápidos
pytest tests/ -m "not slow"
```

### Problemas de permisos

```bash
# Dar permisos al script
chmod +x run_tests.sh
```

---

Para más información sobre testing en FastAPI, consulta la [documentación oficial](https://fastapi.tiangolo.com/tutorial/testing/).
