import streamlit as st
from filters import load_data, apply_filters
import charts

st.set_page_config(page_title="Global Agriculture Terminal", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# Smart Number Formatter to prevent Metric Card text wrapping
def format_num(num):
    if num >= 1e9: return f"{num/1e9:.2f}B"
    elif num >= 1e6: return f"{num/1e6:.2f}M"
    elif num >= 1e3: return f"{num/1e3:.1f}K"
    else: return f"{num:,.0f}"

# Responsive, Professional Light/Dark Theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.5rem !important; max-width: 100% !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* NATIVE THEME SYNC */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.2) !important;
}

/* CARDS & CONTAINERS */
.chart-card, .metric-item, .hero { 
    background-color: var(--secondary-background-color) !important; 
    border: 1px solid rgba(128, 128, 128, 0.2) !important; 
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.chart-card:hover, .metric-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    border-color: rgba(37, 99, 235, 0.4) !important; /* Steel Blue accent on hover */
}

/* TYPOGRAPHY */
.hero-title { font-size: 2.5rem; font-weight: 700; color: var(--text-color) !important; line-height: 1.2; margin-bottom: 0.5rem; letter-spacing: -0.02em; }
.hero-title em { font-style: normal; color: #2563eb !important; } /* Steel Blue */
.hero-desc { color: var(--text-color) !important; opacity: 0.8; font-size: 0.95rem; margin-bottom: 0; }
.hero-eyebrow { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: #10b981 !important; margin-bottom: 0.5rem; }

/* METRICS */
.metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.metric-item { padding: 1.5rem; border-left: 4px solid #2563eb; }
.metric-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-color) !important; opacity: 0.7; margin-bottom: 0.4rem;}
.metric-value { font-size: 2.2rem; font-weight: 700; color: var(--text-color) !important; line-height: 1; margin-bottom: 0.2rem; }
.metric-sub { font-size: 0.75rem; color: var(--text-color) !important; opacity: 0.6; }

/* CHARTS */
.chart-info-title { font-size: 1.1rem !important; font-weight: 700 !important; color: var(--text-color) !important; margin: 0; }
.chart-info-desc { font-size: 0.85rem !important; color: var(--text-color) !important; opacity: 0.7; margin: 0; }
.chart-card-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(128, 128, 128, 0.15); }
.chart-num { background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: #ffffff !important; font-size: 0.85rem; font-weight: 700; width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

/* SIDEBAR ELEMENTS */
.sidebar-title { color: var(--text-color) !important; font-size: 1rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; border-bottom: 1px solid rgba(128, 128, 128, 0.2); padding-bottom: 0.8rem; margin-bottom: 1.2rem; }
[data-testid="stSidebar"] label { color: var(--text-color) !important; opacity: 0.8; font-size: 0.75rem !important; font-weight: 600; }
[data-testid="stSidebar"] input, [data-testid="stSidebar"] [data-baseweb="select"] { background: var(--background-color) !important; border: 1px solid rgba(128, 128, 128, 0.3) !important; border-radius: 6px !important; color: var(--text-color) !important; }
.stMultiSelect [data-baseweb="tag"] { background-color: rgba(37, 99, 235, 0.15) !important; color: #2563eb !important; border: 1px solid rgba(37, 99, 235, 0.3) !important; border-radius: 4px !important; }

/* BUTTONS */
.stButton > button { background: #2563eb !important; border: none !important; color: #ffffff !important; width: 100%; border-radius: 6px !important; font-weight: 600 !important; letter-spacing: 0.05em; transition: all 0.2s; }
.stButton > button:hover { background: #1d4ed8 !important; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 4px !important; border-bottom: 1px solid rgba(128, 128, 128, 0.2); padding-bottom: 0; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border: none !important; color: var(--text-color) !important; opacity: 0.6; padding: 12px 16px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { opacity: 1 !important; border-bottom: 2px solid #2563eb !important; color: #2563eb !important; }

[data-testid="stImage"] { background: transparent !important; box-shadow: none !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_data()

df = get_data()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<div class="sidebar-title">Data Filters</div>', unsafe_allow_html=True)
    
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    year_range = st.slider("Year Range", min_year, max_year, (min_year, max_year))
    
    unique_areas = df['Area'].dropna().unique().tolist()
    default_areas = df['Area'].value_counts().head(5).index.tolist() 
    areas = st.multiselect("Region / Country", unique_areas, default=default_areas)
                         
    unique_elements = ['All'] + df['Element'].dropna().unique().tolist()
    element = st.selectbox("Element Type", unique_elements)
    
    min_val, max_val = float(df['Production_Value'].min()), float(df['Production_Value'].max())
    prod_range = st.slider("Volume Range", min_val, max_val, (min_val, max_val))
    
    search = st.text_input("Search Specific Item", placeholder="e.g. Wheat")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Apply Filters"):
        st.rerun()

filtered_df = apply_filters(df, year_range, areas, element, prod_range, search)

# ── HERO ──
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">FAOSTAT Systems Analytics</div>
    <div class="hero-title">Global Agriculture <em>Terminal</em></div>
    <div class="hero-desc">
        Macro-analysis of international agricultural output, livestock yields, and harvested areas ({min_year} - {max_year}).
    </div>
</div>
""", unsafe_allow_html=True)

# ── METRICS ──
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""<div class="metric-item"><div class="metric-label">Processed Records</div>
        <div class="metric-value">{format_num(len(filtered_df))}</div><div class="metric-sub">Active rows in view</div></div>""", unsafe_allow_html=True)
with m2:
    peak_val = filtered_df['Production_Value'].max() if not filtered_df.empty else 0
    st.markdown(f"""<div class="metric-item" style="border-color: #10b981;"><div class="metric-label">Maximum Yield</div>
        <div class="metric-value">{format_num(peak_val)}</div><div class="metric-sub">Highest recorded value</div></div>""", unsafe_allow_html=True)
with m3:
    avg_val = filtered_df['Production_Value'].mean() if not filtered_df.empty else 0
    st.markdown(f"""<div class="metric-item" style="border-color: #8b5cf6;"><div class="metric-label">Mean Distribution</div>
        <div class="metric-value">{format_num(avg_val)}</div><div class="metric-sub">Average across selection</div></div>""", unsafe_allow_html=True)
with m4:
    total_val = filtered_df['Production_Value'].sum() if not filtered_df.empty else 0
    st.markdown(f"""<div class="metric-item" style="border-color: #f59e0b;"><div class="metric-label">Aggregate Volume</div>
        <div class="metric-value">{format_num(total_val)}</div><div class="metric-sub">Total cumulative output</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Distributions", "Macro Trends", "Correlations", "Raw Data", "Advanced Analysis"])

with tab1:
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">01</div><div><p class="chart-info-title">Elements Distribution</p><p class="chart-info-desc">Proportional split of top 5 data elements</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.pie_chart(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">02</div><div><p class="chart-info-title">Value Frequency</p><p class="chart-info-desc">Histogram of bottom 95% production values</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.histogram(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">09</div><div><p class="chart-info-title">Item Frequency Count</p><p class="chart-info-desc">Most commonly recorded agricultural items</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.count_plot(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">03</div><div><p class="chart-info-title">Production Over Time</p><p class="chart-info-desc">Total sum of all production values across selected years</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.line_chart(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">08</div><div><p class="chart-info-title">Cumulative Growth</p><p class="chart-info-desc">Area chart showing stacked growth</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.area_chart(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">04</div><div><p class="chart-info-title">Top 10 Agricultural Items</p><p class="chart-info-desc">Bar comparison of highest total production</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.bar_chart(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">05</div><div><p class="chart-info-title">Time Scatter Map</p><p class="chart-info-desc">Sampled scatter showing density and outliers</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.scatter_plot(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">06</div><div><p class="chart-info-title">Value Spread by Element</p><p class="chart-info-desc">Logarithmic box plot showing quartiles</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.box_plot(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">07</div><div><p class="chart-info-title">Element Correlation</p><p class="chart-info-desc">Heatmap comparing relationships over time</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.heatmap(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">10</div><div><p class="chart-info-title">Probability Density</p><p class="chart-info-desc">Violin plots showcasing density shape</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.violin_plot(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    display_cols = ['Area', 'Item', 'Element', 'Unit', 'Year', 'Production_Value']
    st.dataframe(filtered_df[display_cols].head(5000), use_container_width=True, height=450)
    st.caption("Data table limited to 5,000 rows to ensure terminal performance.")

with tab5:
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">11</div><div><p class="chart-info-title">Element Relationships</p><p class="chart-info-desc">Multi-dimensional matrix pair plot</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.pair_plot(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">12</div><div><p class="chart-info-title">Yearly Production Bubble</p><p class="chart-info-desc">Bubble size = count of records, Color = average yield</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.bubble_chart(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-card"><div class="chart-card-header"><div class="chart-num">13</div><div><p class="chart-info-title">Top Producing Regions</p><p class="chart-info-desc">Funnel chart showing the 5 countries with the highest volume</p></div></div>', unsafe_allow_html=True)
    st.pyplot(charts.funnel_chart(filtered_df), transparent=True)
    st.markdown('</div>', unsafe_allow_html=True)