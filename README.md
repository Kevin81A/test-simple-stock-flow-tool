# Simple Stock Flow · Herramienta de Demostración y Sembrado (CLI)

> **Prueba técnica SDD · Ficha ADSO 3413974**  
> Utilidad de línea de comandos en Python para sembrado de datos de prueba sobre la API pública (Tarea T-24).

---

## 1. ¿Qué es este repositorio y qué rol cumple en Simple Stock Flow?

Este repositorio contiene la **herramienta de sembrado y utilidades** (`ssf_tool`) de *Simple Stock Flow*.
Cumple el rol de automatizar la carga de datos de demostración (categorías, productos, imágenes reales y transacciones de venta) para que evaluadores y desarrolladores puedan ver el sistema operando con datos realistas de inmediato.

**Invariantes de diseño (Tarea T-24):**
- **Cero acceso a Base de Datos:** No incluye dependencias como `sqlalchemy` ni `pymysql`. No ejecuta DDL ni SQL directo.
- **Uso exclusivo de la API pública:** Toda la información se crea mediante los endpoints REST (`/api/auth/login`, `/api/products`, `/api/products/{id}/image`, `/api/sales`).
- **Idempotencia:** Si se ejecuta múltiples veces consecutivas, detecta los productos ya existentes y no genera duplicados ni errores.

---

## 2. ¿Cómo se ejecuta localmente?

### Con Docker (Recomendado si no tiene Python local)
```bash
# 1. Construir la imagen del sembrador
docker build -t ssf-tool .

# 2. Ejecutar el sembrado contra el stack levantado
docker run --rm --network host -e API_BASE_URL="http://localhost:8000" ssf-tool seed
```

### Sin Docker (Con Python 3.10+ y entorno virtual)
```bash
# 1. Crear y activar entorno virtual
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el comando seed
python -m ssf_tool seed --url http://localhost:8000 --username admin --password "Admin12345!"
```

---

## 3. Variables de entorno requeridas

El comando `seed` lee los siguientes valores de configuración (con valores por defecto si no se especifican):

| Variable | Descripción | Valor por Defecto |
|---|---|---|
| `API_BASE_URL` | URL base del servicio backend | `http://localhost:8000` |
| `ADMIN_USERNAME` | Usuario administrador para autenticación | `admin` |
| `ADMIN_PASSWORD` | Contraseña del administrador | `Admin12345!` |

---

## 4. ¿Cómo se ejecutan las pruebas?

```bash
# Ejecutar las pruebas unitarias con mock de red
python -m unittest discover tests/
```

---

## 5. Decisiones técnicas relevantes tomadas durante la implementación

1. **Aislamiento Estricto de Infraestructura (ADR-001):**
   - El sembrador vive fuera de `test-simple-stock-flow-infra` para que la infraestructura se mantenga 100% contenida y no exija la instalación previa de Python en el host evaluador.
2. **Sembrado Idempotente Basado en Consulta de Catálogo:**
   - Antes de enviar un `POST /api/products`, el cliente consulta el catálogo actual mediante `GET /api/products`. Si el producto ya existe por nombre, reutiliza su identificador único para asociar ventas, evitando colisiones de clave única o errores de duplicidad.
3. **Manejo Multipart Real para Imágenes:**
   - La herramienta genera y sube imágenes binarias reales (JPEG y PNG) a través de `multipart/form-data` respetando el límite de 5 MB y tipos MIME permitidos por la API.
