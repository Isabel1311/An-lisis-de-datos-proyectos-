# 🏗️ Sistema Integral de Control Documental 2025

**SERVMAC — División Conservación BBVA Noreste**

Dashboard interactivo para el control y análisis del sistema integral de documentos, órdenes de compra, contratos, obra menor, facturación, prefacturas y fianzas.

## 📊 Módulos

| Módulo | Descripción |
|--------|-------------|
| 🏠 Dashboard General | KPIs principales, gráficos resumen, panorama general |
| 📋 Órdenes de Compra | 973+ registros con filtros por estado, tipo, fecha |
| 📑 Contratos One Team | Control de contratos con estatus operativo y cierres |
| 🔧 Obra Menor | Proyectos de obra menor con variación presupuestal |
| 💰 Facturación 2025 | Control de facturación con análisis mensual |
| 📄 Control de Prefacturas | Seguimiento de prefacturas y emisión |
| 🛡️ Control de Fianzas | Monitoreo de fianzas, vencimientos y afianzadoras |
| 📊 Facturas Adquira | Facturas de la plataforma Adquira |
| 📁 Proyectos 2024 | Proyectos rezagados del año anterior |
| 🔍 Explorador de Datos | Exploración libre de cualquier hoja con búsqueda |

## 🚀 Despliegue en Streamlit Cloud

### Paso 1: Sube a GitHub

```bash
# Crear repositorio en GitHub y subir archivos
git init
git add .
git commit -m "Initial commit - Sistema Control Documental 2025"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/sistema-control-documental.git
git push -u origin main
```

### Paso 2: Despliega en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona el repositorio `sistema-control-documental`
4. Main file: `app.py`
5. Haz clic en **Deploy**

### Paso 3: Sube el archivo Excel

Una vez desplegada, usa el botón **📁 Cargar archivo Excel** en la barra lateral para subir tu archivo `SISTEMA_INTEGRAL_DE_CONTROL_DOCUMENTAL_2025.xlsx`.

> **Nota**: Si deseas que el archivo se cargue automáticamente, colócalo en la raíz del repositorio con el nombre exacto `SISTEMA_INTEGRAL_DE_CONTROL_DOCUMENTAL_2025.xlsx` (no recomendado para archivos grandes o con datos sensibles).

## 💻 Ejecución Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Copiar el archivo Excel a la carpeta del proyecto
cp /ruta/al/archivo/SISTEMA_INTEGRAL_DE_CONTROL_DOCUMENTAL_2025.xlsx .

# Ejecutar
streamlit run app.py
```

## 📁 Estructura del Repositorio

```
sistema-control-documental/
├── .streamlit/
│   └── config.toml          # Tema BBVA azul
├── app.py                    # Aplicación principal
├── requirements.txt          # Dependencias Python
└── README.md                 # Este archivo
```

## 🎨 Tecnologías

- **Streamlit** — Framework de dashboards
- **Pandas** — Procesamiento de datos
- **Plotly** — Gráficos interactivos
- **OpenPyXL** — Lectura de archivos Excel

---
*SERVMAC — Conservación BBVA Noreste 2025*
