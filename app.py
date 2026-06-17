import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Analisis Keuangan Mahasiswa",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Background utama */
    .stApp { background-color: #0f172a; }
    
    /* Kartu metrik */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Header section */
    .section-title {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 600;
        border-left: 3px solid #6366f1;
        padding-left: 10px;
        margin: 20px 0 12px 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0; }

    /* Divider */
    hr { border-color: #334155; }

    /* Plotly chart background override */
    .js-plotly-plot .plotly { border-radius: 12px; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #94a3b8;
        border-radius: 8px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6366f1 !important;
        color: white !important;
    }
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
# ORDER KATEGORIS (untuk sorting logis)
# ─────────────────────────────────────────────
ORDER_UANG_SAKU = [
    "< Rp 500.000",
    "Rp 500.000 - Rp 1.000.000",
    "Rp 1.000.001 - Rp 1.500.000",
    "> Rp 1.500.001",
]
ORDER_TOTAL_PENGELUARAN = [
    "< Rp 500.000",
    "Rp 500.000 - Rp 700.000",
    "Rp 700.001 - Rp 1.000.000",
    "> Rp 1.000.001",
]

WARNA_UTAMA = ["#6366f1", "#22d3ee", "#f59e0b", "#10b981", "#f43f5e", "#a78bfa"]
BG_PLOT = "#1e293b"
PAPER_BG = "#0f172a"
FONT_COLOR = "#e2e8f0"
GRID_COLOR = "#334155"

def style_fig(fig):
    """Terapkan tema gelap konsisten ke semua chart Plotly."""
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=BG_PLOT,
        font=dict(color=FONT_COLOR, family="Inter, sans-serif"),
        margin=dict(t=40, b=30, l=20, r=20),
        legend=dict(
            bgcolor="#1e293b",
            bordercolor="#334155",
            borderwidth=1,
        ),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    return fig

# ─────────────────────────────────────────────
# SIDEBAR – FILTER
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filter Data")
    st.markdown("---")

    gender_options = ["Semua"] + sorted(df["jenis_kelamin"].unique().tolist())
    gender_filter = st.selectbox("👤 Jenis Kelamin", gender_options)

    uang_saku_options = ["Semua"] + ORDER_UANG_SAKU
    uang_saku_filter = st.selectbox("💵 Uang Saku", uang_saku_options)

    kehabisan_options = ["Semua", "Ya", "Tidak"]
    kehabisan_filter = st.selectbox("⚠️ Pernah Kehabisan Uang", kehabisan_options)

    budgeting_options = ["Semua", "Ya", "Tidak"]
    budgeting_filter = st.selectbox("📒 Melakukan Budgeting", budgeting_options)

    st.markdown("---")
    st.markdown(f"**Total Responden:** {len(df)}")
    st.markdown("**Sumber Data:** Survei Analisis Statistika")

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
<div style="padding: 24px 0 8px 0;">
    <h1 style="color:#f1f5f9; font-size:2rem; font-weight:800; margin:0;">
        💰 Dashboard Analisis Keuangan Mahasiswa
    </h1>
    <p style="color:#94a3b8; margin:6px 0 0 0; font-size:0.95rem;">
        Analisis pola pengeluaran dan perilaku keuangan mahasiswa Sains Data
    </p>
</div>
<hr>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

pct_kehabisan = round(filtered[filtered["kehabisan_uang"] == "Ya"].shape[0] / n * 100, 1) if n else 0
pct_budgeting = round(filtered[filtered["budgeting"] == "Ya"].shape[0] / n * 100, 1) if n else 0
pct_belanja_sering = round(filtered[filtered["frekuensi_belanja_online"] == "3 kali atau lebih"].shape[0] / n * 100, 1) if n else 0
modus_pengeluaran = filtered["total_pengeluaran"].mode()[0] if n else "-"
modus_uang_saku = filtered["uang_saku"].mode()[0] if n else "-"

k1.metric("👥 Responden", f"{n} orang")
k2.metric("⚠️ Kehabisan Uang", f"{pct_kehabisan}%")
k3.metric("📒 Pakai Budgeting", f"{pct_budgeting}%")
k4.metric("🛒 Sering Belanja Online", f"{pct_belanja_sering}%")
k5.metric("💸 Pengeluaran Dominan", modus_pengeluaran.replace("Rp ", "Rp\u00A0"))

st.markdown("")

# ─────────────────────────────────────────────
# TAB NAVIGASI
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Demografi & Distribusi",
    "💳 Pola Pengeluaran",
    "🔍 Perilaku Keuangan",
    "📈 Analisis Lanjutan",
    "🎲 Simulasi Monte Carlo",
])

