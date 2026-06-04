import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Only load the exact columns the dashboard actually uses (ignores useless ID codes)
    cols_to_keep = ['Area', 'Item', 'Element', 'Unit', 'Year', 'Production_Value']
    
    try:
        df = pd.read_parquet("data/cleaned_data.parquet", columns=cols_to_keep)
    except FileNotFoundError:
        df = pd.read_parquet("../data/cleaned_data.parquet", columns=cols_to_keep)
        
    # CRITICAL MEMORY FIX: Convert repeating text into 'categories' to save ~80% RAM
    for col in ['Area', 'Item', 'Element', 'Unit']:
        df[col] = df[col].astype('category')
        
    # Downcast the Year column to a smaller integer size
    df['Year'] = pd.to_numeric(df['Year'], downcast='integer')
        
    return df

def apply_filters(df, year_range, areas, element, prod_range, search):
    filtered = df.copy()

    # 1. Date Range Filter
    filtered = filtered[(filtered['Year'] >= year_range[0]) & (filtered['Year'] <= year_range[1])]

    # 2. Multi-Select Category Filter (Area/Country)
    if areas:
        filtered = filtered[filtered['Area'].isin(areas)]
    else:
        filtered = filtered[filtered['Area'].isin([])] 

    # 3. Single Category Filter (Element type)
    if element != 'All':
        filtered = filtered[filtered['Element'] == element]

    # 4. Numerical Range Filter
    filtered = filtered[(filtered['Production_Value'] >= prod_range[0]) & (filtered['Production_Value'] <= prod_range[1])]

    # 5. Text / Search Filter
    if search:
        filtered = filtered[filtered['Item'].astype(str).str.contains(search, case=False, na=False)]

    return filtered