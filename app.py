import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

# ─── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sistema Integral de Control Documental 2025",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── ESTILOS CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main .block-container { padding: 1rem 2rem; max-width: 1400px; }
    
    .metric-card {
        background: linear-gradient(135deg, #004481 0%, #0066B3 100%);
        border-radius: 12px; padding: 1.2rem; color: white;
        box-shadow: 0 4px 15px rgba(0,68,129,0.2);
        text-align: center; margin-bottom: 0.5rem;
    }
    .metric-card h3 { font-size: 0.8rem; margin: 0; opacity: 0.85; font-weight: 400; }
    .metric-card h1 { font-size: 1.6rem; margin: 0.3rem 0 0 0; font-weight: 700; }
    
    .metric-card-green {
        background: linear-gradient(135deg, #0E6E3D 0%, #15A05A 100%);
        border-radius: 12px; padding: 1.2rem; color: white;
        box-shadow: 0 4px 15px rgba(14,110,61,0.2);
        text-align: center; margin-bottom: 0.5rem;
    }
    .metric-card-green h3 { font-size: 0.8rem; margin: 0; opacity: 0.85; font-weight: 400; }
    .metric-card-green h1 { font-size: 1.6rem; margin: 0.3rem 0 0 0; font-weight: 700; }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #D4721A 0%, #F5A623 100%);
        border-radius: 12px; padding: 1.2rem; color: white;
        box-shadow: 0 4px 15px rgba(212,114,26,0.2);
        text-align: center; margin-bottom: 0.5rem;
    }
    .metric-card-orange h3 { font-size: 0.8rem; margin: 0; opacity: 0.85; font-weight: 400; }
    .metric-card-orange h1 { font-size: 1.6rem; margin: 0.3rem 0 0 0; font-weight: 700; }
    
    .metric-card-red {
        background: linear-gradient(135deg, #C0392B 0%, #E74C3C 100%);
        border-radius: 12px; padding: 1.2rem; color: white;
        box-shadow: 0 4px 15px rgba(192,57,43,0.2);
        text-align: center; margin-bottom: 0.5rem;
    }
    .metric-card-red h3 { font-size: 0.8rem; margin: 0; opacity: 0.85; font-weight: 400; }
    .metric-card-red h1 { font-size: 1.6rem; margin: 0.3rem 0 0 0; font-weight: 700; }

    .section-header {
        background: linear-gradient(90deg, #004481, #0066B3);
        color: white; padding: 0.6rem 1.2rem; border-radius: 8px;
        margin: 1.5rem 0 1rem 0; font-size: 1.1rem; font-weight: 600;
    }
    
    div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0; padding: 8px 20px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# ─── FUNCIONES DE CARGA ────────────────────────────────────────────────────────
@st.cache_data
def load_data(file_path):
    """Carga todas las hojas relevantes del archivo Excel."""
    sheets = {}
    xls = pd.ExcelFile(file_path)
    
    # REGISTRO ORDEN DE COMPRA
    try:
        df = pd.read_excel(xls, 'REGISTRO ORDEN DE COMPRA', header=1)
        df.columns = df.columns.str.strip()
        for col in ['FECHA', 'FECHA DE PUBLICACIÓN']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        for col in ['IMPORTE TOTAL', 'IMPORTE SIN IVA', 'IMPORTE DE LA ORDEN [TOTAL IMPORTE CONTRATO] -SIN IVA', 
                     'IMPORTE CORRESPONDIENTE A CANTIDAD EXPEDIDA', 'IMPORTE DE CIERRE', 'BALANCE']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['ID. PEDIDO COMPRADOR'], how='all')
        sheets['ordenes'] = df
    except Exception as e:
        st.warning(f"Error cargando Órdenes de Compra: {e}")
    
    # CONTRATOS || ONE TEAM
    try:
        df = pd.read_excel(xls, 'CONTRATOS || ONE TEAM', header=1)
        df.columns = df.columns.str.strip()
        for col in ['Fecha de asignación proyecto', 'Fecha inicio vigencia anexo', 'Fecha de Recepción',
                     'Fecha Firma Interna', 'Fecha de detonación', 'Fecha de cierre operación (Acta final)', 'Fecha envío cierre']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        for col in ['Importe Acción', 'Importe Certificación', 'Importe Total', 'Importe Cierre Administrativo',
                     'Total Pagado', 'Por pagar', 'Por devolver']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['ID Folio Contrato'], how='all')
        sheets['contratos'] = df
    except Exception as e:
        st.warning(f"Error cargando Contratos: {e}")
    
    # OBRA MENOR
    try:
        df = pd.read_excel(xls, 'OBRA MENOR', header=1)
        df.columns = df.columns.str.strip()
        for col in ['FECHA_DE_ASIGNACIÓN', 'FECHA INICIO', 'FECHA FIN', 'FECHA FIN REAL', 
                     'FECHA CORREO DETONACIÓN', 'FECHA CIERRE ADMINISTRATIVO']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        for col in ['PRESUPUESTO_INICIAL', 'IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL', 'Importe UDA',
                     'Total Pagado', 'VARIACIÓN_PRESUPUESTAL']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['ID_PROYECTO'], how='all')
        sheets['obra_menor'] = df
    except Exception as e:
        st.warning(f"Error cargando Obra Menor: {e}")
    
    # Facturación 2025
    try:
        df = pd.read_excel(xls, 'Facturación 2025', header=0)
        df.columns = df.columns.str.strip()
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        for col in ['Subtotal (MXN)', 'Impuestos (MXN)', 'Total (MXN)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['NO.'], how='all')
        sheets['facturacion_2025'] = df
    except Exception as e:
        st.warning(f"Error cargando Facturación 2025: {e}")
    
    # CONTROL DE PREFACTURAS
    try:
        df = pd.read_excel(xls, 'CONTROL DE PREFACTURAS', header=1)
        df.columns = df.columns.str.strip()
        for col in ['Fecha solicitud', 'Fecha Emisión', 'Fecha de aceptación', 'Fecha de factura']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        for col in ['Monto (sin IVA)', 'IVA', 'Total']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['Folio Interno'], how='all')
        sheets['prefacturas'] = df
    except Exception as e:
        st.warning(f"Error cargando Prefacturas: {e}")
    
    # CONTROL DE FIANZAS
    try:
        df = pd.read_excel(xls, 'CONTROL DE FIANZAS', header=1)
        df.columns = df.columns.str.strip()
        for col in ['Fecha Solicitud Fianza', 'Fecha Emisión', 'Vencimiento']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        for col in ['Monto de contrato', 'Monto + IVA', 'Importe a afianzar || Cumplimiento',
                     'Importe a afianzar || Buena calidad', 'Monto Garantizado Fianza']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['CR'], how='all')
        sheets['fianzas'] = df
    except Exception as e:
        st.warning(f"Error cargando Fianzas: {e}")
    
    # FACTURACIÓN (Adquira)
    try:
        df = pd.read_excel(xls, 'FACTURACIÓN', header=0)
        df.columns = df.columns.str.strip()
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        for col in ['Subtotal (MXN)', 'Impuestos (MXN)', 'Total (MXN)']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['NO.'], how='all')
        sheets['facturacion_adquira'] = df
    except Exception as e:
        st.warning(f"Error cargando Facturación Adquira: {e}")
    
    # Copia de Facturas Adquira
    try:
        df = pd.read_excel(xls, 'Copia de Facturas Adquira', header=0)
        df.columns = df.columns.str.strip()
        for col in ['BASE IMPONIBLE', 'TOTAL IMPUESTOS', 'TOTAL FACTURA']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['NÚMERO'], how='all')
        sheets['facturas_adquira'] = df
    except Exception as e:
        st.warning(f"Error cargando Copia Facturas Adquira: {e}")
    
    # Proyectos 2024
    try:
        df = pd.read_excel(xls, 'Proyectos 2024', header=1)
        df.columns = df.columns.str.strip()
        for col in ['Importe de cierre', 'Total Pagado', 'Por pagar', 'Por devolver', 'Importe CFE']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['Llave comité /Clave UDA'], how='all')
        sheets['proyectos_2024'] = df
    except Exception as e:
        st.warning(f"Error cargando Proyectos 2024: {e}")
    
    return sheets

