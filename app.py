import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency

# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="💸 Money Moves: Dashboard Keuangan",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS (GEN Z AESTHETIC: Glassmorphism + Neon)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Inter:wght@400;500;600&display=swap');
    
    /* Background & Base Font */
    .stApp { 
        background-color: #0b0f19; 
        font-family: 'Inter', sans-serif; 
    }
    h1, h2, h3, h4 { font-family: 'Outfit', sans-serif; letter-spacing: -0.02em; }
    
    /* Glassmorphism Metric Cards */
    [data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 16px;
        padding: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    [data-testid="metric-container"]:hover {
        border-color: rgba(99, 102, 241, 0.6);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
        transform: translateY(-4px);
    }
    [data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 1.8rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Section Titles with Neon Accent */
    .section-title {
        color: #e2e8f0;
        font-size: 1.15rem;
        font-weight: 700;
        border-left: 4px solid #818cf8;
        padding-left: 12px;
        margin: 24px 0 16px 0;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sidebar Glass Effect */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(51, 65, 85, 0.5);
        backdrop-filter: blur(10px);
    }
    [data-testid="stSidebar"] * { color: #cbd5e1; }
    [data-testid="stSidebar"] h2 { color: #f8fafc; font-family: 'Outfit', sans-serif; }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #6366f1; }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid rgba(51, 65, 85, 0.5);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #94a3b8;
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Outfit', sans-serif;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #818cf8) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    /* Insight Box (TL;DR) */
    .insight-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(34, 211, 238, 0.05));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 16px 0;
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Plotly Overrides */
    .js-plotly-plot .plotly { border-radius: 16px; overflow: hidden; }
    hr { border-color: rgba(51, 65, 85, 0.5); margin: 32px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Analisis_Statistika.csv")
    df.columns = [
        "timestamp", "jenis_kelamin", "prodi", "semester",
        "uang_saku", "total_pengeluaran",
        "pengeluaran_makan", "pengeluaran_transport",
        "pengeluaran_hiburan", "pengeluaran_kuliah",
        "kehabisan_uang", "budgeting",
        "faktor_membengkak", "frekuensi_belanja_online"
    ]
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True, errors="coerce")
    return df

df = load_data()

# ─────────────────────────────────────────────
# ORDER KATEGORIS & TEMA
# ─────────────────────────────────────────────
ORDER_UANG_SAKU = [
    "< Rp 500.000", "Rp 500.000 - Rp 1.000.000", 
    "Rp 1.000.001 - Rp 1.500.000", "> Rp 1.500.001"
]
ORDER_TOTAL_PENGELUARAN = [
    "< Rp 500.000", "Rp 500.000 - Rp 700.000", 
    "Rp 700.001 - Rp 1.000.000", "> Rp 1.000.001"
]

WARNA_UTAMA = ["#818cf8", "#22d3ee", "#fbbf24", "#34d399", "#fb7185", "#c084fc"]
BG_PLOT = "#111827"
PAPER_BG = "#0b0f19"
FONT_COLOR = "#f1f5f9"
GRID_COLOR = "#1e293b"

def style_fig(fig):
    """Tema gelap konsisten + sentuhan modern untuk semua chart Plotly."""
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=BG_PLOT,
        font=dict(color=FONT_COLOR, family="Inter, sans-serif"),
        margin=dict(t=40, b=30, l=20, r=20),
        hovermode="closest",
        hoverlabel=dict(bgcolor="#1e293b", font_size=12, font_family="Inter"),
        legend=dict(
            bgcolor="rgba(30, 41, 59, 0.8)",
            bordercolor="#334155",
            borderwidth=1,
            font=dict(size=11)
        ),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, showline=False)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, showline=False)
    return fig

def insight_box(text):
    st.markdown(f'<div class="insight-box">💡 <strong>TL;DR:</strong> {text}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR – FILTER
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filter Data")
    st.markdown("---")
    
    gender_options = ["Semua"] + sorted(df["jenis_kelamin"].unique().tolist())
    gender_filter = st.selectbox("👤 Jenis Kelamin", gender_options)
    
    uang_saku_options = ["Semua"] + ORDER_UANG_SAKU
    uang_saku_filter = st.selectbox("💵 Range Uang Saku", uang_saku_options)
    
    kehabisan_options = ["Semua", "Ya", "Tidak"]
    kehabisan_filter = st.selectbox("🚨 Pernah Kehabisan Uang?", kehabisan_options)
    
    budgeting_options = ["Semua", "Ya", "Tidak"]
    budgeting_filter = st.selectbox("🧠 Rutin Budgeting?", budgeting_options)
    
    st.markdown("---")
    st.markdown(f"**👥 Total Squad:** `{len(df)}` orang")
    st.markdown("**📂 Sumber:** Survei Analisis Statistika 2026")

# ─────────────────────────────────────────────
# TERAPKAN FILTER
# ─────────────────────────────────────────────
filtered = df.copy()
if gender_filter != "Semua":
    filtered = filtered[filtered["jenis_kelamin"] == gender_filter]
if uang_saku_filter != "Semua":
    filtered = filtered[filtered["uang_saku"] == uang_saku_filter]
if kehabisan_filter != "Semua":
    filtered = filtered[filtered["kehabisan_uang"] == kehabisan_filter]
if budgeting_filter != "Semua":
    filtered = filtered[filtered["budgeting"] == budgeting_filter]

n = len(filtered)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="padding: 16px 0 24px 0;">
    <h1 style="color:#f8fafc; font-size:2.2rem; font-weight:800; margin:0; background: linear-gradient(90deg, #818cf8, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        💸 Money Moves: Dashboard Keuangan Mahasiswa
    </h1>
    <p style="color:#94a3b8; margin:8px 0 0 0; font-size:1rem; font-weight:500;">
        Analisis pola pengeluaran, red flags, dan green flags finansial mahasiswa Sains Data.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI CARDS (Gen Z Copywriting)
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

pct_kehabisan = round(filtered[filtered["kehabisan_uang"] == "Ya"].shape[0] / n * 100, 1) if n else 0
pct_budgeting = round(filtered[filtered["budgeting"] == "Ya"].shape[0] / n * 100, 1) if n else 0
pct_belanja_sering = round(filtered[filtered["frekuensi_belanja_online"] == "3 kali atau lebih"].shape[0] / n * 100, 1) if n else 0
modus_pengeluaran = str(filtered["total_pengeluaran"].mode()[0]) if n else "-"
modus_uang_saku = str(filtered["uang_saku"].mode()[0]) if n else "-"

k1.metric("👥 Total Squad", f"{n} orang")
k2.metric("🚨 Sering Bokek?", f"{pct_kehabisan}%")
k3.metric("🧠 Ada Budgeting?", f"{pct_budgeting}%")
k4.metric("🛒 Shopee/Tokped Addict", f"{pct_belanja_sering}%")
k5.metric("💸 Money Drain", modus_pengeluaran.replace("Rp ", "Rp\u00A0"))

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB NAVIGASI
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 Siapa Kita? (Demografi)",
    "💸 Ke Mana Larinya Duit?",
    "🧠 Vibe Check Keuangan",
    "🔬 Deep Dive & Data Mentah",
])

