import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os, io, base64

st.set_page_config(page_title="SERVMAC — Control Documental 2025", page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")

# ─── LOGO SVG ───
LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 60">
  <defs><linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#004481"/><stop offset="100%" style="stop-color:#0066B3"/></linearGradient></defs>
  <rect x="0" y="8" width="48" height="44" rx="8" fill="url(#g1)"/>
  <path d="M12 22 L24 16 L36 22 L36 38 L24 44 L12 38Z" fill="none" stroke="white" stroke-width="2"/>
  <path d="M24 16 L24 44" stroke="white" stroke-width="1.5" opacity="0.6"/>
  <path d="M12 30 L36 30" stroke="white" stroke-width="1.5" opacity="0.6"/>
  <circle cx="24" cy="30" r="4" fill="#00A9E0"/>
  <text x="58" y="28" font-family="Helvetica,Arial,sans-serif" font-size="18" font-weight="700" fill="#004481">SERVMAC</text>
  <text x="58" y="46" font-family="Helvetica,Arial,sans-serif" font-size="10" font-weight="400" fill="#5C7D9A" letter-spacing="1.5">CONTROL DOCUMENTAL</text>
  <rect x="158" y="14" width="1.5" height="32" rx="1" fill="#E0E8F0"/>
  <text x="169" y="28" font-family="Helvetica,Arial,sans-serif" font-size="11" font-weight="600" fill="#004481">BBVA</text>
  <text x="169" y="42" font-family="Helvetica,Arial,sans-serif" font-size="8" font-weight="400" fill="#5C7D9A" letter-spacing="0.8">CONSERVACIÓN NE</text>
</svg>'''
LOGO_B64 = base64.b64encode(LOGO_SVG.encode()).decode()

# ─── CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.main .block-container { padding: 1.5rem 2.5rem 3rem; max-width: 1440px; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #001B36 0%, #002952 40%, #003D7A 100%); border-right: none; }
section[data-testid="stSidebar"] * { color: #C8DDEF !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] {
    background: rgba(255,255,255,0.04); border-radius: 10px; padding: 0.45rem 0.8rem; margin-bottom: 2px; transition: all 0.2s;
}
section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"]:hover { background: rgba(0,169,224,0.15); }

.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.kpi-card { background: white; border-radius: 14px; padding: 20px 22px; box-shadow: 0 1px 3px rgba(0,68,129,0.06); border-left: 4px solid #004481; transition: all 0.25s; position: relative; overflow: hidden; }
.kpi-card:hover { box-shadow: 0 4px 12px rgba(0,68,129,0.08); transform: translateY(-2px); }
.kpi-card::after { content: ''; position: absolute; top: 0; right: 0; width: 60px; height: 60px; background: linear-gradient(135deg, transparent 50%, rgba(0,68,129,0.03) 50%); border-radius: 0 14px 0 0; }
.kpi-card .kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; color: #5C7D9A; margin-bottom: 6px; }
.kpi-card .kpi-value { font-size: 1.55rem; font-weight: 700; color: #0F1B2D; line-height: 1.2; font-family: 'JetBrains Mono', monospace; }
.kpi-card .kpi-sub { font-size: 0.72rem; color: #5C7D9A; margin-top: 4px; }
.kpi-card.green { border-left-color: #0E6E3D; }
.kpi-card.orange { border-left-color: #D4721A; }
.kpi-card.red { border-left-color: #C0392B; }
.kpi-card.aqua { border-left-color: #00A9E0; }

.hero-kpi { background: linear-gradient(135deg, #004481 0%, #0066B3 60%, #00A9E0 100%); border-radius: 18px; padding: 28px 32px; color: white; box-shadow: 0 12px 40px rgba(0,68,129,0.12); margin-bottom: 28px; position: relative; overflow: hidden; }
.hero-kpi::before { content: ''; position: absolute; top: -30%; right: -10%; width: 200px; height: 200px; background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%); border-radius: 50%; }
.hero-kpi h4 { font-size: 0.8rem; opacity: 0.8; margin: 0; font-weight: 400; letter-spacing: 1px; text-transform: uppercase; }
.hero-kpi h1 { font-size: 2rem; margin: 8px 0 4px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.hero-kpi p { font-size: 0.85rem; opacity: 0.75; margin: 0; }

.section-hdr { display: flex; align-items: center; gap: 10px; margin: 28px 0 16px; padding-bottom: 10px; border-bottom: 2px solid #EEF2F7; }
.section-hdr .icon { width: 34px; height: 34px; background: linear-gradient(135deg, #004481, #0066B3); border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; }
.section-hdr h3 { font-size: 1.05rem; font-weight: 600; color: #0F1B2D; margin: 0; }
.section-hdr .badge { background: #EEF2F7; color: #5C7D9A; font-size: 0.7rem; padding: 3px 10px; border-radius: 20px; font-weight: 500; }

.overview-section { background: white; border-radius: 14px; padding: 24px; box-shadow: 0 1px 3px rgba(0,68,129,0.06); margin-bottom: 16px; border: 1px solid #E8EEF4; }
.overview-section h4 { font-size: 0.95rem; font-weight: 600; color: #004481; margin: 0 0 16px; padding-bottom: 10px; border-bottom: 1px solid #EEF2F7; display: flex; align-items: center; gap: 8px; }
.ov-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }
.ov-item { background: #F7F9FC; border-radius: 10px; padding: 12px 16px; }
.ov-item .label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.6px; color: #5C7D9A; font-weight: 500; }
.ov-item .val { font-size: 0.95rem; font-weight: 600; color: #0F1B2D; margin-top: 2px; }

.status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.status-badge.green { background: #E8F5E9; color: #0E6E3D; }
.status-badge.orange { background: #FFF3E0; color: #D4721A; }
.status-badge.red { background: #FFEBEE; color: #C0392B; }
.status-badge.blue { background: #E3F2FD; color: #004481; }

div[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,68,129,0.06); }
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #F7F9FC; border-radius: 12px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px; padding: 8px 20px; font-weight: 500; font-size: 0.85rem; }
.stDownloadButton button { background: linear-gradient(135deg, #004481, #0066B3) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; padding: 0.5rem 1.5rem !important; }
.stDownloadButton button:hover { box-shadow: 0 4px 12px rgba(0,68,129,0.12) !important; transform: translateY(-1px) !important; }
.divider { height: 1px; background: #EEF2F7; margin: 24px 0; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ───
def fmt(v):
    if pd.isna(v) or v is None: return "$0.00"
    return f"${v:,.2f}"

def fmt_int(v):
    if pd.isna(v) or v is None: return "0"
    return f"{int(v):,}"

def kpi_card(label, value, sub="", style=""):
    s = f'<div class="kpi-card {style}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>'
    if sub: s += f'<div class="kpi-sub">{sub}</div>'
    return s + '</div>'

def section_header(icon, title, badge=""):
    b = f'<span class="badge">{badge}</span>' if badge else ""
    return f'<div class="section-hdr"><div class="icon">{icon}</div><h3>{title}</h3>{b}</div>'

def ov_item(label, value):
    return f'<div class="ov-item"><div class="label">{label}</div><div class="val">{value}</div></div>'

PLOTLY_LAYOUT = dict(font=dict(family="DM Sans, sans-serif", size=12, color="#0F1B2D"), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=30, b=20), hoverlabel=dict(bgcolor="white", font_size=12))
COLORS = ['#004481','#0066B3','#00A9E0','#4DC8E9','#0E6E3D','#D4721A','#C0392B','#8E44AD','#2C3E50']

# ─── DATA LOADING ───
@st.cache_data
def load_data(fp):
    sheets = {}
    xls = pd.ExcelFile(fp)
    cfg = {
        'ordenes': ('REGISTRO ORDEN DE COMPRA', 1, ['FECHA','FECHA DE PUBLICACIÓN'], ['IMPORTE TOTAL','IMPORTE SIN IVA','IMPORTE DE LA ORDEN [TOTAL IMPORTE CONTRATO] -SIN IVA','IMPORTE CORRESPONDIENTE A CANTIDAD EXPEDIDA','IMPORTE DE CIERRE','BALANCE'], 'ID. PEDIDO COMPRADOR'),
        'contratos': ('CONTRATOS || ONE TEAM', 1, ['Fecha de asignación proyecto','Fecha inicio vigencia anexo','Fecha de Recepción','Fecha Firma Interna','Fecha de detonación','Fecha de cierre operación (Acta final)','Fecha envío cierre'], ['Importe Acción','Importe Certificación','Importe Total','Importe Cierre Administrativo','Total Pagado','Por pagar','Por devolver'], 'ID Folio Contrato'),
        'obra_menor': ('OBRA MENOR', 1, ['FECHA_DE_ASIGNACIÓN','FECHA INICIO','FECHA FIN','FECHA FIN REAL','FECHA CORREO DETONACIÓN','FECHA CIERRE ADMINISTRATIVO'], ['PRESUPUESTO_INICIAL','IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL','Importe UDA','Total Pagado','VARIACIÓN_PRESUPUESTAL'], 'ID_PROYECTO'),
        'facturacion_2025': ('Facturación 2025', 0, ['Fecha'], ['Subtotal (MXN)','Impuestos (MXN)','Total (MXN)'], 'NO.'),
        'prefacturas': ('CONTROL DE PREFACTURAS', 1, ['Fecha solicitud','Fecha Emisión','Fecha de aceptación','Fecha de factura'], ['Monto (sin IVA)','IVA','Total'], 'Folio Interno'),
        'fianzas': ('CONTROL DE FIANZAS', 1, ['Fecha Solicitud Fianza','Fecha Emisión','Vencimiento'], ['Monto de contrato','Monto + IVA','Importe a afianzar || Cumplimiento','Importe a afianzar || Buena calidad','Monto Garantizado Fianza'], 'CR'),
        'facturas_adquira': ('Copia de Facturas Adquira', 0, [], ['BASE IMPONIBLE','TOTAL IMPUESTOS','TOTAL FACTURA'], 'NÚMERO'),
        'proyectos_2024': ('Proyectos 2024', 1, [], ['Importe de cierre','Total Pagado','Por pagar','Por devolver','Importe CFE'], 'Llave comité /Clave UDA'),
    }
    for key, (sn, hdr, dates, nums, drop) in cfg.items():
        try:
            df = pd.read_excel(xls, sn, header=hdr)
            df.columns = df.columns.str.strip()
            for c in dates:
                if c in df.columns: df[c] = pd.to_datetime(df[c], errors='coerce')
            for c in nums:
                if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=[drop], how='all')
            sheets[key] = df
        except: pass
    return sheets

def get_all_sucursales(S):
    n = set()
    mappings = [('ordenes','NOMBRE DEL PROYECTO O SUCURSAL'), ('obra_menor','SUCURSAL'), ('contratos','Proyecto / Obra'),
                ('prefacturas','Proyecto / Obra'), ('fianzas','Proyecto'), ('proyectos_2024','Sucursal')]
    for k, c in mappings:
        if k in S and c in S[k].columns: n.update(S[k][c].dropna().unique())
    return sorted([str(x) for x in n if str(x).strip()])

def get_sucursal_data(S, suc):
    d, u = {}, str(suc).upper().strip()
    mappings = [('ordenes','NOMBRE DEL PROYECTO O SUCURSAL'), ('contratos','Proyecto / Obra'), ('obra_menor','SUCURSAL'),
                ('prefacturas','Proyecto / Obra'), ('fianzas','Proyecto'), ('proyectos_2024','Sucursal'), ('facturas_adquira','PROYECTO RELACIONADO')]
    for k, c in mappings:
        if k in S and c in S[k].columns:
            m = S[k][S[k][c].astype(str).str.upper().str.strip().str.contains(u, na=False)]
            if len(m) > 0: d[k] = m
    return d

def generate_pdf(suc, sd):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=0.7*inch, rightMargin=0.7*inch, topMargin=0.7*inch, bottomMargin=0.7*inch)
    bb = HexColor('#004481'); bm = HexColor('#0066B3'); bg = HexColor('#F7F9FC'); bd = HexColor('#E0E8F0'); tx = HexColor('#5C7D9A')
    sty = getSampleStyleSheet()
    sty.add(ParagraphStyle('T', parent=sty['Title'], fontSize=20, textColor=bb, fontName='Helvetica-Bold', spaceAfter=4))
    sty.add(ParagraphStyle('Sub', parent=sty['Normal'], fontSize=10, textColor=tx, spaceAfter=16))
    sty.add(ParagraphStyle('SH', parent=sty['Heading2'], fontSize=13, textColor=bb, fontName='Helvetica-Bold', spaceBefore=20, spaceAfter=8))
    sty.add(ParagraphStyle('CT', parent=sty['Normal'], fontSize=7.5, leading=10))
    sty.add(ParagraphStyle('CB', parent=sty['Normal'], fontSize=7.5, leading=10, fontName='Helvetica-Bold'))
    sty.add(ParagraphStyle('FT', parent=sty['Normal'], fontSize=7, textColor=tx))
    story = []
    story.append(Paragraph("SERVMAC — Sistema Integral de Control Documental", sty['T']))
    story.append(Paragraph(f"Reporte: <b>{suc}</b> | {datetime.now().strftime('%d/%m/%Y %H:%M')} | Conservación BBVA Noreste", sty['Sub']))
    story.append(HRFlowable(width="100%", thickness=2, color=bb, spaceAfter=12))

    tots = [('ÓRDENES', len(sd.get('ordenes',[])), sd.get('ordenes',pd.DataFrame()).get('IMPORTE TOTAL',pd.Series(dtype=float)).sum()),
            ('CONTRATOS', len(sd.get('contratos',[])), sd.get('contratos',pd.DataFrame()).get('Importe Total',pd.Series(dtype=float)).sum()),
            ('OBRA MENOR', len(sd.get('obra_menor',[])), sd.get('obra_menor',pd.DataFrame()).get('IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL',pd.Series(dtype=float)).sum()),
            ('PREFACTURAS', len(sd.get('prefacturas',[])), sd.get('prefacturas',pd.DataFrame()).get('Total',pd.Series(dtype=float)).sum())]
    kd = [[Paragraph(f'<b>{t[0]}</b>', sty['CB']) for t in tots],
          [Paragraph(f'{t[1]} reg.', sty['CT']) for t in tots],
          [Paragraph(f'<b>${t[2]:,.2f}</b>', sty['CB']) for t in tots]]
    kt = Table(kd, colWidths=[doc.width/4]*4)
    kt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),bb),('TEXTCOLOR',(0,0),(-1,0),white),('BACKGROUND',(0,1),(-1,-1),bg),
        ('GRID',(0,0),(-1,-1),0.5,bd),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(kt); story.append(Spacer(1,16))

    def add_tbl(title, df, cols):
        if df is None or len(df)==0: return
        cs = [c for c in cols if c in df.columns]
        if not cs: return
        story.append(Paragraph(title, sty['SH']))
        hdr = [Paragraph(f'<b>{c[:22]}</b>', sty['CB']) for c in cs]
        rows = [hdr]
        for _, r in df.head(30).iterrows():
            row = []
            for c in cs:
                v = r[c]
                if pd.isna(v): v = "—"
                elif isinstance(v, float): v = f"${v:,.2f}" if abs(v) > 100 else f"{v:,.2f}"
                elif isinstance(v, pd.Timestamp): v = v.strftime('%d/%m/%Y')
                else: v = str(v)[:35]
                row.append(Paragraph(v, sty['CT']))
            rows.append(row)
        cw = [doc.width/len(cs)]*len(cs)
        t = Table(rows, colWidths=cw, repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),bm),('TEXTCOLOR',(0,0),(-1,0),white),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,bg]),
            ('GRID',(0,0),(-1,-1),0.4,bd),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]))
        story.append(t)
        if len(df)>30: story.append(Paragraph(f"<i>30 de {len(df)} registros</i>", sty['FT']))
        story.append(Spacer(1,10))

    add_tbl("Órdenes de Compra", sd.get('ordenes'), ['FECHA','IMPORTE TOTAL','ESTADO','TIPO DE PROYECTO','IMPORTE DE CIERRE','ESTATUS'])
    add_tbl("Contratos One Team", sd.get('contratos'), ['ID Folio Contrato','Importe Total','Estatus Operativo','Estatus Cierre','Total Pagado','Por pagar'])
    add_tbl("Obra Menor", sd.get('obra_menor'), ['ID_PROYECTO','PROYECTO','ASIGNADO_A','ESTATUS_OPERACIÓN REAL','PRESUPUESTO_INICIAL','IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL','Total Pagado'])
    add_tbl("Prefacturas", sd.get('prefacturas'), ['Folio Interno','Fecha solicitud','Monto (sin IVA)','Total','Estatus'])
    add_tbl("Fianzas", sd.get('fianzas'), ['CR','Afianzadora','Monto de contrato','Estatus Expedición','Vencimiento','Estatus Vigencia'])
    add_tbl("Proyectos 2024", sd.get('proyectos_2024'), ['CR','Proyecto','Importe de cierre','Estatus','Total Pagado','Por pagar'])
    add_tbl("Facturas Adquira", sd.get('facturas_adquira'), ['NÚMERO','FECHA FACTURA','CATEGORIA','BASE IMPONIBLE','TOTAL FACTURA','ESTADO'])

    story.append(Spacer(1,20))
    story.append(HRFlowable(width="100%", thickness=1, color=bd, spaceAfter=8))
    story.append(Paragraph(f"SERVMAC — Conservación BBVA Noreste | {datetime.now().strftime('%d/%m/%Y %H:%M')} | Sistema Integral 2025", sty['FT']))
    doc.build(story); buf.seek(0)
    return buf

# ─── LOAD ───
DATA_PATH = "SISTEMA_INTEGRAL_DE_CONTROL_DOCUMENTAL_2025.xlsx"
if not os.path.exists(DATA_PATH):
    for p in ["/mnt/user-data/uploads/SISTEMA_INTEGRAL_DE_CONTROL_DOCUMENTAL_2025.xlsx", "data/SISTEMA_INTEGRAL_DE_CONTROL_DOCUMENTAL_2025.xlsx"]:
        if os.path.exists(p): DATA_PATH = p; break

with st.sidebar:
    st.markdown(f'<div style="padding:16px 0 8px;"><img src="data:image/svg+xml;base64,{LOGO_B64}" style="width:210px;"></div>', unsafe_allow_html=True)
    st.markdown("")
    uploaded = st.file_uploader("", type=['xlsx','xls'], label_visibility="collapsed")
    if uploaded: DATA_PATH = uploaded
    if not os.path.exists(DATA_PATH) if isinstance(DATA_PATH, str) else False:
        if not uploaded: st.warning("Sube tu archivo Excel"); st.stop()
    st.markdown("---")
    modulo = st.radio("NAVEGACIÓN", ["🏠  Dashboard","🔎  Overview Sucursal","📋  Órdenes de Compra","📑  Contratos One Team",
        "🔧  Obra Menor","💰  Facturación 2025","📄  Prefacturas","🛡️  Fianzas","📊  Facturas Adquira","📁  Proyectos 2024","🗂️  Explorador"], index=0)
    st.markdown("---")
    st.markdown(f'<div style="text-align:center;opacity:0.5;font-size:0.7rem;">Actualizado {datetime.now().strftime("%d/%m/%Y")}<br>v2.0</div>', unsafe_allow_html=True)

try: sheets = load_data(DATA_PATH)
except Exception as e: st.error(f"Error: {e}"); st.stop()

# ─── GENERIC MODULE RENDERER ───
def render_module(title, key, kpis, filters, chart_fn, tcols):
    if key not in sheets: st.error(f"Sin datos: {title}"); return
    df = sheets[key].copy()
    st.markdown(f'<div class="hero-kpi" style="padding:18px 28px;"><h4>{title.upper()}</h4><h1>{fmt_int(len(df))} registros</h1></div>', unsafe_allow_html=True)
    fc = st.columns(len(filters)) if filters else []
    for i,(cn,lb) in enumerate(filters):
        if cn in df.columns:
            with fc[i]:
                o = ['Todos'] + sorted([str(x) for x in df[cn].dropna().unique()])
                s = st.selectbox(lb, o, key=f"f_{key}_{cn}")
                if s != 'Todos': df = df[df[cn].astype(str) == s]
    h = '<div class="kpi-grid">'
    for lb,col,sty in kpis:
        v = df[col].sum() if col in df.columns else 0
        h += kpi_card(lb, fmt(v) if abs(v)>1000 else fmt_int(v), f"{df[col].notna().sum() if col in df.columns else 0} reg.", sty)
    st.markdown(h+'</div>', unsafe_allow_html=True)
    chart_fn(df)
    st.markdown(section_header("📋","Detalle",f"{len(df)} reg."), unsafe_allow_html=True)
    dc = [c for c in tcols if c in df.columns]
    st.dataframe(df[dc], use_container_width=True, height=420, hide_index=True)
    st.download_button("📥 CSV", df.to_csv(index=False).encode('utf-8'), f"{key}.csv", "text/csv")

# ═══ DASHBOARD ═══
if modulo == "🏠  Dashboard":
    st.markdown(f'<div class="hero-kpi"><h4>SISTEMA INTEGRAL DE CONTROL DOCUMENTAL 2025</h4><h1>SERVMAC — Conservación BBVA Noreste</h1><p>Panel de control y monitoreo operativo | {len(sheets)} módulos activos</p></div>', unsafe_allow_html=True)
    kpis = [
        ("Órdenes de Compra", fmt_int(len(sheets.get('ordenes',[]))), fmt(sheets.get('ordenes',pd.DataFrame()).get('IMPORTE TOTAL',pd.Series(dtype=float)).sum())+" total", ""),
        ("Contratos One Team", fmt_int(len(sheets.get('contratos',[]))), fmt(sheets.get('contratos',pd.DataFrame()).get('Importe Total',pd.Series(dtype=float)).sum())+" total", "green"),
        ("Obra Menor", fmt_int(len(sheets.get('obra_menor',[]))), fmt(sheets.get('obra_menor',pd.DataFrame()).get('IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL',pd.Series(dtype=float)).sum())+" cierre", "orange"),
        ("Facturación 2025", fmt_int(len(sheets.get('facturacion_2025',[]))), fmt(sheets.get('facturacion_2025',pd.DataFrame()).get('Total (MXN)',pd.Series(dtype=float)).sum())+" total", "aqua"),
        ("Prefacturas", fmt_int(len(sheets.get('prefacturas',[]))), fmt(sheets.get('prefacturas',pd.DataFrame()).get('Total',pd.Series(dtype=float)).sum()), "red"),
        ("Fianzas", fmt_int(len(sheets.get('fianzas',[]))), fmt(sheets.get('fianzas',pd.DataFrame()).get('Monto Garantizado Fianza',pd.Series(dtype=float)).sum())+" garantizado", "green"),
    ]
    st.markdown('<div class="kpi-grid">'+''.join(kpi_card(l,v,s,c) for l,v,s,c in kpis)+'</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown(section_header("📊","Órdenes por Estado"), unsafe_allow_html=True)
        if 'ordenes' in sheets and 'ESTADO' in sheets['ordenes'].columns:
            d=sheets['ordenes']['ESTADO'].value_counts().reset_index(); d.columns=['Estado','Cantidad']
            fig=px.pie(d,values='Cantidad',names='Estado',hole=0.55,color_discrete_sequence=COLORS)
            fig.update_layout(**PLOTLY_LAYOUT,height=370,legend=dict(orientation="h",yanchor="bottom",y=-0.15,font=dict(size=10)))
            fig.update_traces(textposition='inside',textinfo='percent+label',textfont_size=10)
            st.plotly_chart(fig,use_container_width=True)
    with c2:
        st.markdown(section_header("💰","Facturación Mensual 2025"), unsafe_allow_html=True)
        if 'facturacion_2025' in sheets and 'Fecha' in sheets['facturacion_2025'].columns:
            d=sheets['facturacion_2025'].dropna(subset=['Fecha']).copy(); d['M']=d['Fecha'].dt.to_period('M').astype(str)
            m=d.groupby('M')['Total (MXN)'].sum().reset_index()
            fig=go.Figure(go.Bar(x=m['M'],y=m['Total (MXN)'],marker=dict(color=m['Total (MXN)'],colorscale=[[0,'#004481'],[1,'#00A9E0']]),hovertemplate='%{x}<br>$%{y:,.0f}<extra></extra>'))
            fig.update_layout(**PLOTLY_LAYOUT,height=370,xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor='#F0F0F0',tickformat='$,.0f'))
            st.plotly_chart(fig,use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown(section_header("🔧","Obra Menor — Estatus"), unsafe_allow_html=True)
        if 'obra_menor' in sheets and 'ESTATUS_OPERACIÓN REAL' in sheets['obra_menor'].columns:
            d=sheets['obra_menor']['ESTATUS_OPERACIÓN REAL'].value_counts().head(8).reset_index(); d.columns=['E','C']
            fig=px.bar(d,x='C',y='E',orientation='h',color='C',color_continuous_scale=[[0,'#E8F5E9'],[1,'#0E6E3D']])
            fig.update_layout(**PLOTLY_LAYOUT,height=370,coloraxis_showscale=False,yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig,use_container_width=True)
    with c4:
        st.markdown(section_header("📑","Contratos — Estatus Operativo"), unsafe_allow_html=True)
        if 'contratos' in sheets and 'Estatus Operativo' in sheets['contratos'].columns:
            d=sheets['contratos']['Estatus Operativo'].value_counts().head(8).reset_index(); d.columns=['E','C']
            fig=px.bar(d,x='C',y='E',orientation='h',color='C',color_continuous_scale=[[0,'#FFF3E0'],[1,'#D4721A']])
            fig.update_layout(**PLOTLY_LAYOUT,height=370,coloraxis_showscale=False,yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig,use_container_width=True)

    st.markdown(section_header("🏢","Distribución por Tipo de Proyecto"), unsafe_allow_html=True)
    if 'ordenes' in sheets and 'TIPO DE PROYECTO' in sheets['ordenes'].columns:
        d=sheets['ordenes'].groupby('TIPO DE PROYECTO').agg(Cant=('TIPO DE PROYECTO','count'),Imp=('IMPORTE TOTAL','sum')).reset_index().sort_values('Imp',ascending=False)
        fig=make_subplots(rows=1,cols=2,specs=[[{"type":"bar"},{"type":"pie"}]],subplot_titles=("Importe por Tipo","Distribución"))
        fig.add_trace(go.Bar(x=d['TIPO DE PROYECTO'],y=d['Imp'],marker_color=COLORS[:len(d)]),row=1,col=1)
        fig.add_trace(go.Pie(labels=d['TIPO DE PROYECTO'],values=d['Cant'],hole=0.5,marker_colors=COLORS[:len(d)]),row=1,col=2)
        fig.update_layout(**PLOTLY_LAYOUT,height=420,showlegend=False); fig.update_yaxes(tickformat="$,.0f",row=1,col=1)
        st.plotly_chart(fig,use_container_width=True)

# ═══ OVERVIEW SUCURSAL ═══
elif modulo == "🔎  Overview Sucursal":
    st.markdown('<div class="hero-kpi" style="padding:22px 28px;"><h4>OVERVIEW DE SUCURSAL / PROYECTO</h4><h1>Vista 360° del proyecto</h1><p>Selecciona una sucursal para ver toda su información consolidada y exportar a PDF</p></div>', unsafe_allow_html=True)
    sucs = get_all_sucursales(sheets)
    if not sucs: st.warning("No se encontraron sucursales."); st.stop()
    sel = st.selectbox("🏢 Selecciona Sucursal / Proyecto", [""]+sucs, format_func=lambda x: "— Selecciona —" if x=="" else x)
    if sel:
        sd = get_sucursal_data(sheets, sel)
        if not sd: st.info(f"Sin registros para **{sel}**."); st.stop()

        to = sd.get('ordenes',pd.DataFrame()).get('IMPORTE TOTAL',pd.Series(dtype=float)).sum()
        tc = sd.get('contratos',pd.DataFrame()).get('Importe Total',pd.Series(dtype=float)).sum()
        tom = sd.get('obra_menor',pd.DataFrame()).get('IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL',pd.Series(dtype=float)).sum()
        tpf = sd.get('prefacturas',pd.DataFrame()).get('Total',pd.Series(dtype=float)).sum()
        tp = sd.get('contratos',pd.DataFrame()).get('Total Pagado',pd.Series(dtype=float)).sum() + sd.get('obra_menor',pd.DataFrame()).get('Total Pagado',pd.Series(dtype=float)).sum()
        pp = sd.get('contratos',pd.DataFrame()).get('Por pagar',pd.Series(dtype=float)).sum()

        st.markdown(f'<div class="kpi-grid">{kpi_card("Importe Órdenes",fmt(to),f"{len(sd.get("ordenes",[]))} reg.")}{kpi_card("Importe Contratos",fmt(tc),f"{len(sd.get("contratos",[]))} contratos","green")}{kpi_card("Cierre Obra Menor",fmt(tom),f"{len(sd.get("obra_menor",[]))} proy.","orange")}{kpi_card("Total Pagado",fmt(tp),"Contratos+Obra","aqua")}{kpi_card("Por Pagar",fmt(pp),"Pendiente","red")}{kpi_card("Prefacturas",fmt(tpf),f"{len(sd.get("prefacturas",[]))} reg.","green")}</div>', unsafe_allow_html=True)

        cb,_ = st.columns([1,3])
        with cb:
            pdf = generate_pdf(sel, sd)
            st.download_button("📥 Exportar Overview a PDF", pdf, f"Overview_{sel.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if 'ordenes' in sd:
            df=sd['ordenes']; st.markdown(section_header("📋","Órdenes de Compra",f"{len(df)} reg."), unsafe_allow_html=True)
            h='<div class="overview-section"><div class="ov-grid">'
            for _,r in df.iterrows():
                h+=ov_item("Pedido",str(r.get('ID. PEDIDO COMPRADOR','—')))+ov_item("Estado",str(r.get('ESTADO','—')))+ov_item("Importe",fmt(r.get('IMPORTE TOTAL')))+ov_item("Tipo",str(r.get('TIPO DE PROYECTO','—')))+ov_item("Cierre",fmt(r.get('IMPORTE DE CIERRE')))+ov_item("Estatus",str(r.get('ESTATUS','—')))
            st.markdown(h+'</div></div>', unsafe_allow_html=True)
            with st.expander("Ver tabla"):
                dc=[c for c in ['ID. PEDIDO COMPRADOR','FECHA','IMPORTE TOTAL','ESTADO','TIPO DE PROYECTO','IMPORTE DE CIERRE','BALANCE','ESTATUS'] if c in df.columns]
                st.dataframe(df[dc],use_container_width=True,hide_index=True)

        if 'contratos' in sd:
            df=sd['contratos']; st.markdown(section_header("📑","Contratos One Team",f"{len(df)} contratos"), unsafe_allow_html=True)
            for _,r in df.iterrows():
                st.markdown(f'<div class="overview-section"><h4>📑 {r.get("ID Folio Contrato","—")}</h4><div class="ov-grid">{ov_item("CR",str(r.get("CR","—")))}{ov_item("Importe Total",fmt(r.get("Importe Total")))}{ov_item("Estatus Op.",str(r.get("Estatus Operativo","—")))}{ov_item("Estatus Cierre",str(r.get("Estatus Cierre","—")))}{ov_item("Supervisor",str(r.get("Supervisor asignado para coordinación / revisión","—")))}{ov_item("Pagado",fmt(r.get("Total Pagado")))}{ov_item("Por Pagar",fmt(r.get("Por pagar")))}{ov_item("Contrato",str(r.get("Contrato Número","—")))}{ov_item("Anexo",str(r.get("Anexo de Obra","—")))}{ov_item("Tipología",str(r.get("Tipología","—")))}</div></div>', unsafe_allow_html=True)

        if 'obra_menor' in sd:
            df=sd['obra_menor']; st.markdown(section_header("🔧","Obra Menor",f"{len(df)} proy."), unsafe_allow_html=True)
            for _,r in df.iterrows():
                es=str(r.get("ESTATUS_OPERACIÓN REAL","—"))
                bc="green" if any(x in es.lower() for x in ["terminad","cerrad"]) else "orange" if "proceso" in es.lower() else "blue"
                st.markdown(f'<div class="overview-section"><h4>🔧 {r.get("ID_PROYECTO","—")} <span class="status-badge {bc}">{es}</span></h4><div class="ov-grid">{ov_item("Sucursal",str(r.get("SUCURSAL","—")))}{ov_item("Proyecto",str(r.get("PROYECTO","—")))}{ov_item("Asignado",str(r.get("ASIGNADO_A","—")))}{ov_item("Presupuesto",fmt(r.get("PRESUPUESTO_INICIAL")))}{ov_item("Cierre Adm.",fmt(r.get("IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL")))}{ov_item("Pagado",fmt(r.get("Total Pagado")))}{ov_item("Variación",fmt(r.get("VARIACIÓN_PRESUPUESTAL")))}{ov_item("Fecha Asig.",str(r.get("FECHA_DE_ASIGNACIÓN","—"))[:10])}{ov_item("Días",str(r.get("DÍAS DESDE LA ASIGNACIÓN","—")))}{ov_item("Est. Pago",str(r.get("Estatus de pago","—")))}</div></div>', unsafe_allow_html=True)

            if len(df)>0 and all(c in df.columns for c in ['PRESUPUESTO_INICIAL','IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL']):
                dc=df[['ID_PROYECTO','PRESUPUESTO_INICIAL','IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL']].dropna()
                if len(dc)>0:
                    fig=go.Figure()
                    fig.add_trace(go.Bar(x=dc['ID_PROYECTO'],y=dc['PRESUPUESTO_INICIAL'],name='Presupuesto',marker_color='#004481'))
                    fig.add_trace(go.Bar(x=dc['ID_PROYECTO'],y=dc['IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL'],name='Cierre',marker_color='#00A9E0'))
                    fig.update_layout(**PLOTLY_LAYOUT,height=350,barmode='group',yaxis=dict(tickformat='$,.0f',showgrid=True,gridcolor='#F0F0F0'))
                    st.plotly_chart(fig,use_container_width=True)

        if 'prefacturas' in sd:
            df=sd['prefacturas']; st.markdown(section_header("📄","Prefacturas",f"{len(df)} reg."), unsafe_allow_html=True)
            for _,r in df.iterrows():
                st.markdown(f'<div class="overview-section"><h4>📄 {r.get("Folio Interno","—")}</h4><div class="ov-grid">{ov_item("Folio PF",str(r.get("Folio Pre Factura","—")))}{ov_item("Fecha",str(r.get("Fecha solicitud","—"))[:10])}{ov_item("Monto s/IVA",fmt(r.get("Monto (sin IVA)")))}{ov_item("Total",fmt(r.get("Total")))}{ov_item("Estatus",str(r.get("Estatus","—")))}{ov_item("Factura?",str(r.get("¿Se emitió factura?","—")))}</div></div>', unsafe_allow_html=True)

        if 'fianzas' in sd:
            df=sd['fianzas']; st.markdown(section_header("🛡️","Fianzas",f"{len(df)} reg."), unsafe_allow_html=True)
            for _,r in df.iterrows():
                st.markdown(f'<div class="overview-section"><h4>🛡️ Fianza — {r.get("No. Fianza","—")}</h4><div class="ov-grid">{ov_item("Afianzadora",str(r.get("Afianzadora","—")))}{ov_item("Monto Contrato",fmt(r.get("Monto de contrato")))}{ov_item("Garantizado",fmt(r.get("Monto Garantizado Fianza")))}{ov_item("Expedición",str(r.get("Estatus Expedición","—")))}{ov_item("Vencimiento",str(r.get("Vencimiento","—"))[:10])}{ov_item("Vigencia",str(r.get("Estatus Vigencia","—")))}</div></div>', unsafe_allow_html=True)

        if 'proyectos_2024' in sd:
            df=sd['proyectos_2024']; st.markdown(section_header("📁","Proyectos 2024",f"{len(df)} reg."), unsafe_allow_html=True)
            for _,r in df.iterrows():
                st.markdown(f'<div class="overview-section"><h4>📁 {r.get("Sucursal","—")} — {r.get("Proyecto","—")}</h4><div class="ov-grid">{ov_item("CR",str(r.get("CR","—")))}{ov_item("Cierre",fmt(r.get("Importe de cierre")))}{ov_item("Estatus",str(r.get("Estatus","—")))}{ov_item("Asignado",str(r.get("Asignado a","—")))}{ov_item("Pagado",fmt(r.get("Total Pagado")))}{ov_item("Por Pagar",fmt(r.get("Por pagar")))}</div></div>', unsafe_allow_html=True)

        if 'facturas_adquira' in sd:
            df=sd['facturas_adquira']; st.markdown(section_header("📊","Facturas Adquira",f"{len(df)} reg."), unsafe_allow_html=True)
            dc=[c for c in ['NÚMERO','FECHA FACTURA','PEDIDO','CATEGORIA','BASE IMPONIBLE','TOTAL FACTURA','ESTADO'] if c in df.columns]
            st.dataframe(df[dc],use_container_width=True,hide_index=True)
    else:
        st.markdown('<div style="text-align:center;padding:60px 20px;color:#5C7D9A;"><div style="font-size:3rem;margin-bottom:12px;">🏢</div><h3 style="color:#5C7D9A;font-weight:500;">Selecciona una sucursal o proyecto</h3><p style="font-size:0.9rem;">Usa el selector para ver la vista 360° con información consolidada</p></div>', unsafe_allow_html=True)

# ═══ ÓRDENES ═══
elif modulo == "📋  Órdenes de Compra":
    def ch(df):
        c1,c2=st.columns(2)
        with c1:
            st.markdown(section_header("🏆","Top 15 por Importe"),unsafe_allow_html=True)
            if 'NOMBRE DEL PROYECTO O SUCURSAL' in df.columns:
                t=df.groupby('NOMBRE DEL PROYECTO O SUCURSAL')['IMPORTE TOTAL'].sum().nlargest(15).reset_index()
                fig=px.bar(t,x='IMPORTE TOTAL',y='NOMBRE DEL PROYECTO O SUCURSAL',orientation='h',color='IMPORTE TOTAL',color_continuous_scale=[[0,'#00A9E0'],[1,'#004481']])
                fig.update_layout(**PLOTLY_LAYOUT,height=480,coloraxis_showscale=False,yaxis=dict(autorange="reversed"),xaxis=dict(tickformat='$,.0f'))
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown(section_header("📈","Evolución Mensual"),unsafe_allow_html=True)
            if 'FECHA' in df.columns:
                d=df.dropna(subset=['FECHA']).copy(); d['M']=d['FECHA'].dt.to_period('M').astype(str)
                m=d.groupby('M').agg(C=('M','count'),I=('IMPORTE TOTAL','sum')).reset_index()
                fig=make_subplots(specs=[[{"secondary_y":True}]])
                fig.add_trace(go.Bar(x=m['M'],y=m['I'],name='Importe',marker_color='#004481'),secondary_y=False)
                fig.add_trace(go.Scatter(x=m['M'],y=m['C'],name='Cantidad',line=dict(color='#00A9E0',width=3),mode='lines+markers'),secondary_y=True)
                fig.update_layout(**PLOTLY_LAYOUT,height=480); fig.update_yaxes(tickformat="$,.0f",secondary_y=False)
                st.plotly_chart(fig,use_container_width=True)
    render_module("Órdenes de Compra","ordenes",[("Importe Total","IMPORTE TOTAL",""),("Sin IVA","IMPORTE SIN IVA","green"),("Cierre","IMPORTE DE CIERRE","orange")],
        [("ESTADO","Estado"),("TIPO DE PROYECTO","Tipo Proyecto")],ch,
        ['ID. PEDIDO COMPRADOR','FECHA','IMPORTE TOTAL','ESTADO','NOMBRE DEL PROYECTO O SUCURSAL','TIPO DE PROYECTO','IMPORTE DE CIERRE','BALANCE','ESTATUS'])

# ═══ CONTRATOS ═══
elif modulo == "📑  Contratos One Team":
    def ch(df):
        c1,c2=st.columns(2)
        with c1:
            st.markdown(section_header("💰","Top 15"),unsafe_allow_html=True)
            if 'Proyecto / Obra' in df.columns and 'Importe Total' in df.columns:
                t=df.nlargest(15,'Importe Total')[['Proyecto / Obra','Importe Total']].dropna()
                fig=px.bar(t,x='Importe Total',y='Proyecto / Obra',orientation='h',color='Importe Total',color_continuous_scale=[[0,'#E8F5E9'],[1,'#0E6E3D']])
                fig.update_layout(**PLOTLY_LAYOUT,height=480,coloraxis_showscale=False,yaxis=dict(autorange="reversed"),xaxis=dict(tickformat='$,.0f'))
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown(section_header("📊","Estatus Operativo"),unsafe_allow_html=True)
            if 'Estatus Operativo' in df.columns:
                d=df['Estatus Operativo'].value_counts().reset_index(); d.columns=['E','C']
                fig=px.pie(d,values='C',names='E',hole=0.55,color_discrete_sequence=COLORS)
                fig.update_layout(**PLOTLY_LAYOUT,height=480)
                st.plotly_chart(fig,use_container_width=True)
        st.markdown(section_header("💵","Pagado vs Por Pagar"),unsafe_allow_html=True)
        if all(c in df.columns for c in ['Proyecto / Obra','Total Pagado','Por pagar']):
            d=df.groupby('Proyecto / Obra')[['Total Pagado','Por pagar']].sum().reset_index().nlargest(15,'Total Pagado')
            fig=go.Figure()
            fig.add_trace(go.Bar(x=d['Proyecto / Obra'],y=d['Total Pagado'],name='Pagado',marker_color='#0E6E3D'))
            fig.add_trace(go.Bar(x=d['Proyecto / Obra'],y=d['Por pagar'],name='Por Pagar',marker_color='#C0392B'))
            fig.update_layout(**PLOTLY_LAYOUT,barmode='stack',height=400,xaxis_tickangle=-45,yaxis=dict(tickformat='$,.0f',showgrid=True,gridcolor='#F0F0F0'))
            st.plotly_chart(fig,use_container_width=True)
    render_module("Contratos One Team","contratos",[("Importe Total","Importe Total",""),("Pagado","Total Pagado","green"),("Por Pagar","Por pagar","red")],
        [("Estatus Operativo","Est. Operativo"),("Estatus Cierre","Est. Cierre")],ch,
        ['ID Folio Contrato','CR','Proyecto / Obra','Importe Total','Estatus Operativo','Estatus Cierre','Total Pagado','Por pagar'])

# ═══ OBRA MENOR ═══
elif modulo == "🔧  Obra Menor":
    def ch(df):
        c1,c2=st.columns(2)
        with c1:
            st.markdown(section_header("📊","Por Tipo"),unsafe_allow_html=True)
            if 'PROYECTO' in df.columns:
                d=df['PROYECTO'].value_counts().reset_index(); d.columns=['P','C']
                fig=px.pie(d,values='C',names='P',hole=0.5,color_discrete_sequence=COLORS)
                fig.update_layout(**PLOTLY_LAYOUT,height=420); st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown(section_header("👤","Asignación"),unsafe_allow_html=True)
            if 'ASIGNADO_A' in df.columns:
                d=df['ASIGNADO_A'].value_counts().head(12).reset_index(); d.columns=['A','C']
                fig=px.bar(d,x='C',y='A',orientation='h',color='C',color_continuous_scale=[[0,'#FFF3E0'],[1,'#D4721A']])
                fig.update_layout(**PLOTLY_LAYOUT,height=420,coloraxis_showscale=False,yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig,use_container_width=True)
        st.markdown(section_header("📈","Presupuesto vs Cierre"),unsafe_allow_html=True)
        if all(c in df.columns for c in ['SUCURSAL','PRESUPUESTO_INICIAL','IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL']):
            d=df[['SUCURSAL','PRESUPUESTO_INICIAL','IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL']].dropna().nlargest(20,'PRESUPUESTO_INICIAL')
            fig=go.Figure()
            fig.add_trace(go.Bar(x=d['SUCURSAL'],y=d['PRESUPUESTO_INICIAL'],name='Presupuesto',marker_color='#004481'))
            fig.add_trace(go.Bar(x=d['SUCURSAL'],y=d['IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL'],name='Cierre',marker_color='#00A9E0'))
            fig.update_layout(**PLOTLY_LAYOUT,barmode='group',height=420,xaxis_tickangle=-45,yaxis=dict(tickformat='$,.0f',showgrid=True,gridcolor='#F0F0F0'))
            st.plotly_chart(fig,use_container_width=True)
    render_module("Obra Menor","obra_menor",[("Presupuesto","PRESUPUESTO_INICIAL",""),("Cierre","IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL","orange"),("Pagado","Total Pagado","green")],
        [("PROYECTO","Proyecto"),("ESTATUS_OPERACIÓN REAL","Est. Operación"),("ASIGNADO_A","Asignado a")],ch,
        ['ID_PROYECTO','SUCURSAL','PROYECTO','ASIGNADO_A','ESTATUS_OPERACIÓN REAL','PRESUPUESTO_INICIAL','IMPORTE_DE_CIERRE_ADMINISTRATIVO_PARCIAL','Total Pagado','VARIACIÓN_PRESUPUESTAL'])

# ═══ FACTURACIÓN ═══
elif modulo == "💰  Facturación 2025":
    def ch(df):
        c1,c2=st.columns(2)
        with c1:
            st.markdown(section_header("📈","Mensual"),unsafe_allow_html=True)
            if 'Fecha' in df.columns:
                d=df.dropna(subset=['Fecha']).copy(); d['M']=d['Fecha'].dt.to_period('M').astype(str)
                m=d.groupby('M').agg(T=('Total (MXN)','sum'),C=('NO.','count')).reset_index()
                fig=make_subplots(specs=[[{"secondary_y":True}]])
                fig.add_trace(go.Bar(x=m['M'],y=m['T'],name='Total',marker=dict(color=m['T'],colorscale=[[0,'#004481'],[1,'#00A9E0']])),secondary_y=False)
                fig.add_trace(go.Scatter(x=m['M'],y=m['C'],name='#',line=dict(color='#C0392B',width=3),mode='lines+markers'),secondary_y=True)
                fig.update_layout(**PLOTLY_LAYOUT,height=420); fig.update_yaxes(tickformat="$,.0f",secondary_y=False)
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown(section_header("📊","Estatus"),unsafe_allow_html=True)
            if 'Estatus Comprobante' in df.columns:
                d=df['Estatus Comprobante'].value_counts().reset_index(); d.columns=['E','C']
                fig=px.pie(d,values='C',names='E',hole=0.55,color_discrete_sequence=COLORS)
                fig.update_layout(**PLOTLY_LAYOUT,height=420); st.plotly_chart(fig,use_container_width=True)
    render_module("Facturación 2025","facturacion_2025",[("Subtotal","Subtotal (MXN)",""),("Impuestos","Impuestos (MXN)","orange"),("Total","Total (MXN)","green")],
        [("Estatus Comprobante","Estatus"),("FDP","Forma de Pago")],ch,
        ['FDP','Fecha','NO.','Razón social','Estatus Comprobante','Subtotal (MXN)','Total (MXN)','ORDEN DE COMPRA'])

# ═══ PREFACTURAS ═══
elif modulo == "📄  Prefacturas":
    def ch(df):
        c1,c2=st.columns(2)
        with c1:
            st.markdown(section_header("💰","Top por Monto"),unsafe_allow_html=True)
            if 'Proyecto / Obra' in df.columns:
                t=df.nlargest(15,'Total')[['Proyecto / Obra','Total']].dropna()
                fig=px.bar(t,x='Total',y='Proyecto / Obra',orientation='h',color='Total',color_continuous_scale=[[0,'#00A9E0'],[1,'#004481']])
                fig.update_layout(**PLOTLY_LAYOUT,height=450,coloraxis_showscale=False,yaxis=dict(autorange="reversed"),xaxis=dict(tickformat='$,.0f'))
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown(section_header("📊","Estatus"),unsafe_allow_html=True)
            if 'Estatus' in df.columns:
                d=df['Estatus'].value_counts().reset_index(); d.columns=['E','C']
                fig=px.pie(d,values='C',names='E',hole=0.55,color_discrete_sequence=COLORS)
                fig.update_layout(**PLOTLY_LAYOUT,height=450); st.plotly_chart(fig,use_container_width=True)
    render_module("Control de Prefacturas","prefacturas",[("Sin IVA","Monto (sin IVA)",""),("IVA","IVA","orange"),("Total","Total","green")],
        [("Estatus","Estatus")],ch,
        ['Folio Interno','Folio Pre Factura','CR','Proyecto / Obra','Fecha solicitud','Monto (sin IVA)','Total','Estatus','¿Se emitió factura?','Folio factura'])

# ═══ FIANZAS ═══
elif modulo == "🛡️  Fianzas":
    def ch(df):
        c1,c2=st.columns(2)
        with c1:
            st.markdown(section_header("💰","Montos"),unsafe_allow_html=True)
            if 'Proyecto' in df.columns and 'Monto de contrato' in df.columns:
                t=df.nlargest(15,'Monto de contrato')[['Proyecto','Monto de contrato']].dropna()
                fig=px.bar(t,x='Monto de contrato',y='Proyecto',orientation='h',color='Monto de contrato',color_continuous_scale=[[0,'#00A9E0'],[1,'#004481']])
                fig.update_layout(**PLOTLY_LAYOUT,height=400,coloraxis_showscale=False,yaxis=dict(autorange="reversed"),xaxis=dict(tickformat='$,.0f'))
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown(section_header("🏢","Afianzadoras"),unsafe_allow_html=True)
            if 'Afianzadora' in df.columns:
                d=df['Afianzadora'].value_counts().reset_index(); d.columns=['A','C']
                fig=px.pie(d,values='C',names='A',hole=0.55,color_discrete_sequence=COLORS)
                fig.update_layout(**PLOTLY_LAYOUT,height=400); st.plotly_chart(fig,use_container_width=True)
    render_module("Control de Fianzas","fianzas",[("Monto Contrato","Monto de contrato",""),("Garantizado","Monto Garantizado Fianza","green")],
        [("Estatus Expedición","Expedición"),("Estatus Vigencia","Vigencia")],ch,
        ['CR','Proyecto','Anexo de Obra','Afianzadora','No. Fianza','Monto de contrato','Monto Garantizado Fianza','Estatus Expedición','Vencimiento','Estatus Vigencia'])

# ═══ FACTURAS ADQUIRA ═══
elif modulo == "📊  Facturas Adquira":
    def ch(df):
        c1,c2=st.columns(2)
        with c1:
            st.markdown(section_header("📊","Por Categoría"),unsafe_allow_html=True)
            if 'CATEGORIA' in df.columns:
                d=df.groupby('CATEGORIA')['TOTAL FACTURA'].sum().reset_index().sort_values('TOTAL FACTURA',ascending=False)
                fig=px.bar(d,x='TOTAL FACTURA',y='CATEGORIA',orientation='h',color='TOTAL FACTURA',color_continuous_scale=[[0,'#00A9E0'],[1,'#004481']])
                fig.update_layout(**PLOTLY_LAYOUT,height=400,coloraxis_showscale=False,yaxis=dict(autorange="reversed"),xaxis=dict(tickformat='$,.0f'))
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown(section_header("📈","Estado"),unsafe_allow_html=True)
            if 'ESTADO' in df.columns:
                d=df['ESTADO'].value_counts().reset_index(); d.columns=['E','C']
                fig=px.pie(d,values='C',names='E',hole=0.55,color_discrete_sequence=COLORS)
                fig.update_layout(**PLOTLY_LAYOUT,height=400); st.plotly_chart(fig,use_container_width=True)
    render_module("Facturas Adquira","facturas_adquira",[("Base Imponible","BASE IMPONIBLE",""),("Impuestos","TOTAL IMPUESTOS","orange"),("Total","TOTAL FACTURA","green")],
        [("CATEGORIA","Categoría"),("ESTADO","Estado")],ch,
        ['NÚMERO','FECHA FACTURA','PEDIDO','CATEGORIA','PROYECTO RELACIONADO','BASE IMPONIBLE','TOTAL IMPUESTOS','TOTAL FACTURA','ESTADO'])

# ═══ PROYECTOS 2024 ═══
elif modulo == "📁  Proyectos 2024":
    def ch(df):
        c1,c2=st.columns(2)
        with c1:
            st.markdown(section_header("📊","Estatus"),unsafe_allow_html=True)
            if 'Estatus' in df.columns:
                d=df['Estatus'].value_counts().reset_index(); d.columns=['E','C']
                fig=px.pie(d,values='C',names='E',hole=0.55,color_discrete_sequence=COLORS)
                fig.update_layout(**PLOTLY_LAYOUT,height=400); st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown(section_header("💰","Top Importe"),unsafe_allow_html=True)
            if 'Sucursal' in df.columns:
                t=df.nlargest(15,'Importe de cierre')[['Sucursal','Importe de cierre']].dropna()
                fig=px.bar(t,x='Importe de cierre',y='Sucursal',orientation='h',color='Importe de cierre',color_continuous_scale=[[0,'#E8F5E9'],[1,'#0E6E3D']])
                fig.update_layout(**PLOTLY_LAYOUT,height=400,coloraxis_showscale=False,yaxis=dict(autorange="reversed"),xaxis=dict(tickformat='$,.0f'))
                st.plotly_chart(fig,use_container_width=True)
    render_module("Proyectos 2024","proyectos_2024",[("Cierre","Importe de cierre",""),("Pagado","Total Pagado","green"),("Por Pagar","Por pagar","red")],
        [("Estatus","Estatus")],ch,
        ['Llave comité /Clave UDA','CR','Sucursal','Proyecto','Importe de cierre','Asignado a','Estatus','Días transcurridos','Total Pagado','Por pagar'])

# ═══ EXPLORADOR ═══
elif modulo == "🗂️  Explorador":
    st.markdown('<div class="hero-kpi" style="padding:18px 28px;"><h4>EXPLORADOR DE DATOS</h4><h1>Análisis libre</h1><p>Navega, filtra y descarga cualquier hoja</p></div>', unsafe_allow_html=True)
    sm={'📋 Órdenes':'ordenes','📑 Contratos':'contratos','🔧 Obra Menor':'obra_menor','💰 Facturación':'facturacion_2025','📄 Prefacturas':'prefacturas','🛡️ Fianzas':'fianzas','📊 Adquira':'facturas_adquira','📁 Proy 2024':'proyectos_2024'}
    av={k:v for k,v in sm.items() if v in sheets}
    sel=st.selectbox("Hoja",list(av.keys()))
    if sel:
        k=av[sel]; df=sheets[k].copy()
        st.markdown(f'<div class="kpi-grid">{kpi_card("Filas",fmt_int(len(df)))}{kpi_card("Columnas",fmt_int(len(df.columns)),"","green")}</div>',unsafe_allow_html=True)
        s=st.text_input("🔎 Buscar","")
        if s:
            mask=df.astype(str).apply(lambda x:x.str.contains(s,case=False,na=False)).any(axis=1); df=df[mask]
            st.info(f"{len(df)} encontrados")
        nc=df.select_dtypes(include=[np.number]).columns.tolist()
        if nc:
            st.markdown(section_header("📊","Análisis Rápido"),unsafe_allow_html=True)
            sc=st.selectbox("Columna",nc)
            c1,c2=st.columns([2,1])
            with c1:
                fig=px.histogram(df,x=sc,nbins=30,color_discrete_sequence=['#004481'])
                fig.update_layout(**PLOTLY_LAYOUT,height=300); st.plotly_chart(fig,use_container_width=True)
            with c2: st.dataframe(df[sc].describe().round(2),use_container_width=True)
        st.markdown(section_header("📋","Datos",f"{len(df)} reg."),unsafe_allow_html=True)
        st.dataframe(df,use_container_width=True,height=500,hide_index=True)
        st.download_button("📥 CSV",df.to_csv(index=False).encode('utf-8'),f"{k}.csv","text/csv")
