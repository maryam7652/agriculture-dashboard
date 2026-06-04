import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patheffects as pe
import seaborn as sns
import numpy as np

# Professional Steel Blue / Emerald Palette
PRO_PALETTE = ["#2563eb", "#0ea5e9", "#06b6d4", "#10b981", "#8b5cf6", "#f59e0b", "#f43f5e", "#64748b"]

# Deep slate text with a crisp white glowing outline ensures perfect readability in BOTH Light and Dark modes
TEXT_COLOR = "#1e293b" 
OUTLINE = [pe.withStroke(linewidth=2.5, foreground='white')]

# FIX: Converted CSS rgba strings to Matplotlib-safe hex codes with alpha
GRID_COLOR = "#80808033"  # 20% opacity grey
SPINE_COLOR = "#80808066" # 40% opacity grey

def _base_fig(w=10, h=4.5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_alpha(0.0)          
    ax.set_facecolor("none")          
    
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_path_effects(OUTLINE)
        label.set_fontweight('bold')
        
    for spine in ax.spines.values():
        spine.set_edgecolor(SPINE_COLOR)
        
    ax.title.set_color(TEXT_COLOR)
    ax.title.set_path_effects(OUTLINE)
    ax.title.set_fontweight('bold')
    ax.title.set_fontsize(13)
    
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.xaxis.label.set_path_effects(OUTLINE)
    ax.xaxis.label.set_fontweight('bold')
    
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_path_effects(OUTLINE)
    ax.yaxis.label.set_fontweight('bold')
    
    return fig, ax

def _style_ax(ax):
    ax.grid(True, color=GRID_COLOR, linewidth=0.7, linestyle="--")
    ax.set_axisbelow(True)
    return ax

# ── CHARTS ────────────────────────────────────────────────────────

def pie_chart(df):
    fig, ax = _base_fig(10, 4.5)
    counts = df['Element'].value_counts().head(5) 
    
    if counts.empty:
        txt = ax.text(0.5, 0.5, 'NO DATA', ha='center', va='center', color=TEXT_COLOR, fontweight='bold')
        txt.set_path_effects(OUTLINE)
        ax.axis('off')
    else:
        wedges, texts, autotexts = ax.pie(
            counts, labels=counts.index, autopct='%1.1f%%',
            colors=PRO_PALETTE[:len(counts)], startangle=90,
            wedgeprops=dict(edgecolor='white', linewidth=1.5),
        )
        for t in texts: 
            t.set_color(TEXT_COLOR)
            t.set_fontsize(10)
            t.set_path_effects(OUTLINE)
            t.set_fontweight('bold')
        for at in autotexts: 
            at.set_color("#ffffff")
            at.set_fontsize(9)
            at.set_fontweight("bold")
            
    ax.axis('equal')
    ax.set_title('Top Data Elements Distribution', pad=12)
    return fig

def histogram(df):
    fig, ax = _base_fig(10, 4.5)
    q95 = df['Production_Value'].quantile(0.95)
    data = df[df['Production_Value'] <= q95]['Production_Value'].dropna()
    
    if len(data) > 0:
        n, bins, patches = ax.hist(data, bins=30, color="#2563eb", edgecolor='white', linewidth=0.5, alpha=0.8)
        norm = mpl.colors.Normalize(vmin=bins.min(), vmax=bins.max())
        cmap = mpl.cm.Blues
        for patch, left in zip(patches, bins[:-1]):
            patch.set_facecolor(cmap(norm(left) * 0.6 + 0.4))
            
    ax.set_title('Production Value Distribution (Bottom 95%)')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
    _style_ax(ax)
    fig.tight_layout()
    return fig

def line_chart(df):
    fig, ax = _base_fig(10, 4.5)
    trend = df.groupby('Year')['Production_Value'].sum().reset_index()
    if not trend.empty:
        ax.plot(trend['Year'], trend['Production_Value'], color="#2563eb", linewidth=2.5, marker='o', markersize=4)
        
    ax.set_title('Total Global Production Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Production Value')
    _style_ax(ax)
    fig.tight_layout()
    return fig

def bar_chart(df):
    fig, ax = _base_fig(10, 5.5)
    top_items = df.groupby('Item')['Production_Value'].sum().nlargest(10).reset_index()
    
    if not top_items.empty:
        bars = ax.barh(top_items['Item'].str[:25], top_items['Production_Value'], color=PRO_PALETTE[:10], edgecolor='white', linewidth=0.5)
        ax.invert_yaxis()
        
    ax.set_title('Top 10 Agricultural Items by Volume')
    ax.set_xlabel('Total Production Value')
    _style_ax(ax)
    fig.tight_layout()
    return fig

def scatter_plot(df):
    fig, ax = _base_fig(10, 4.5)
    sample = df.sample(min(1000, len(df)), random_state=42)
    ax.scatter(sample['Year'], sample['Production_Value'], alpha=0.6, color="#0ea5e9", s=15, edgecolors='none')
                    
    ax.set_title('Sampled Production Volume Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('Production Value')
    _style_ax(ax)
    fig.tight_layout()
    return fig

def box_plot(df):
    fig, ax = _base_fig(10, 4.5)
    top_elements = df['Element'].value_counts().nlargest(4).index
    filtered = df[df['Element'].isin(top_elements)].dropna(subset=['Production_Value'])
    
    if filtered.empty:
        txt = ax.text(0.5, 0.5, 'NO DATA', ha='center', color=TEXT_COLOR)
        txt.set_path_effects(OUTLINE)
        ax.axis('off')
    else:
        sns.boxplot(data=filtered, x='Element', y='Production_Value', hue='Element', palette=PRO_PALETTE[:4], legend=False, ax=ax)
        ax.set_yscale('log')
        
    ax.set_title('Spread of Values by Element (Log Scale)')
    ax.set_xlabel('Element Type')
    ax.set_ylabel('Log Value')
    _style_ax(ax)
    fig.tight_layout()
    return fig

def heatmap(df):
    fig, ax = _base_fig(10, 4.5)
    pivot = df.pivot_table(index='Year', columns='Element', values='Production_Value', aggfunc='mean')
    corr = pivot.corr()
    
    if not corr.empty and len(corr.columns) > 1:
        sns.heatmap(corr, annot=True, cmap='Blues', fmt='.2f', linewidths=0.5, linecolor=SPINE_COLOR, ax=ax, annot_kws={"weight": "bold"})
    else:
        txt = ax.text(0.5, 0.5, 'Insufficient Variables', ha='center', color=TEXT_COLOR, fontweight='bold')
        txt.set_path_effects(OUTLINE)
        ax.axis('off')
                
    ax.set_title('Correlation Heatmap: Agricultural Elements', pad=12)
    fig.tight_layout()
    return fig

def area_chart(df):
    fig, ax = _base_fig(10, 4.5)
    trend = df.groupby('Year')['Production_Value'].sum().reset_index()
    if not trend.empty:
        ax.fill_between(trend['Year'], trend['Production_Value'], alpha=0.2, color="#10b981")
        ax.plot(trend['Year'], trend['Production_Value'], color="#10b981", linewidth=2)
            
    ax.set_title('Cumulative Production Trend')
    ax.set_xlabel('Year')
    ax.set_ylabel('Production Value')
    _style_ax(ax)
    fig.tight_layout()
    return fig

def count_plot(df):
    fig, ax = _base_fig(10, 4.5)
    top_items = df['Item'].value_counts().nlargest(8).index
    filtered = df[df['Item'].isin(top_items)]
    
    if not filtered.empty:
        sns.countplot(data=filtered, y='Item', order=top_items, color="#2563eb", ax=ax, edgecolor='white', linewidth=0.5)
        
    ax.set_title('Frequency of Top Items in Dataset')
    ax.set_xlabel('Count of Records')
    ax.set_ylabel('')
    _style_ax(ax)
    fig.tight_layout()
    return fig

def violin_plot(df):
    fig, ax = _base_fig(10, 4.5)
    top_elements = df['Element'].value_counts().nlargest(3).index
    filtered = df[df['Element'].isin(top_elements)].dropna(subset=['Production_Value'])
    
    if not filtered.empty:
        sns.violinplot(data=filtered, x='Element', y='Production_Value', hue='Element', palette=PRO_PALETTE[:3], legend=False, ax=ax)
        ax.set_yscale('log')
        
    ax.set_title('Probability Density of Elements (Log Scale)')
    ax.set_xlabel('Element')
    ax.set_ylabel('Log Value')
    _style_ax(ax)
    fig.tight_layout()
    return fig

def bubble_chart(df):
    fig, ax = _base_fig(10, 4.5)
    stats = df.groupby('Year').agg(total_prod=('Production_Value', 'sum'), avg_prod=('Production_Value', 'mean'), record_count=('Production_Value', 'count')).reset_index()
    
    if not stats.empty:
        scatter = ax.scatter(stats['Year'], stats['total_prod'], s=stats['record_count']/10, c=stats['avg_prod'], cmap='Blues', alpha=0.8, edgecolors=SPINE_COLOR)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Average Yield/Prod', color=TEXT_COLOR, fontweight='bold')
        cbar.ax.yaxis.label.set_path_effects(OUTLINE)
        cbar.ax.yaxis.set_tick_params(colors=TEXT_COLOR)
        for label in cbar.ax.yaxis.get_ticklabels():
            label.set_fontweight('bold')
            label.set_path_effects(OUTLINE)
            
    ax.set_title('Yearly Volume vs Total Records (Bubble Size)')
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Production')
    _style_ax(ax)
    fig.tight_layout()
    return fig

def funnel_chart(df):
    fig, ax = _base_fig(10, 4.5)
    top_areas = df.groupby('Area')['Production_Value'].sum().nlargest(5).reset_index()
    
    if not top_areas.empty:
        bars = ax.barh(top_areas['Area'], top_areas['Production_Value'], color=PRO_PALETTE[:5], height=0.6, edgecolor='white')
        for bar, val in zip(bars, top_areas['Production_Value']):
            # Convert to millions/billions for the chart label too
            if val >= 1e9: formatted_val = f"{val/1e9:.1f}B"
            else: formatted_val = f"{val/1e6:.1f}M"
            
            txt = ax.text(bar.get_width() + (top_areas['Production_Value'].max() * 0.02), bar.get_y() + bar.get_height() / 2, 
                          formatted_val, va='center', fontsize=10, color=TEXT_COLOR, fontweight='bold')
            txt.set_path_effects(OUTLINE)
            
    ax.set_title('Top 5 Countries/Areas by Total Volume')
    ax.set_xlabel('Total Production')
    ax.invert_yaxis()
    _style_ax(ax)
    fig.tight_layout()
    return fig

def pair_plot(df):
    pivot = df.pivot_table(index='Year', columns='Element', values='Production_Value', aggfunc='mean')
    valid_cols = pivot.columns[:4] 
    
    if len(valid_cols) > 1:
        pg = sns.pairplot(pivot[valid_cols].dropna(), plot_kws={'alpha': 0.6, 'color': '#2563eb'}, diag_kws={'color': '#10b981'})
        pg.fig.patch.set_alpha(0.0)
        for ax in pg.axes.flatten():
            if ax:
                ax.set_facecolor("none")
                for spine in ax.spines.values(): spine.set_edgecolor(SPINE_COLOR)
                ax.tick_params(colors=TEXT_COLOR, labelsize=8)
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_path_effects(OUTLINE); label.set_fontweight('bold')
                if ax.xaxis.label: 
                    ax.xaxis.label.set_color(TEXT_COLOR); ax.xaxis.label.set_path_effects(OUTLINE); ax.xaxis.label.set_fontweight('bold')
                if ax.yaxis.label: 
                    ax.yaxis.label.set_color(TEXT_COLOR); ax.yaxis.label.set_path_effects(OUTLINE); ax.yaxis.label.set_fontweight('bold')
        
        suptitle = pg.fig.suptitle('Element Relationships over Time', y=1.02, fontsize=14, fontweight='bold', color=TEXT_COLOR)
        suptitle.set_path_effects(OUTLINE)
        return pg.fig
    else:
        fig, ax = _base_fig(10, 4.5)
        txt = ax.text(0.5, 0.5, 'INSUFFICIENT DATA', ha='center', color=TEXT_COLOR, fontweight='bold')
        txt.set_path_effects(OUTLINE)
        return fig