def fmt_money(val):
    """Formatea un valor numérico como moneda MXN."""
    if pd.isna(val) or val is None:
        return "$0.00"
    return f"${val:,.2f}"

def metric_card(title, value, style="metric-card"):
    return f'<div class="{style}"><h3>{title}</h3><h1>{value}</h1></div>'


# ─── CARGA DE DATOS ────────────────────────────────────────────────────────────
DATA_PATH = "SISTEMA_INTEGRAL_DE_CONTROL_DOCUMENTAL_2025.xlsx"

# Buscar archivo
if not os.path.exists(DATA_PATH):
    possible_paths = [
        "/mnt/user-data/uploads/SISTEMA_INTEGRAL_DE_CONTROL_DOCUMENTAL_2025.xlsx",
        "data/SISTEMA_INTEGRAL_DE_CONTROL_DOCUMENTAL_2025.xlsx"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            DATA_PATH = p
            break

uploaded_file = st.sidebar.file_uploader("📁 Cargar archivo Excel", type=['xlsx', 'xls'])

if uploaded_file:
    DATA_PATH = uploaded_file

if not os.path.exists(DATA_PATH) if isinstance(DATA_PATH, str) else False:
    if not uploaded_file:
        st.warning("⚠️ No se encontró el archivo de datos. Por favor sube el archivo Excel.")
        st.stop()

try:
    sheets = load_data(DATA_PATH)
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.stop()


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏗️ SERVMAC")
st.sidebar.markdown("**Sistema Integral de Control Documental**")
st.sidebar.markdown("*BBVA Conservación Noreste 2025*")

modulo = st.sidebar.radio(
    "📊 Módulo",
    ["🏠 Dashboard General", 
     "📋 Órdenes de Compra",
     "📑 Contratos One Team", 
     "🔧 Obra Menor",
     "💰 Facturación 2025",
     "📄 Control de Prefacturas",
     "🛡️ Control de Fianzas",
     "📊 Facturas Adquira",
     "📁 Proyectos 2024",
     "🔍 Explorador de Datos"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.caption(f"📅 Datos actualizados: {datetime.now().strftime('%d/%m/%Y')}")


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: DASHBOARD GENERAL
# ═══════════════════════════════════════════════════════════════════════════════
if modulo == "🏠 Dashboard General":
    st.markdown("## 🏗️ Sistema Integral de Control Documental 2025")
    st.markdown("**SERVMAC — División Conservación BBVA Noreste**")
    st.markdown("---")
    
    # ── KPIs principales ──
    col1, col2, col3, col4 = st.columns(4)
    
    n_ordenes = len(sheets.get('ordenes', pd.DataFrame()))
    n_contratos = len(sheets.get('contratos', pd.DataFrame()))
    n_obra_menor = len(sheets.get('obra_menor', pd.DataFrame()))
    n_prefacturas = len(sheets.get('prefacturas', pd.DataFrame()))
    
    with col1:
        st.markdown(metric_card("ÓRDENES DE COMPRA", f"{n_ordenes:,}"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("CONTRATOS ONE TEAM", f"{n_contratos:,}", "metric-card-green"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("PROYECTOS OBRA MENOR", f"{n_obra_menor:,}", "metric-card-orange"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("PREFACTURAS", f"{n_prefacturas:,}", "metric-card-red"), unsafe_allow_html=True)
    
    st.markdown("")
    
    # ── Montos totales ──
    col1, col2, col3 = st.columns(3)
    
    total_ordenes = sheets.get('ordenes', pd.DataFrame()).get('IMPORTE TOTAL', pd.Series(dtype=float)).sum()
    total_contratos = sheets.get('contratos', pd.DataFrame()).get('Importe Total', pd.Series(dtype=float)).sum()
    total_facturacion = sheets.get('facturacion_2025', pd.DataFrame()).get('Total (MXN)', pd.Series(dtype=float)).sum()
    
    with col1:
        st.markdown(metric_card("TOTAL ÓRDENES DE COMPRA", fmt_money(total_ordenes)), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("TOTAL CONTRATOS", fmt_money(total_contratos), "metric-card-green"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("TOTAL FACTURADO 2025", fmt_money(total_facturacion), "metric-card-orange"), unsafe_allow_html=True)
    
    st.markdown("")
    
    # ── Gráficos resumen ──
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="section-header">📊 Órdenes por Estado</div>', unsafe_allow_html=True)
        if 'ordenes' in sheets and 'ESTADO' in sheets['ordenes'].columns:
            df_estado = sheets['ordenes']['ESTADO'].value_counts().reset_index()
            df_estado.columns = ['Estado', 'Cantidad']
            fig = px.pie(df_estado, values='Cantidad', names='Estado', 
                        color_discrete_sequence=px.colors.qualitative.Set2,
                        hole=0.4)
            fig.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20),
                            font=dict(size=12))
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.markdown('<div class="section-header">📈 Facturación Mensual 2025</div>', unsafe_allow_html=True)
        if 'facturacion_2025' in sheets and 'Fecha' in sheets['facturacion_2025'].columns:
            df_fact = sheets['facturacion_2025'].copy()
            df_fact = df_fact.dropna(subset=['Fecha'])
            df_fact['Mes'] = df_fact['Fecha'].dt.to_period('M').astype(str)
            df_mensual = df_fact.groupby('Mes')['Total (MXN)'].sum().reset_index()
            fig = px.bar(df_mensual, x='Mes', y='Total (MXN)',
                        color_discrete_sequence=['#004481'])
            fig.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20),
                            xaxis_title="Mes", yaxis_title="Total (MXN)",
                            font=dict(size=12))
            fig.update_yaxes(tickformat="$,.0f")
            st.plotly_chart(fig, use_container_width=True)
    
    # ── Obra Menor - Estatus ──
    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        st.markdown('<div class="section-header">🔧 Obra Menor — Estatus Operación</div>', unsafe_allow_html=True)
        if 'obra_menor' in sheets:
            status_col = None
            for c in ['ESTATUS_OPERACIÓN REAL', 'ESTATUS OPERACIÓN ESTIMADO']:
                if c in sheets['obra_menor'].columns:
                    status_col = c
                    break
            if status_col:
                df_st = sheets['obra_menor'][status_col].value_counts().reset_index()
                df_st.columns = ['Estatus', 'Cantidad']
                fig = px.bar(df_st.head(10), x='Cantidad', y='Estatus', orientation='h',
                            color_discrete_sequence=['#0E6E3D'])
                fig.update_layout(height=350, margin=dict(t=20, b=40, l=20, r=20),
                                font=dict(size=11))
                st.plotly_chart(fig, use_container_width=True)
    
    with col_right2:
        st.markdown('<div class="section-header">📑 Contratos — Estatus Operativo</div>', unsafe_allow_html=True)
        if 'contratos' in sheets and 'Estatus Operativo' in sheets['contratos'].columns:
            df_co = sheets['contratos']['Estatus Operativo'].value_counts().reset_index()
            df_co.columns = ['Estatus', 'Cantidad']
            fig = px.bar(df_co.head(10), x='Cantidad', y='Estatus', orientation='h',
                        color_discrete_sequence=['#D4721A'])
            fig.update_layout(height=350, margin=dict(t=20, b=40, l=20, r=20),
                            font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
    
    # ── Proyectos por tipo ──
    st.markdown('<div class="section-header">🏢 Distribución por Tipo de Proyecto</div>', unsafe_allow_html=True)
    if 'ordenes' in sheets and 'TIPO DE PROYECTO' in sheets['ordenes'].columns:
        df_tipo = sheets['ordenes'].groupby('TIPO DE PROYECTO').agg(
            Cantidad=('TIPO DE PROYECTO', 'count'),
            Importe_Total=('IMPORTE TOTAL', 'sum')
        ).reset_index().sort_values('Importe_Total', ascending=False)
        
        fig = make_subplots(rows=1, cols=2, specs=[[{"type": "bar"}, {"type": "pie"}]],
                           subplot_titles=("Importe por Tipo", "Distribución de Cantidad"))
        fig.add_trace(go.Bar(x=df_tipo['TIPO DE PROYECTO'], y=df_tipo['Importe_Total'],
                            marker_color='#004481', name='Importe'), row=1, col=1)
        fig.add_trace(go.Pie(labels=df_tipo['TIPO DE PROYECTO'], values=df_tipo['Cantidad'],
                            hole=0.4, name='Cantidad'), row=1, col=2)
        fig.update_layout(height=400, margin=dict(t=40, b=20), showlegend=False,
                         font=dict(size=11))
        fig.update_yaxes(tickformat="$,.0f", row=1, col=1)
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: ÓRDENES DE COMPRA
# ═══════════════════════════════════════════════════════════════════════════════
elif modulo == "📋 Órdenes de Compra":
    st.markdown("## 📋 Registro de Órdenes de Compra")
    
    if 'ordenes' not in sheets:
        st.error("No se encontraron datos de Órdenes de Compra")
        st.stop()
    
    df = sheets['ordenes'].copy()
    
    # Filtros
    st.markdown('<div class="section-header">🔎 Filtros</div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    
    with fc1:
        estados = ['Todos'] + sorted(df['ESTADO'].dropna().unique().tolist()) if 'ESTADO' in df.columns else ['Todos']
        sel_estado = st.selectbox("Estado", estados)
    with fc2:
        tipos = ['Todos'] + sorted(df['TIPO DE PROYECTO'].dropna().unique().tolist()) if 'TIPO DE PROYECTO' in df.columns else ['Todos']
        sel_tipo = st.selectbox("Tipo de Proyecto", tipos)
    with fc3:
        if 'FECHA' in df.columns:
            min_date = df['FECHA'].min()
            max_date = df['FECHA'].max()
            if pd.notna(min_date) and pd.notna(max_date):
                date_range = st.date_input("Rango de fechas", value=(min_date, max_date), 
                                          min_value=min_date, max_value=max_date)
    
    if sel_estado != 'Todos' and 'ESTADO' in df.columns:
        df = df[df['ESTADO'] == sel_estado]
    if sel_tipo != 'Todos' and 'TIPO DE PROYECTO' in df.columns:
        df = df[df['TIPO DE PROYECTO'] == sel_tipo]
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("TOTAL REGISTROS", f"{len(df):,}"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("IMPORTE TOTAL", fmt_money(df['IMPORTE TOTAL'].sum()) if 'IMPORTE TOTAL' in df.columns else "$0", "metric-card-green"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("IMPORTE SIN IVA", fmt_money(df['IMPORTE SIN IVA'].sum()) if 'IMPORTE SIN IVA' in df.columns else "$0", "metric-card-orange"), unsafe_allow_html=True)
    with col4:
        total_cierre = df['IMPORTE DE CIERRE'].sum() if 'IMPORTE DE CIERRE' in df.columns else 0
        st.markdown(metric_card("IMPORTE CIERRES", fmt_money(total_cierre), "metric-card-red"), unsafe_allow_html=True)
    
    # Gráficos
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">📊 Top 15 Proyectos por Importe</div>', unsafe_allow_html=True)
        if 'NOMBRE DEL PROYECTO O SUCURSAL' in df.columns:
            top = df.groupby('NOMBRE DEL PROYECTO O SUCURSAL')['IMPORTE TOTAL'].sum().nlargest(15).reset_index()
            fig = px.bar(top, x='IMPORTE TOTAL', y='NOMBRE DEL PROYECTO O SUCURSAL', orientation='h',
                        color_discrete_sequence=['#004481'])
            fig.update_layout(height=500, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(autorange="reversed"),
                            font=dict(size=10))
            fig.update_xaxes(tickformat="$,.0f")
            st.plotly_chart(fig, use_container_width=True)
    
    with col_r:
        st.markdown('<div class="section-header">📈 Órdenes por Mes</div>', unsafe_allow_html=True)
        if 'FECHA' in df.columns:
            df_temp = df.dropna(subset=['FECHA'])
            df_temp['Mes'] = df_temp['FECHA'].dt.to_period('M').astype(str)
            monthly = df_temp.groupby('Mes').agg(
                Cantidad=('Mes', 'count'),
                Importe=('IMPORTE TOTAL', 'sum')
            ).reset_index()
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=monthly['Mes'], y=monthly['Importe'], name='Importe', marker_color='#004481'), secondary_y=False)
            fig.add_trace(go.Scatter(x=monthly['Mes'], y=monthly['Cantidad'], name='Cantidad', 
                                    line=dict(color='#E74C3C', width=3), mode='lines+markers'), secondary_y=True)
            fig.update_layout(height=500, margin=dict(t=20, b=20), font=dict(size=11))
            fig.update_yaxes(tickformat="$,.0f", secondary_y=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla
    st.markdown('<div class="section-header">📋 Detalle de Órdenes</div>', unsafe_allow_html=True)
    display_cols = [c for c in ['ID. PEDIDO COMPRADOR', 'FECHA', 'IMPORTE TOTAL', 'ESTADO', 'ORDEN',
                                'NOMBRE DEL PROYECTO O SUCURSAL', 'TIPO DE PROYECTO', 'IMPORTE DE CIERRE', 'ESTATUS'] 
                   if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: CONTRATOS ONE TEAM
# ═══════════════════════════════════════════════════════════════════════════════
elif modulo == "📑 Contratos One Team":
    st.markdown("## 📑 Contratos || One Team")
    
    if 'contratos' not in sheets:
        st.error("No se encontraron datos de Contratos")
        st.stop()
    
    df = sheets['contratos'].copy()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("TOTAL CONTRATOS", f"{len(df):,}"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("IMPORTE TOTAL", fmt_money(df['Importe Total'].sum()) if 'Importe Total' in df.columns else "$0", "metric-card-green"), unsafe_allow_html=True)
    with col3:
        total_pagado = df['Total Pagado'].sum() if 'Total Pagado' in df.columns else 0
        st.markdown(metric_card("TOTAL PAGADO", fmt_money(total_pagado), "metric-card-orange"), unsafe_allow_html=True)
    with col4:
        por_pagar = df['Por pagar'].sum() if 'Por pagar' in df.columns else 0
        st.markdown(metric_card("POR PAGAR", fmt_money(por_pagar), "metric-card-red"), unsafe_allow_html=True)
    
    # Filtros
    fc1, fc2 = st.columns(2)
    with fc1:
        if 'Estatus Operativo' in df.columns:
            ops = ['Todos'] + sorted(df['Estatus Operativo'].dropna().unique().tolist())
            sel_op = st.selectbox("Estatus Operativo", ops)
            if sel_op != 'Todos':
                df = df[df['Estatus Operativo'] == sel_op]
    with fc2:
        if 'Estatus Cierre' in df.columns:
            cierres = ['Todos'] + sorted(df['Estatus Cierre'].dropna().unique().tolist())
            sel_cierre = st.selectbox("Estatus Cierre", cierres)
            if sel_cierre != 'Todos':
                df = df[df['Estatus Cierre'] == sel_cierre]
    
    # Gráficos
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown('<div class="section-header">💰 Top 15 Contratos por Importe</div>', unsafe_allow_html=True)
        if 'Proyecto / Obra' in df.columns and 'Importe Total' in df.columns:
            top_c = df.nlargest(15, 'Importe Total')[['Proyecto / Obra', 'Importe Total', 'CR']].dropna()
            fig = px.bar(top_c, x='Importe Total', y='Proyecto / Obra', orientation='h',
                        color_discrete_sequence=['#0E6E3D'],
                        hover_data=['CR'])
            fig.update_layout(height=500, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(autorange="reversed"),
                            font=dict(size=10))
            fig.update_xaxes(tickformat="$,.0f")
            st.plotly_chart(fig, use_container_width=True)
    
    with col_r:
        st.markdown('<div class="section-header">📊 Estatus Operativo</div>', unsafe_allow_html=True)
        if 'Estatus Operativo' in df.columns:
            df_eo = df['Estatus Operativo'].value_counts().reset_index()
            df_eo.columns = ['Estatus', 'Cantidad']
            fig = px.pie(df_eo, values='Cantidad', names='Estatus', hole=0.45,
                        color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=500, margin=dict(t=20, b=20), font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
    
    # Análisis Pagado vs Por Pagar
    st.markdown('<div class="section-header">💵 Análisis Pagado vs Por Pagar por Proyecto</div>', unsafe_allow_html=True)
    if all(c in df.columns for c in ['Proyecto / Obra', 'Total Pagado', 'Por pagar']):
        df_pay = df[['Proyecto / Obra', 'Total Pagado', 'Por pagar']].dropna()
        df_pay = df_pay.groupby('Proyecto / Obra').sum().reset_index()
        df_pay = df_pay.nlargest(20, 'Total Pagado')
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_pay['Proyecto / Obra'], y=df_pay['Total Pagado'], name='Pagado', marker_color='#0E6E3D'))
        fig.add_trace(go.Bar(x=df_pay['Proyecto / Obra'], y=df_pay['Por pagar'], name='Por Pagar', marker_color='#E74C3C'))
        fig.update_layout(barmode='stack', height=450, margin=dict(t=20, b=20), font=dict(size=10),
                         xaxis_tickangle=-45)
        fig.update_yaxes(tickformat="$,.0f")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla
    st.markdown('<div class="section-header">📋 Detalle de Contratos</div>', unsafe_allow_html=True)
    display_cols = [c for c in ['ID Folio Contrato', 'CR', 'Proyecto / Obra', 'Importe Total', 
                                'Estatus Operativo', 'Estatus Cierre', 'Total Pagado', 'Por pagar',
                                'Supervisor asignado para coordinación / revisión'] 
                   if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: OBRA MENOR
# ═══════════════════════════════════════════════════════════════════════════════
elif modulo == "🔧 Obra Menor":
    st.markdown("## 🔧 Obra Menor")
    
    if 'obra_menor' not in sheets:
        st.error("No se encontraron datos de Obra Menor")
        st.stop()
    
    df = sheets['obra_menor'].copy()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("TOTAL PROYECTOS", f"{len(df):,}"), unsafe_allow_html=True)
    with col2:
        presupuesto = df['PRESUPUESTO_INICIAL'].sum() if 'PRESUPUESTO_INICIAL' in df.columns else 0
        st.markdown(metric_card("PRESUPUESTO INICIAL", fmt_money(presupuesto), "metric-card-green"), unsafe_allow_html=True)
    with col3:
        cierre = df['IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL'].sum() if 'IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL' in df.columns else 0
        st.markdown(metric_card("IMPORTE CIERRE", fmt_money(cierre), "metric-card-orange"), unsafe_allow_html=True)
    with col4:
        pagado = df['Total Pagado'].sum() if 'Total Pagado' in df.columns else 0
        st.markdown(metric_card("TOTAL PAGADO", fmt_money(pagado), "metric-card-red"), unsafe_allow_html=True)
    
    # Filtros
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        if 'PROYECTO' in df.columns:
            proyectos = ['Todos'] + sorted(df['PROYECTO'].dropna().unique().tolist())
            sel_proy = st.selectbox("Proyecto", proyectos)
            if sel_proy != 'Todos':
                df = df[df['PROYECTO'] == sel_proy]
    with fc2:
        status_col = 'ESTATUS_OPERACIÓN REAL' if 'ESTATUS_OPERACIÓN REAL' in df.columns else None
        if status_col:
            estatus_ops = ['Todos'] + sorted(df[status_col].dropna().unique().tolist())
            sel_est = st.selectbox("Estatus Operación", estatus_ops)
            if sel_est != 'Todos':
                df = df[df[status_col] == sel_est]
    with fc3:
        if 'ASIGNADO_A' in df.columns:
            asignados = ['Todos'] + sorted(df['ASIGNADO_A'].dropna().unique().tolist())
            sel_asig = st.selectbox("Asignado a", asignados)
            if sel_asig != 'Todos':
                df = df[df['ASIGNADO_A'] == sel_asig]
    
    # Gráficos
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown('<div class="section-header">📊 Proyectos por Tipo</div>', unsafe_allow_html=True)
        if 'PROYECTO' in df.columns:
            df_proy = df['PROYECTO'].value_counts().reset_index()
            df_proy.columns = ['Proyecto', 'Cantidad']
            fig = px.pie(df_proy, values='Cantidad', names='Proyecto', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(height=400, margin=dict(t=20, b=20), font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
    
    with col_r:
        st.markdown('<div class="section-header">👤 Asignación por Persona</div>', unsafe_allow_html=True)
        if 'ASIGNADO_A' in df.columns:
            df_asig = df['ASIGNADO_A'].value_counts().head(15).reset_index()
            df_asig.columns = ['Asignado', 'Cantidad']
            fig = px.bar(df_asig, x='Cantidad', y='Asignado', orientation='h',
                        color_discrete_sequence=['#D4721A'])
            fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20),
                            yaxis=dict(autorange="reversed"), font=dict(size=10))
            st.plotly_chart(fig, use_container_width=True)
    
    # Variación presupuestal
    st.markdown('<div class="section-header">📈 Variación Presupuestal (Presupuesto vs Cierre)</div>', unsafe_allow_html=True)
    if all(c in df.columns for c in ['SUCURSAL', 'PRESUPUESTO_INICIAL', 'IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL']):
        df_var = df[['SUCURSAL', 'PRESUPUESTO_INICIAL', 'IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL']].dropna()
        df_var = df_var.nlargest(20, 'PRESUPUESTO_INICIAL')
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_var['SUCURSAL'], y=df_var['PRESUPUESTO_INICIAL'], 
                            name='Presupuesto Inicial', marker_color='#004481'))
        fig.add_trace(go.Bar(x=df_var['SUCURSAL'], y=df_var['IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL'], 
                            name='Importe Cierre', marker_color='#E74C3C'))
        fig.update_layout(barmode='group', height=450, margin=dict(t=20, b=20), font=dict(size=10),
                         xaxis_tickangle=-45)
        fig.update_yaxes(tickformat="$,.0f")
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla
    st.markdown('<div class="section-header">📋 Detalle Obra Menor</div>', unsafe_allow_html=True)
    display_cols = [c for c in ['ID_PROYECTO', 'SUCURSAL', 'PROYECTO', 'TRABAJO', 'ASIGNADO_A',
                                'ESTATUS_OPERACIÓN REAL', 'PRESUPUESTO_INICIAL', 
                                'IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL', 'Total Pagado'] 
                   if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: FACTURACIÓN 2025
# ═══════════════════════════════════════════════════════════════════════════════
elif modulo == "💰 Facturación 2025":
    st.markdown("## 💰 Facturación 2025")
    
    if 'facturacion_2025' not in sheets:
        st.error("No se encontraron datos de Facturación 2025")
        st.stop()
    
    df = sheets['facturacion_2025'].copy()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("TOTAL FACTURAS", f"{len(df):,}"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("SUBTOTAL", fmt_money(df['Subtotal (MXN)'].sum()), "metric-card-green"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("IMPUESTOS", fmt_money(df['Impuestos (MXN)'].sum()), "metric-card-orange"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("TOTAL FACTURADO", fmt_money(df['Total (MXN)'].sum()), "metric-card-red"), unsafe_allow_html=True)
    
    # Filtros
    fc1, fc2 = st.columns(2)
    with fc1:
        if 'Estatus Comprobante' in df.columns:
            estatus_list = ['Todos'] + sorted(df['Estatus Comprobante'].dropna().unique().tolist())
            sel_est = st.selectbox("Estatus Comprobante", estatus_list)
            if sel_est != 'Todos':
                df = df[df['Estatus Comprobante'] == sel_est]
    with fc2:
        if 'FDP' in df.columns:
            fdp_list = ['Todos'] + sorted(df['FDP'].dropna().unique().tolist())
            sel_fdp = st.selectbox("Forma de Pago", fdp_list)
            if sel_fdp != 'Todos':
                df = df[df['FDP'] == sel_fdp]
    
    # Gráficos
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">📈 Facturación Mensual</div>', unsafe_allow_html=True)
        if 'Fecha' in df.columns:
            df_m = df.dropna(subset=['Fecha']).copy()
            df_m['Mes'] = df_m['Fecha'].dt.to_period('M').astype(str)
            monthly = df_m.groupby('Mes').agg(Total=('Total (MXN)', 'sum'), Cantidad=('NO.', 'count')).reset_index()
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=monthly['Mes'], y=monthly['Total'], name='Total', marker_color='#004481'), secondary_y=False)
            fig.add_trace(go.Scatter(x=monthly['Mes'], y=monthly['Cantidad'], name='# Facturas', 
                                    line=dict(color='#E74C3C', width=3), mode='lines+markers'), secondary_y=True)
            fig.update_layout(height=400, margin=dict(t=20, b=20), font=dict(size=11))
            fig.update_yaxes(tickformat="$,.0f", secondary_y=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col_r:
        st.markdown('<div class="section-header">📊 Distribución por Estatus</div>', unsafe_allow_html=True)
        if 'Estatus Comprobante' in df.columns:
            df_ec = df['Estatus Comprobante'].value_counts().reset_index()
            df_ec.columns = ['Estatus', 'Cantidad']
            fig = px.pie(df_ec, values='Cantidad', names='Estatus', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=400, margin=dict(t=20, b=20), font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla
    st.markdown('<div class="section-header">📋 Detalle de Facturas</div>', unsafe_allow_html=True)
    display_cols = [c for c in ['FDP', 'Fecha', 'NO.', 'Razón social', 'Estatus Comprobante', 
                                'Subtotal (MXN)', 'Impuestos (MXN)', 'Total (MXN)', 'ORDEN DE COMPRA'] 
                   if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: CONTROL DE PREFACTURAS
# ═══════════════════════════════════════════════════════════════════════════════
elif modulo == "📄 Control de Prefacturas":
    st.markdown("## 📄 Control de Prefacturas")
    
    if 'prefacturas' not in sheets:
        st.error("No se encontraron datos de Prefacturas")
        st.stop()
    
    df = sheets['prefacturas'].copy()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("TOTAL PREFACTURAS", f"{len(df):,}"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("MONTO SIN IVA", fmt_money(df['Monto (sin IVA)'].sum()), "metric-card-green"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("IVA TOTAL", fmt_money(df['IVA'].sum()), "metric-card-orange"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("TOTAL", fmt_money(df['Total'].sum()), "metric-card-red"), unsafe_allow_html=True)
    
    # Filtro
    if 'Estatus' in df.columns:
        estatus = ['Todos'] + sorted(df['Estatus'].dropna().unique().tolist())
        sel = st.selectbox("Estatus", estatus)
        if sel != 'Todos':
            df = df[df['Estatus'] == sel]
    
    # Gráficos
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">💰 Top Prefacturas por Monto</div>', unsafe_allow_html=True)
        top_pf = df.nlargest(15, 'Total')[['Proyecto / Obra', 'Total', 'CR']].dropna() if 'Proyecto / Obra' in df.columns else pd.DataFrame()
        if not top_pf.empty:
            fig = px.bar(top_pf, x='Total', y='Proyecto / Obra', orientation='h',
                        color_discrete_sequence=['#004481'], hover_data=['CR'])
            fig.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(autorange="reversed"),
                            font=dict(size=10))
            fig.update_xaxes(tickformat="$,.0f")
            st.plotly_chart(fig, use_container_width=True)
    
    with col_r:
        st.markdown('<div class="section-header">📊 Estatus de Prefacturas</div>', unsafe_allow_html=True)
        if 'Estatus' in df.columns:
            df_est = df['Estatus'].value_counts().reset_index()
            df_est.columns = ['Estatus', 'Cantidad']
            fig = px.pie(df_est, values='Cantidad', names='Estatus', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(height=450, margin=dict(t=20, b=20), font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla
    st.markdown('<div class="section-header">📋 Detalle de Prefacturas</div>', unsafe_allow_html=True)
    display_cols = [c for c in ['Folio Interno', 'Folio Pre Factura', 'CR', 'Proyecto / Obra',
                                'Fecha solicitud', 'Monto (sin IVA)', 'Total', 'Estatus', 
                                '¿Se emitió factura?', 'Folio factura'] 
                   if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: CONTROL DE FIANZAS
# ═══════════════════════════════════════════════════════════════════════════════
elif modulo == "🛡️ Control de Fianzas":
    st.markdown("## 🛡️ Control de Fianzas")
    
    if 'fianzas' not in sheets:
        st.error("No se encontraron datos de Fianzas")
        st.stop()
    
    df = sheets['fianzas'].copy()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("TOTAL FIANZAS", f"{len(df):,}"), unsafe_allow_html=True)
    with col2:
        monto_contrato = df['Monto de contrato'].sum() if 'Monto de contrato' in df.columns else 0
        st.markdown(metric_card("MONTO CONTRATOS", fmt_money(monto_contrato), "metric-card-green"), unsafe_allow_html=True)
    with col3:
        monto_garantizado = df['Monto Garantizado Fianza'].sum() if 'Monto Garantizado Fianza' in df.columns else 0
        st.markdown(metric_card("MONTO GARANTIZADO", fmt_money(monto_garantizado), "metric-card-orange"), unsafe_allow_html=True)
    with col4:
        if 'Estatus Vigencia' in df.columns:
            vencidas = len(df[df['Estatus Vigencia'].astype(str).str.contains('Vencid|vencid', na=False)])
            st.markdown(metric_card("FIANZAS VENCIDAS", f"{vencidas}", "metric-card-red"), unsafe_allow_html=True)
        else:
            st.markdown(metric_card("REGISTROS", f"{len(df)}", "metric-card-red"), unsafe_allow_html=True)
    
    # Filtros
    fc1, fc2 = st.columns(2)
    with fc1:
        if 'Estatus Expedición' in df.columns:
            exp = ['Todos'] + sorted(df['Estatus Expedición'].dropna().unique().tolist())
            sel_exp = st.selectbox("Estatus Expedición", exp)
            if sel_exp != 'Todos':
                df = df[df['Estatus Expedición'] == sel_exp]
    with fc2:
        if 'Estatus Vigencia' in df.columns:
            vig = ['Todos'] + sorted(df['Estatus Vigencia'].dropna().unique().tolist())
            sel_vig = st.selectbox("Estatus Vigencia", vig)
            if sel_vig != 'Todos':
                df = df[df['Estatus Vigencia'] == sel_vig]
    
    # Gráficos
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">💰 Montos por Proyecto</div>', unsafe_allow_html=True)
        if 'Proyecto' in df.columns and 'Monto de contrato' in df.columns:
            top_f = df.nlargest(15, 'Monto de contrato')[['Proyecto', 'Monto de contrato']].dropna()
            fig = px.bar(top_f, x='Monto de contrato', y='Proyecto', orientation='h',
                        color_discrete_sequence=['#004481'])
            fig.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(autorange="reversed"),
                            font=dict(size=10))
            fig.update_xaxes(tickformat="$,.0f")
            st.plotly_chart(fig, use_container_width=True)
    
    with col_r:
        st.markdown('<div class="section-header">🏢 Afianzadoras</div>', unsafe_allow_html=True)
        if 'Afianzadora' in df.columns:
            df_af = df['Afianzadora'].value_counts().reset_index()
            df_af.columns = ['Afianzadora', 'Cantidad']
            fig = px.pie(df_af, values='Cantidad', names='Afianzadora', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=450, margin=dict(t=20, b=20), font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla
    st.markdown('<div class="section-header">📋 Detalle de Fianzas</div>', unsafe_allow_html=True)
    display_cols = [c for c in ['CR', 'Proyecto', 'Anexo de Obra', 'Afianzadora', 'No. Fianza',
                                'Monto de contrato', 'Monto Garantizado Fianza', 'Estatus Expedición',
                                'Vencimiento', 'Estatus Vigencia'] 
                   if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: FACTURAS ADQUIRA
# ═══════════════════════════════════════════════════════════════════════════════
elif modulo == "📊 Facturas Adquira":
    st.markdown("## 📊 Facturas Adquira")
    
    if 'facturas_adquira' not in sheets:
        st.error("No se encontraron datos de Facturas Adquira")
        st.stop()
    
    df = sheets['facturas_adquira'].copy()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("TOTAL FACTURAS", f"{len(df):,}"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("BASE IMPONIBLE", fmt_money(df['BASE IMPONIBLE'].sum()), "metric-card-green"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_card("TOTAL IMPUESTOS", fmt_money(df['TOTAL IMPUESTOS'].sum()), "metric-card-orange"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_card("TOTAL FACTURAS", fmt_money(df['TOTAL FACTURA'].sum()), "metric-card-red"), unsafe_allow_html=True)
    
    # Filtro por categoría
    if 'CATEGORIA' in df.columns:
        cats = ['Todas'] + sorted(df['CATEGORIA'].dropna().unique().tolist())
        sel_cat = st.selectbox("Categoría", cats)
        if sel_cat != 'Todas':
            df = df[df['CATEGORIA'] == sel_cat]
    
    # Gráficos
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">📊 Facturación por Categoría</div>', unsafe_allow_html=True)
        if 'CATEGORIA' in df.columns:
            df_cat = df.groupby('CATEGORIA')['TOTAL FACTURA'].sum().reset_index().sort_values('TOTAL FACTURA', ascending=False)
            fig = px.bar(df_cat, x='TOTAL FACTURA', y='CATEGORIA', orientation='h',
                        color_discrete_sequence=['#004481'])
            fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(autorange="reversed"),
                            font=dict(size=10))
            fig.update_xaxes(tickformat="$,.0f")
            st.plotly_chart(fig, use_container_width=True)
    
    with col_r:
        st.markdown('<div class="section-header">📈 Estado de Facturas</div>', unsafe_allow_html=True)
        if 'ESTADO' in df.columns:
            df_estado = df['ESTADO'].value_counts().reset_index()
            df_estado.columns = ['Estado', 'Cantidad']
            fig = px.pie(df_estado, values='Cantidad', names='Estado', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(height=400, margin=dict(t=20, b=20), font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla
    st.markdown('<div class="section-header">📋 Detalle</div>', unsafe_allow_html=True)
    display_cols = [c for c in ['NÚMERO', 'FECHA FACTURA', 'PEDIDO', 'CATEGORIA', 'PROYECTO RELACIONADO',
                                'BASE IMPONIBLE', 'TOTAL IMPUESTOS', 'TOTAL FACTURA', 'ESTADO', 'ESTATUS DE FACTURA'] 
                   if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: PROYECTOS 2024
# ═══════════════════════════════════════════════════════════════════════════════
elif modulo == "📁 Proyectos 2024":
    st.markdown("## 📁 Proyectos 2024 (Rezagados)")
    
    if 'proyectos_2024' not in sheets:
        st.error("No se encontraron datos de Proyectos 2024")
        st.stop()
    
    df = sheets['proyectos_2024'].copy()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(metric_card("TOTAL PROYECTOS", f"{len(df):,}"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_card("IMPORTE CIERRE", fmt_money(df['Importe de cierre'].sum()), "metric-card-green"), unsafe_allow_html=True)
    with col3:
        total_pag = df['Total Pagado'].sum() if 'Total Pagado' in df.columns else 0
        st.markdown(metric_card("TOTAL PAGADO", fmt_money(total_pag), "metric-card-orange"), unsafe_allow_html=True)
    with col4:
        por_pagar = df['Por pagar'].sum() if 'Por pagar' in df.columns else 0
        st.markdown(metric_card("POR PAGAR", fmt_money(por_pagar), "metric-card-red"), unsafe_allow_html=True)
    
    # Filtro
    if 'Estatus' in df.columns:
        est_list = ['Todos'] + sorted(df['Estatus'].dropna().unique().tolist())
        sel = st.selectbox("Estatus", est_list)
        if sel != 'Todos':
            df = df[df['Estatus'] == sel]
    
    # Gráficos
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">📊 Estatus de Proyectos</div>', unsafe_allow_html=True)
        if 'Estatus' in df.columns:
            df_est = df['Estatus'].value_counts().reset_index()
            df_est.columns = ['Estatus', 'Cantidad']
            fig = px.pie(df_est, values='Cantidad', names='Estatus', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=400, margin=dict(t=20, b=20), font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
    
    with col_r:
        st.markdown('<div class="section-header">💰 Top Proyectos por Importe</div>', unsafe_allow_html=True)
        top_p = df.nlargest(15, 'Importe de cierre')[['Sucursal', 'Importe de cierre']].dropna() if 'Sucursal' in df.columns else pd.DataFrame()
        if not top_p.empty:
            fig = px.bar(top_p, x='Importe de cierre', y='Sucursal', orientation='h',
                        color_discrete_sequence=['#0E6E3D'])
            fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(autorange="reversed"),
                            font=dict(size=10))
            fig.update_xaxes(tickformat="$,.0f")
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla
    st.markdown('<div class="section-header">📋 Detalle</div>', unsafe_allow_html=True)
    display_cols = [c for c in ['Llave comité /Clave UDA', 'CR', 'Sucursal', 'Proyecto', 
                                'Importe de cierre', 'Asignado a', 'Estatus', 'Días transcurridos',
                                'Total Pagado', 'Por pagar'] 
                   if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=400)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: EXPLORADOR DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════
elif modulo == "🔍 Explorador de Datos":
    st.markdown("## 🔍 Explorador de Datos")
    st.markdown("Explora todas las hojas del archivo en formato tabular interactivo.")
    
    sheet_names = {
        'ordenes': '📋 Órdenes de Compra',
        'contratos': '📑 Contratos One Team',
        'obra_menor': '🔧 Obra Menor',
        'facturacion_2025': '💰 Facturación 2025',
        'prefacturas': '📄 Prefacturas',
        'fianzas': '🛡️ Fianzas',
        'facturacion_adquira': '📊 Facturación Adquira',
        'facturas_adquira': '📊 Facturas Adquira (Copia)',
        'proyectos_2024': '📁 Proyectos 2024'
    }
    
    available = {v: k for k, v in sheet_names.items() if k in sheets}
    
    sel_sheet = st.selectbox("Selecciona una hoja", list(available.keys()))
    
    if sel_sheet:
        key = available[sel_sheet]
        df = sheets[key].copy()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(metric_card("FILAS", f"{len(df):,}"), unsafe_allow_html=True)
        with col2:
            st.markdown(metric_card("COLUMNAS", f"{len(df.columns):,}", "metric-card-green"), unsafe_allow_html=True)
        with col3:
            num_cols = df.select_dtypes(include=[np.number]).columns
            if len(num_cols) > 0:
                total = df[num_cols[0]].sum() if len(num_cols) > 0 else 0
                st.markdown(metric_card(f"SUMA: {num_cols[0][:20]}", fmt_money(total), "metric-card-orange"), unsafe_allow_html=True)
        
        # Búsqueda
        search = st.text_input("🔎 Buscar en todos los campos", "")
        if search:
            mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
            df = df[mask]
            st.info(f"Se encontraron {len(df)} registros")
        
        # Columnas numéricas para análisis rápido
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            st.markdown('<div class="section-header">📊 Análisis Rápido</div>', unsafe_allow_html=True)
            sel_col = st.selectbox("Columna numérica", num_cols)
            
            col_l, col_r = st.columns(2)
            with col_l:
                fig = px.histogram(df, x=sel_col, nbins=30, color_discrete_sequence=['#004481'])
                fig.update_layout(height=300, margin=dict(t=20, b=20), font=dict(size=11))
                st.plotly_chart(fig, use_container_width=True)
            with col_r:
                stats = df[sel_col].describe()
                st.dataframe(stats.round(2), use_container_width=True)
        
        # Tabla completa
        st.markdown('<div class="section-header">📋 Datos Completos</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=500)
        
        # Descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV", csv, f"{key}.csv", "text/csv")
