import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Load the highly compressed Parquet file instead of the massive CSV
    try:
        df = pd.read_parquet("data/cleaned_data.parquet")
    except FileNotFoundError:
        df = pd.read_parquet("../data/cleaned_data.parquet")
    return df

# ... keep your apply_filters function exactly the same below this!

def apply_filters(df, year_range, areas, element, prod_range, search):
    filtered = df.copy()

    # 1. Date Range Filter
    filtered = filtered[(filtered['Year'] >= year_range[0]) & (filtered['Year'] <= year_range[1])]

    # 2. Multi-Select Category Filter (Area/Country)
    if areas:
        filtered = filtered[filtered['Area'].isin(areas)]
    else:
        filtered = filtered[filtered['Area'].isin([])] # Empty if nothing selected

    # 3. Single Category Filter (Element type)
    if element != 'All':
        filtered = filtered[filtered['Element'] == element]

    # 4. Numerical Range Filter
    filtered = filtered[(filtered['Production_Value'] >= prod_range[0]) & (filtered['Production_Value'] <= prod_range[1])]

    # 5. Text / Search Filter
    if search:
        filtered = filtered[filtered['Item'].astype(str).str.contains(search, case=False, na=False)]

    return filtered