# ══════════════════════════════════════════════
# TAB 1 – DEMOGRAFI & DISTRIBUSI
# ══════════════════════════════════════════════
with tab1:
    insight_box("Mayoritas responden didominasi oleh satu gender tertentu dengan range uang saku yang cenderung pas-pasan namun tetap bisa survive!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-title">Distribusi Jenis Kelamin</p>', unsafe_allow_html=True)
        gender_cnt = filtered["jenis_kelamin"].value_counts().reset_index()
        gender_cnt.columns = ["Jenis Kelamin", "Jumlah"]
        fig = px.pie(
            gender_cnt, names="Jenis Kelamin", values="Jumlah",
            color_discrete_sequence=WARNA_UTAMA, hole=0.5,
        )
        fig.update_traces(textfont_size=13, textinfo="percent+label", hovertemplate="<b>%{label}</b><br>Jumlah: %{value} orang<extra></extra>")
        fig.update_layout(showlegend=False)
        style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Distribusi Uang Saku Bulanan</p>', unsafe_allow_html=True)
        uang_cnt = filtered["uang_saku"].value_counts().reindex(ORDER_UANG_SAKU, fill_value=0).reset_index()
        uang_cnt.columns = ["Uang Saku", "Jumlah"]
        fig2 = px.bar(
            uang_cnt, x="Uang Saku", y="Jumlah",
            color="Jumlah", color_continuous_scale="Blues",
            text="Jumlah",
        )
        fig2.update_traces(textposition="outside", textfont_color=FONT_COLOR, marker=dict(corner_radius=6))
        fig2.update_coloraxes(showscale=False)
        style_fig(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-title">Uang Saku Berdasarkan Jenis Kelamin</p>', unsafe_allow_html=True)
    cross = pd.crosstab(filtered["uang_saku"], filtered["jenis_kelamin"]).reindex(ORDER_UANG_SAKU, fill_value=0)
    fig3 = go.Figure()
    for i, col_name in enumerate(cross.columns):
        fig3.add_trace(go.Bar(
            name=col_name, x=cross.index, y=cross[col_name],
            marker_color=WARNA_UTAMA[i], marker=dict(corner_radius=4),
            text=cross[col_name], textposition="auto",
            hovertemplate=f"<b>{col_name}</b><br>Jumlah: %{{y}}<extra></extra>"
        ))
    fig3.update_layout(barmode="group", xaxis_title="Range Uang Saku", yaxis_title="Jumlah Mahasiswa")
    style_fig(fig3)
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 – POLA PENGELUARAN
# ══════════════════════════════════════════════
with tab2:
    insight_box("Faktor utama pembengkakan budget biasanya bukan karena kebutuhan primer, melainkan gaya hidup dan keinginan mendadak (FOMO).")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-title">Total Pengeluaran Bulanan</p>', unsafe_allow_html=True)
        tot_cnt = filtered["total_pengeluaran"].value_counts().reindex(ORDER_TOTAL_PENGELUARAN, fill_value=0).reset_index()
        tot_cnt.columns = ["Total Pengeluaran", "Jumlah"]
        fig = px.bar(
            tot_cnt, x="Total Pengeluaran", y="Jumlah",
            color="Total Pengeluaran", color_discrete_sequence=WARNA_UTAMA,
            text="Jumlah",
        )
        fig.update_traces(textposition="outside", textfont_color=FONT_COLOR, marker=dict(corner_radius=6), showlegend=False)
        style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Faktor Pengeluaran Membengkak 📈</p>', unsafe_allow_html=True)
        faktor_cnt = filtered["faktor_membengkak"].value_counts().reset_index()
        faktor_cnt.columns = ["Faktor", "Jumlah"]
        faktor_cnt["Faktor_short"] = faktor_cnt["Faktor"].str.extract(r'^([^(]+)').iloc[:, 0].str.strip()
        
        fig2 = px.bar(
            faktor_cnt, y="Faktor_short", x="Jumlah",
            orientation="h", color="Jumlah",
            color_continuous_scale="Purples", text="Jumlah",
        )
        fig2.update_traces(textposition="outside", textfont_color=FONT_COLOR, marker=dict(corner_radius=6))
        fig2.update_coloraxes(showscale=False)
        fig2.update_layout(yaxis_title=" ", xaxis_title="Jumlah Responden")
        style_fig(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-title">Breakdown Kategori Pengeluaran</p>', unsafe_allow_html=True)
    col_makan = filtered["pengeluaran_makan"].value_counts()
    col_transport = filtered["pengeluaran_transport"].value_counts()
    col_hiburan = filtered["pengeluaran_hiburan"].value_counts()
    col_kuliah = filtered["pengeluaran_kuliah"].value_counts()

    all_cats = set(col_makan.index) | set(col_transport.index) | set(col_hiburan.index) | set(col_kuliah.index)
    breakdown_df = pd.DataFrame({
        "Makan 🍔": col_makan,
        "Transport 🛵": col_transport,
        "Hiburan 🎮": col_hiburan,
        "Kuliah 📚": col_kuliah,
    }).fillna(0).reset_index().rename(columns={"index": "Kategori"})
    
    breakdown_melt = breakdown_df.melt(id_vars="Kategori", var_name="Jenis", value_name="Jumlah")

    fig3 = px.bar(
        breakdown_melt, x="Kategori", y="Jumlah", color="Jenis",
        barmode="group", color_discrete_sequence=WARNA_UTAMA,
        text="Jumlah",
    )
    fig3.update_traces(textposition="outside", textfont_color=FONT_COLOR, marker=dict(corner_radius=4))
    fig3.update_layout(xaxis_title="Range Pengeluaran", yaxis_title="Jumlah Mahasiswa")
    style_fig(fig3)
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 – PERILAKU KEUANGAN
# ══════════════════════════════════════════════
with tab3:
    insight_box("Korelasi negatif yang kuat: Mahasiswa yang rutin budgeting memiliki persentase 'bokek' yang jauh lebih rendah. Budgeting is a green flag! 🟢")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-title">Pernah Kehabisan Uang? 🚨</p>', unsafe_allow_html=True)
        kh_cnt = filtered["kehabisan_uang"].value_counts().reset_index()
        kh_cnt.columns = ["Status", "Jumlah"]
        fig = px.pie(kh_cnt, names="Status", values="Jumlah", hole=0.6,
                     color="Status",
                     color_discrete_map={"Ya": "#fb7185", "Tidak": "#34d399"})
        fig.update_traces(textfont_size=14, textinfo="percent+label", hovertemplate="<b>%{label}</b><br>%{value} orang<extra></extra>")
        style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">Rutin Melakukan Budgeting? 🧠</p>', unsafe_allow_html=True)
        bd_cnt = filtered["budgeting"].value_counts().reset_index()
        bd_cnt.columns = ["Status", "Jumlah"]
        fig2 = px.pie(bd_cnt, names="Status", values="Jumlah", hole=0.6,
                      color="Status",
                      color_discrete_map={"Ya": "#818cf8", "Tidak": "#fbbf24"})
        fig2.update_traces(textfont_size=14, textinfo="percent+label", hovertemplate="<b>%{label}</b><br>%{value} orang<extra></extra>")
        style_fig(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-title">Hubungan Budgeting vs Kehabisan Uang (Stacked %)</p>', unsafe_allow_html=True)
    cross_bk = pd.crosstab(filtered["budgeting"], filtered["kehabisan_uang"])
    cross_bk_pct = (cross_bk.div(cross_bk.sum(axis=1), axis=0) * 100).round(1)

    fig3 = go.Figure()
    colors_map = {"Ya": "#fb7185", "Tidak": "#34d399"}
    for col_name in cross_bk_pct.columns:
        fig3.add_trace(go.Bar(
            name=f"Kehabisan: {col_name}",
            x=cross_bk_pct.index,
            y=cross_bk_pct[col_name],
            marker_color=colors_map.get(col_name, WARNA_UTAMA[0]),
            text=cross_bk_pct[col_name].map(lambda v: f"{v:.1f}%"),
            textposition="inside",
            hovertemplate="<b>%{x}</b><br>%{y}%<extra></extra>"
        ))
    fig3.update_layout(barmode="relative", xaxis_title="Melakukan Budgeting", yaxis_title="Persentase (%)")
    style_fig(fig3)
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 – ANALISIS LANJUTAN
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">📋 Tabel Frekuensi Interaktif</p>', unsafe_allow_html=True)
    col_select = st.selectbox("Pilih Variabel untuk Di-bedah:", [
        "uang_saku", "total_pengeluaran", "pengeluaran_makan",
        "pengeluaran_transport", "pengeluaran_hiburan", "pengeluaran_kuliah",
        "kehabisan_uang", "budgeting", "faktor_membengkak", "frekuensi_belanja_online",
        "jenis_kelamin",
    ])
    
    freq_df = filtered[col_select].value_counts().reset_index()
    freq_df.columns = ["Kategori", "Frekuensi"]
    freq_df["Persentase"] = (freq_df["Frekuensi"] / n * 100).round(2).astype(str) + "%"
    freq_df["Kumulatif"] = freq_df["Frekuensi"].cumsum()
    modus_val = freq_df.iloc[0]["Kategori"]

    col_m, col_t = st.columns([2, 1])
    with col_m:
        fig_f = px.bar(
            freq_df, x="Kategori", y="Frekuensi",
            color="Frekuensi", color_continuous_scale="Viridis",
            text="Persentase",
        )
        fig_f.update_traces(textposition="outside", textfont_color=FONT_COLOR, marker=dict(corner_radius=6))
        fig_f.update_coloraxes(showscale=False)
        style_fig(fig_f)
        st.plotly_chart(fig_f, use_container_width=True)
    with col_t:
        st.markdown(f"**🏆 Modus:**<br>`{modus_val}`")
        st.markdown(f"**👥 Sample:**<br>`{n}` orang")
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(freq_df, use_container_width=True, hide_index=True, height=300)

    st.markdown("---")

    # Heatmap Korelasi Kategoris (Cramér's V) - *Bug syntax asli diperbaiki di sini*
    st.markdown('<p class="section-title">🔥 Heatmap Asosiasi Antar Variabel (Cramér\'s V)</p>', unsafe_allow_html=True)
    st.caption("Cramér's V: 0 = tidak ada hubungan, 1 = hubungan sempurna. Semakin merah, semakin kuat korelasinya.")

    cat_cols = [
        "uang_saku", "total_pengeluaran", "pengeluaran_makan",
        "pengeluaran_transport", "pengeluaran_hiburan", "pengeluaran_kuliah",
        "kehabisan_uang", "budgeting", "faktor_membengkak",
        "frekuensi_belanja_online", "jenis_kelamin",
    ]
    cat_labels = [
        "Uang Saku", "Total Keluar", "Makan",
        "Transport", "Hiburan", "Kuliah",
        "Bokek", "Budgeting", "Faktor Bengkak",
        "Belanja Online", "Gender",
    ]

    def cramers_v(x, y):
        confusion_matrix = pd.crosstab(x, y)
        chi2 = chi2_contingency(confusion_matrix)[0]
        n_obs = confusion_matrix.sum().sum()
        phi2 = chi2 / n_obs
        r, k = confusion_matrix.shape
        phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n_obs - 1))
        rcorr = r - ((r - 1) ** 2) / (n_obs - 1)
        kcorr = k - ((k - 1) ** 2) / (n_obs - 1)
        denom = min((kcorr - 1), (rcorr - 1))
        return np.sqrt(phi2corr / denom) if denom > 0 else 0

    if n >= 5:
        matrix = np.zeros((len(cat_cols), len(cat_cols)))
        for i, c1 in enumerate(cat_cols):
            for j, c2 in enumerate(cat_cols):
                if i == j:
                    matrix[i][j] = 1.0
                elif i < j:
                    try:
                        v = cramers_v(filtered[c1], filtered[c2])
                    except Exception:
                        v = 0.0
                    matrix[i][j] = v
                    matrix[j][i] = v

        fig_heat = go.Figure(data=go.Heatmap(
            z=np.round(matrix, 2),
            x=cat_labels, y=cat_labels,
            colorscale="Magma", # Magma lebih estetik untuk dark mode
            zmin=0, zmax=1,
            text=np.round(matrix, 2),
            texttemplate="%{text}",
            textfont={"size": 10, "color": "white"},
            hovertemplate="<b>%{y}</b> & <b>%{x}</b><br>Skor: %{z}<extra></extra>"
        ))
        fig_heat.update_layout(
            height=550,
            xaxis=dict(tickangle=-45, tickfont=dict(size=11)),
            yaxis=dict(tickfont=dict(size=11)),
        )
        style_fig(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("⚠️ Data terlalu sedikit untuk menghitung Cramér's V. Hapus filter di sidebar untuk melihat heatmap.")

    st.markdown("---")

    # Tabel data mentah
    st.markdown('<p class="section-title">📄 Data Mentah (Filtered)</p>', unsafe_allow_html=True)
    with st.expander("👀 Intip Data Mentah"):
        st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=400)
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV (Filtered)",
            data=csv,
            file_name="money_moves_filtered.csv",
            mime="text/csv",
        )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#475569; font-size:0.8rem; font-family: Inter, sans-serif;'>"
    "Dibuat dengan 💜 dan ☕ · Dashboard Analisis Keuangan Mahasiswa · Sains Data · 2026"
    "</p>",
    unsafe_allow_html=True,
)