# ══════════════════════════════════════════════
# TAB 1 – DEMOGRAFI & DISTRIBUSI
# ══════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns(2)

    # Distribusi Jenis Kelamin
    with col1:
        st.markdown('<p class="section-title">Distribusi Jenis Kelamin</p>', unsafe_allow_html=True)
        gender_cnt = filtered["jenis_kelamin"].value_counts().reset_index()
        gender_cnt.columns = ["Jenis Kelamin", "Jumlah"]
        fig = px.pie(
            gender_cnt, names="Jenis Kelamin", values="Jumlah",
            color_discrete_sequence=WARNA_UTAMA, hole=0.45,
        )
        fig.update_traces(textfont_size=13, textinfo="percent+label")
        fig.update_layout(showlegend=False)
        style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Distribusi Uang Saku
    with col2:
        st.markdown('<p class="section-title">Distribusi Uang Saku Bulanan</p>', unsafe_allow_html=True)
        uang_cnt = filtered["uang_saku"].value_counts().reindex(ORDER_UANG_SAKU, fill_value=0).reset_index()
        uang_cnt.columns = ["Uang Saku", "Jumlah"]
        fig2 = px.bar(
            uang_cnt, x="Uang Saku", y="Jumlah",
            color="Jumlah", color_continuous_scale="Viridis",
            text="Jumlah",
        )
        fig2.update_traces(textposition="outside", textfont_color=FONT_COLOR)
        fig2.update_coloraxes(showscale=False)
        style_fig(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # Uang Saku vs Jenis Kelamin
    st.markdown('<p class="section-title">Uang Saku Berdasarkan Jenis Kelamin</p>', unsafe_allow_html=True)
    cross = pd.crosstab(filtered["uang_saku"], filtered["jenis_kelamin"]).reindex(ORDER_UANG_SAKU, fill_value=0)
    fig3 = go.Figure()
    for i, col_name in enumerate(cross.columns):
        fig3.add_trace(go.Bar(
            name=col_name, x=cross.index, y=cross[col_name],
            marker_color=WARNA_UTAMA[i],
            text=cross[col_name], textposition="auto",
        ))
    fig3.update_layout(barmode="group", xaxis_title="Uang Saku", yaxis_title="Jumlah")
    style_fig(fig3)
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 – POLA PENGELUARAN
# ══════════════════════════════════════════════
with tab2:
    col1, col2 = st.columns(2)

    # Total Pengeluaran
    with col1:
        st.markdown('<p class="section-title">Total Pengeluaran Bulanan</p>', unsafe_allow_html=True)
        tot_cnt = filtered["total_pengeluaran"].value_counts().reindex(ORDER_TOTAL_PENGELUARAN, fill_value=0).reset_index()
        tot_cnt.columns = ["Total Pengeluaran", "Jumlah"]
        fig = px.bar(
            tot_cnt, x="Total Pengeluaran", y="Jumlah",
            color="Total Pengeluaran", color_discrete_sequence=WARNA_UTAMA,
            text="Jumlah",
        )
        fig.update_traces(textposition="outside", textfont_color=FONT_COLOR, showlegend=False)
        style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Faktor Membengkak
    with col2:
        st.markdown('<p class="section-title">Faktor Pengeluaran Membengkak</p>', unsafe_allow_html=True)
        faktor_cnt = filtered["faktor_membengkak"].value_counts().reset_index()
        faktor_cnt.columns = ["Faktor", "Jumlah"]
        # Potong label panjang
        faktor_cnt["Faktor_short"] = faktor_cnt["Faktor"].str.extract(r'^([^(]+)').iloc[:, 0].str.strip()
        fig2 = px.bar(
            faktor_cnt, y="Faktor_short", x="Jumlah",
            orientation="h", color="Jumlah",
            color_continuous_scale="Viridis", text="Jumlah",
        )
        fig2.update_traces(textposition="outside", textfont_color=FONT_COLOR)
        fig2.update_coloraxes(showscale=False)
        fig2.update_layout(yaxis_title="")
        style_fig(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # Breakdown kategori pengeluaran
    st.markdown('<p class="section-title">Perbandingan Kategori Pengeluaran</p>', unsafe_allow_html=True)
    col_makan = filtered["pengeluaran_makan"].value_counts()
    col_transport = filtered["pengeluaran_transport"].value_counts()
    col_hiburan = filtered["pengeluaran_hiburan"].value_counts()
    col_kuliah = filtered["pengeluaran_kuliah"].value_counts()

    all_cats = set(col_makan.index) | set(col_transport.index) | set(col_hiburan.index) | set(col_kuliah.index)
    breakdown_df = pd.DataFrame({
        "Makan": col_makan,
        "Transport": col_transport,
        "Hiburan": col_hiburan,
        "Kuliah": col_kuliah,
    }).fillna(0).reset_index().rename(columns={"index": "Kategori"})
    breakdown_melt = breakdown_df.melt(id_vars="Kategori", var_name="Jenis", value_name="Jumlah")

    fig3 = px.bar(
        breakdown_melt, x="Kategori", y="Jumlah", color="Jenis",
        barmode="group", color_discrete_sequence=WARNA_UTAMA,
        text="Jumlah",
    )
    fig3.update_traces(textposition="outside", textfont_color=FONT_COLOR)
    fig3.update_layout(xaxis_title="Range Pengeluaran", yaxis_title="Jumlah Mahasiswa")
    style_fig(fig3)
    st.plotly_chart(fig3, use_container_width=True)

    # Frekuensi belanja online
    st.markdown('<p class="section-title">Frekuensi Belanja Online</p>', unsafe_allow_html=True)
    belanja_cnt = filtered["frekuensi_belanja_online"].value_counts().reset_index()
    belanja_cnt.columns = ["Frekuensi", "Jumlah"]
    fig4 = px.pie(
        belanja_cnt, names="Frekuensi", values="Jumlah",
        color_discrete_sequence=WARNA_UTAMA, hole=0.45,
    )
    fig4.update_traces(textfont_size=13, textinfo="percent+label")
    style_fig(fig4)
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.plotly_chart(fig4, use_container_width=True)
    with col_b:
        st.markdown("")
        st.markdown("")
        freq_tbl = belanja_cnt.copy()
        freq_tbl["Persentase"] = (freq_tbl["Jumlah"] / n * 100).round(1).astype(str) + "%"
        st.dataframe(freq_tbl, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 3 – PERILAKU KEUANGAN
# ══════════════════════════════════════════════
with tab3:
    col1, col2 = st.columns(2)

    # Kehabisan uang
    with col1:
        st.markdown('<p class="section-title">Pernah Kehabisan Uang?</p>', unsafe_allow_html=True)
        kh_cnt = filtered["kehabisan_uang"].value_counts().reset_index()
        kh_cnt.columns = ["Status", "Jumlah"]
        fig = px.pie(kh_cnt, names="Status", values="Jumlah", hole=0.5,
                     color="Status",
                     color_discrete_map={"Ya": "#f43f5e", "Tidak": "#10b981"})
        fig.update_traces(textfont_size=13, textinfo="percent+label")
        style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Budgeting
    with col2:
        st.markdown('<p class="section-title">Melakukan Budgeting?</p>', unsafe_allow_html=True)
        bd_cnt = filtered["budgeting"].value_counts().reset_index()
        bd_cnt.columns = ["Status", "Jumlah"]
        fig2 = px.pie(bd_cnt, names="Status", values="Jumlah", hole=0.5,
                      color="Status",
                      color_discrete_map={"Ya": "#6366f1", "Tidak": "#f59e0b"})
        fig2.update_traces(textfont_size=13, textinfo="percent+label")
        style_fig(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # Hubungan Budgeting vs Kehabisan Uang
    st.markdown('<p class="section-title">Hubungan Budgeting vs Kehabisan Uang</p>', unsafe_allow_html=True)
    cross_bk = pd.crosstab(filtered["budgeting"], filtered["kehabisan_uang"])
    cross_bk_pct = (cross_bk.div(cross_bk.sum(axis=1), axis=0) * 100).round(1)

    fig3 = go.Figure()
    colors_map = {"Ya": "#f43f5e", "Tidak": "#10b981"}
    for col_name in cross_bk_pct.columns:
        fig3.add_trace(go.Bar(
            name=f"Kehabisan: {col_name}",
            x=cross_bk_pct.index,
            y=cross_bk_pct[col_name],
            marker_color=colors_map.get(col_name, WARNA_UTAMA[0]),
            text=cross_bk_pct[col_name].map(lambda v: f"{v:.1f}%"),
            textposition="inside",
        ))
    fig3.update_layout(
        barmode="stack",
        xaxis_title="Melakukan Budgeting",
        yaxis_title="Persentase (%)",
    )
    style_fig(fig3)
    st.plotly_chart(fig3, use_container_width=True)

    # Kehabisan uang per uang saku
    st.markdown('<p class="section-title">Kehabisan Uang Berdasarkan Uang Saku</p>', unsafe_allow_html=True)
    cross_us = pd.crosstab(
        filtered["uang_saku"], filtered["kehabisan_uang"]
    ).reindex(ORDER_UANG_SAKU, fill_value=0)
    cross_us_pct = (cross_us.div(cross_us.sum(axis=1), axis=0) * 100).round(1)

    fig4 = go.Figure()
    for col_name in cross_us_pct.columns:
        fig4.add_trace(go.Bar(
            name=f"Kehabisan: {col_name}",
            x=cross_us_pct.index,
            y=cross_us_pct[col_name],
            marker_color=colors_map.get(col_name, WARNA_UTAMA[0]),
            text=cross_us_pct[col_name].map(lambda v: f"{v:.1f}%"),
            textposition="inside",
        ))
    fig4.update_layout(
        barmode="stack",
        xaxis_title="Uang Saku",
        yaxis_title="Persentase (%)",
    )
    style_fig(fig4)
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 – ANALISIS LANJUTAN
# ══════════════════════════════════════════════
with tab4:
    # Tabel Frekuensi Lengkap
    st.markdown('<p class="section-title">📋 Tabel Frekuensi Semua Variabel</p>', unsafe_allow_html=True)
    col_select = st.selectbox("Pilih Kolom:", [
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
        fig_f.update_traces(textposition="outside", textfont_color=FONT_COLOR)
        fig_f.update_coloraxes(showscale=False)
        style_fig(fig_f)
        st.plotly_chart(fig_f, use_container_width=True)
    with col_t:
        st.markdown(f"**Modus:** `{modus_val}`")
        st.markdown(f"**Total Responden (filtered):** `{n}`")
        st.dataframe(freq_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Heatmap Korelasi Kategoris (Chi-square proxy via Cramér's V)
    st.markdown('<p class="section-title">🔥 Heatmap Asosiasi Antar Variabel (Cramér\'s V)</p>', unsafe_allow_html=True)

    from scipy.stats import chi2_contingency

    cat_cols = [
        "uang_saku", "total_pengeluaran", "pengeluaran_makan",
        "pengeluaran_transport", "pengeluaran_hiburan", "pengeluaran_kuliah",
        "kehabisan_uang", "budgeting", "faktor_membengkak",
        "frekuensi_belanja_online", "jenis_kelamin",
    ]
    cat_labels = [
        "Uang Saku", "Total Pengeluaran", "Makan",
        "Transport", "Hiburan", "Kuliah",
        "Kehabisan", "Budgeting", "Faktor Membengkak",
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
            colorscale="Viridis",
            zmin=0, zmax=1,
            text=np.round(matrix, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
        ))
        fig_heat.update_layout(
            height=500,
            xaxis=dict(tickangle=-30),
        )
        style_fig(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.caption("Cramér's V: 0 = tidak ada asosiasi, 1 = asosiasi sempurna")
    else:
        st.warning("Data terlalu sedikit untuk menghitung Cramér's V. Hapus filter untuk melihat heatmap.")

    st.markdown("---")

    # Tabel data mentah
    st.markdown('<p class="section-title">📄 Data Mentah (Filtered)</p>', unsafe_allow_html=True)
    with st.expander("Tampilkan Data"):
        st.dataframe(filtered.reset_index(drop=True), use_container_width=True)
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV (Filtered)",
            data=csv,
            file_name="data_filtered.csv",
            mime="text/csv",
        )

# ══════════════════════════════════════════════
# TAB 5 – SIMULASI MONTE CARLO
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-title">🎲 Simulasi Monte Carlo: Risiko Keuangan</p>', unsafe_allow_html=True)
    st.markdown("Simulasi ini memproyeksikan probabilitas kehabisan uang dan distribusi sisa uang bulanan berdasarkan **10.000 iterasi acak**, menggunakan distribusi empiris dari data survei yang sedang aktif (sesuai filter sidebar).")
    
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        sim_uang_saku = st.selectbox("💵 Skenario Uang Saku:", ORDER_UANG_SAKU, index=1)
    with col_sim2:
        sim_budgeting = st.selectbox("📒 Skenario Budgeting:", ["Ya", "Tidak"])
        
    if st.button("🚀 Jalankan Simulasi Monte Carlo", type="primary"):
        with st.spinner("Menjalankan 10.000 iterasi simulasi..."):
            n_sim = 10000
            
            # 1. Ambil data referensi berdasarkan skenario yang dipilih
            ref_data = filtered[(filtered["uang_saku"] == sim_uang_saku) & (filtered["budgeting"] == sim_budgeting)]
            
            # Fallback jika data hasil filter terlalu sedikit, agar simulasi tetap berjalan
            if len(ref_data) < 5:
                ref_data = filtered[filtered["uang_saku"] == sim_uang_saku]
            if len(ref_data) < 5:
                ref_data = filtered 
                
            # 2. Fungsi vectorized untuk mapping kategori ke nilai numerik (midpoint + random uniform dalam range)
            def map_to_numeric(series, jenis):
                res = np.zeros(len(series))
                s_str = series.astype(str)
                if jenis == "uang_saku":
                    res = np.where(s_str.str.contains("< Rp 500.000", na=False), np.random.uniform(100000, 499000, len(series)), res)
                    res = np.where(s_str.str.contains("Rp 500.000 - Rp 1.000.000", na=False), np.random.uniform(500000, 1000000, len(series)), res)
                    res = np.where(s_str.str.contains("Rp 1.000.001 - Rp 1.500.000", na=False), np.random.uniform(1000001, 1500000, len(series)), res)
                    res = np.where(s_str.str.contains("> Rp 1.500.001", na=False), np.random.uniform(1500001, 2500000, len(series)), res)
                elif jenis == "pengeluaran":
                    res = np.where(s_str.str.contains("< Rp 500.000", na=False), np.random.uniform(100000, 499000, len(series)), res)
                    res = np.where(s_str.str.contains("Rp 500.000 - Rp 700.000", na=False), np.random.uniform(500000, 700000, len(series)), res)
                    res = np.where(s_str.str.contains("Rp 700.001 - Rp 1.000.000", na=False), np.random.uniform(700001, 1000000, len(series)), res)
                    res = np.where(s_str.str.contains("> Rp 1.000.001", na=False), np.random.uniform(1000001, 1500000, len(series)), res)
                return res
            
            # 3. Jalankan Simulasi (Bootstrap sampling dari data historis)
            sampled_us = np.random.choice(ref_data["uang_saku"].values, size=n_sim)
            sampled_exp = np.random.choice(ref_data["total_pengeluaran"].values, size=n_sim)
            sampled_khabis = np.random.choice(ref_data["kehabisan_uang"].values, size=n_sim)
            
            # Konversi ke numerik
            vals_us = map_to_numeric(pd.Series(sampled_us), "uang_saku")
            vals_exp = map_to_numeric(pd.Series(sampled_exp), "pengeluaran")
            
            # Hitung sisa uang
            sisa_uang = vals_us - vals_exp
            
            # 4. Hitung Metrik Statistik
            prob_khabis = np.mean(sampled_khabis == "Ya") * 100
            mean_sisa = np.mean(sisa_uang)
            risk_sisa_negatif = np.mean(sisa_uang < 0) * 100
            p5_sisa = np.percentile(sisa_uang, 5)
            p95_sisa = np.percentile(sisa_uang, 95)
            
            # Hitung baseline global untuk perbandingan delta
            overall_khabis = np.mean(filtered["kehabisan_uang"] == "Ya") * 100
            delta_khabis = prob_khabis - overall_khabis
            
            # 5. Tampilkan Output KPI
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(
                "📉 Probabilitas Kehabisan Uang", 
                f"{prob_khabis:.1f}%", 
                delta=f"{delta_khabis:+.1f}% vs rata-rata", 
                delta_color="inverse" if prob_khabis > overall_khabis else "normal"
            )
            kpi2.metric(
                "💰 Rata-rata Sisa Uang", 
                f"Rp {mean_sisa:,.0f}"
            )
            kpi3.metric(
                "⚠️ Risiko Defisit (Sisa < 0)", 
                f"{risk_sisa_negatif:.1f}%"
            )
            
            st.markdown("---")
            
            # 6. Visualisasi Distribusi Sisa Uang
            st.markdown('<p class="section-title">📊 Distribusi Sisa Uang Bulanan (10.000 Simulasi)</p>', unsafe_allow_html=True)
            
            df_sim = pd.DataFrame({"Sisa Uang": sisa_uang})
            fig_sim = px.histogram(
                df_sim, x="Sisa Uang", nbins=50,
                color_discrete_sequence=["#6366f1"],
                marginal="box",
                opacity=0.8
            )
            # Tambahkan garis vertikal di 0 (Titik Impas)
            fig_sim.add_vline(x=0, line_dash="dash", line_color="#f43f5e", annotation_text="Titik Impas (Rp 0)")
            
            fig_sim.update_layout(
                xaxis_title="Sisa Uang (Rp)",
                yaxis_title="Frekuensi",
                showlegend=False,
                hovermode="x unified"
            )
            style_fig(fig_sim)
            st.plotly_chart(fig_sim, use_container_width=True)
            
            # 7. Insight / Interpretasi Otomatis
            st.info(f"""
            💡 **Interpretasi Simulasi:**
            - Berdasarkan profil **Uang Saku: {sim_uang_saku}** dan **Budgeting: {sim_budgeting}**, simulasi menunjukkan rata-rata sisa uang sebesar **Rp {mean_sisa:,.0f}**.
            - Terdapat risiko **{risk_sisa_negatif:.1f}%** di mana pengeluaran melebihi uang saku (defisit).
            - Rentang sisa uang yang paling mungkin terjadi (90% confidence interval) adalah antara **Rp {p5_sisa:,.0f}** hingga **Rp {p95_sisa:,.0f}**.
            - Area histogram di sebelah kiri garis merah (Rp 0) merepresentasikan skenario kehabisan uang sebelum akhir bulan.
            """)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#475569; font-size:0.8rem;'>"
    "Dashboard Analisis Keuangan Mahasiswa · Sains Data · 2026"
    "</p>",
    unsafe_allow_html=True,
)
