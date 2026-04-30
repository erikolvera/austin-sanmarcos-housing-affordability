import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Austin Housing Affordability", layout="wide")



st.title("Austin-San Marcos Housing Affordability Analysis")
st.markdown("Exploring the divergence in home prices, the rising income needed for a mortgage, and the geographic distribution of affordable housing.")

@st.cache_data
def load_and_clean_redfin():
    redfin_df = pd.read_csv('data/redfin_austin_sanmarcos.csv', encoding='utf-16', sep='\t')
    clean_df = redfin_df.copy()
    clean_df.columns = [col.strip() for col in clean_df.columns]
    
    if 'Week of Period End' in clean_df.columns:
        clean_df['Week of Period End'] = pd.to_datetime(clean_df['Week of Period End'])
        
    if 'Median Sale Price' in clean_df.columns:
        clean_df['Median Sale Price'] = clean_df['Median Sale Price'].replace({r'\$': '', r'K': '000'}, regex=True).astype(float)
        
    cols_with_commas = ['Homes Sold', 'New Listings', 'Inventory']
    for col in cols_with_commas:
        if col in clean_df.columns and clean_df[col].dtype == object:
            clean_df[col] = clean_df[col].astype(str).str.replace(',', '', regex=False).astype(float)
            
    return clean_df

@st.cache_data
def load_and_clean_zhvi():
    zillow_zhvi = pd.read_csv('data/zillow_zhvi_city.csv')
    
    zhvi_filtered_raw = zillow_zhvi[zillow_zhvi['RegionName'].isin(['Austin', 'San Marcos'])].copy()
    
    date_cols = [col for col in zhvi_filtered_raw.columns if col.startswith('20')]
    id_cols = [col for col in zhvi_filtered_raw.columns if col not in date_cols]
    
    zhvi_melted = zhvi_filtered_raw.melt(id_vars=id_cols, value_vars=date_cols, var_name='Date', value_name='ZHVI')
    zhvi_melted['Date'] = pd.to_datetime(zhvi_melted['Date'])
    
    return zhvi_melted

@st.cache_data
def load_and_clean_housing():
    housing = pd.read_csv('data/austin_affordable_housing.csv')
    
    housing_clean = housing.dropna(subset=['Latitude', 'Longitude']).copy()
    if 'Zip Code' in housing_clean.columns:
        housing_clean['Zip Code'] = housing_clean['Zip Code'].astype(str).str.replace('.0', '', regex=False)
        
    return housing_clean

@st.cache_data
def load_and_clean_income():
    income = pd.read_csv('data/zillow_income_needed_metro.csv')
    
    income_austin_raw = income[income['RegionName'].str.contains('Austin', na=False, case=False)].copy()
    
    date_cols = [col for col in income_austin_raw.columns if col.startswith('20')]
    id_cols = [col for col in income_austin_raw.columns if col not in date_cols]
    
    income_melted = income_austin_raw.melt(id_vars=id_cols, value_vars=date_cols, var_name='Date', value_name='Income_Needed')
    income_melted['Date'] = pd.to_datetime(income_melted['Date'])
    
    return income_melted

# Load data
with st.spinner("Loading data..."):
    redfin_df = load_and_clean_redfin()
    zhvi_df = load_and_clean_zhvi()
    housing_df = load_and_clean_housing()
    income_df = load_and_clean_income()

st.header("1. Zillow Home Value Index (ZHVI) Trends")
st.markdown("Comparing the typical home values in Austin and San Marcos over time.")

fig_zhvi = px.line(zhvi_df, x='Date', y='ZHVI', color='RegionName', 
                   title="ZHVI Over Time: Austin vs. San Marcos",
                   labels={"ZHVI": "Home Value ($)", "RegionName": "City"},
                   color_discrete_sequence=['#06b6d4', '#ec4899'])
fig_zhvi.update_traces(line=dict(width=4))
fig_zhvi.update_layout(plot_bgcolor='#0f172a', paper_bgcolor='#0f172a', font_color='#f8fafc')
st.plotly_chart(fig_zhvi, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.header("2. The Affordability Wall")
    st.markdown("The income needed to afford a median-priced home in the Austin Metro has skyrocketed.")
    
    fig_income = px.line(income_df, x='Date', y='Income_Needed', 
                         title="Income Needed for a Mortgage in Austin Metro",
                         labels={"Income_Needed": "Required Income ($)"},
                         color_discrete_sequence=['#38bdf8'])
    fig_income.update_traces(line=dict(width=4))
    fig_income.update_layout(plot_bgcolor='#0f172a', paper_bgcolor='#0f172a', font_color='#f8fafc')
    st.plotly_chart(fig_income, use_container_width=True)

with col2:
    st.header("3. Redfin Active Inventory vs. Median Price")
    st.markdown("Exploring market dynamics in Austin via active inventory.")
    
    # Filter redfin for Austin
    redfin_austin = redfin_df[redfin_df['Region'] == 'Austin, TX'].copy() if 'Region' in redfin_df.columns else redfin_df
    
    if 'Inventory' in redfin_austin.columns and 'Median Sale Price' in redfin_austin.columns:
        redfin_austin['Year'] = redfin_austin['Week of Period End'].dt.year
        fig_scatter = px.scatter(redfin_austin, x='Inventory', y='Median Sale Price', color='Year',
                                 hover_data=['Week of Period End'],
                                 title="Inventory vs. Median Sale Price (Austin)",
                                 color_continuous_scale=px.colors.sequential.YlOrRd)
        fig_scatter.update_traces(marker=dict(size=10))
        fig_scatter.update_layout(plot_bgcolor='#0f172a', paper_bgcolor='#0f172a', font_color='#f8fafc',
                                  font=dict(size=14))
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Inventory or Median Sale Price data not available for this view.")

st.header("4. Geographic Distribution of Affordable Housing")
st.markdown("""
**How to read this Bubble Map:**  
Each circle represents a single Affordable Housing Property. The **size and color** of the circle correspond to the number of affordable units in that building. Larger, darker red circles represent massive apartment complexes, while smaller, lighter dots represent smaller properties.

By mapping these locations, we can observe severe **spatial inequality**:
- **Clustering**: The massive chain of large bubbles down the center represents the I-35 corridor and East Austin.
- **Housing Deserts**: West Austin is almost entirely empty, indicating a total lack of affordable housing infrastructure.
""")

if not housing_df.empty:
    fig_map = px.scatter_mapbox(housing_df, lat="Latitude", lon="Longitude", 
                                hover_name="Project_Name" if "Project_Name" in housing_df.columns else None,
                                hover_data=["Total_Units", "Affordable_Units"] if "Total_Units" in housing_df.columns else None,
                                size="Affordable_Units" if "Affordable_Units" in housing_df.columns else None,
                                color="Affordable_Units" if "Affordable_Units" in housing_df.columns else None,
                                color_continuous_scale=px.colors.sequential.Reds,
                                size_max=25, zoom=10, height=550,
                                title="Bubble Map: Property Size and Location")
    fig_map.update_layout(mapbox_style="open-street-map", 
                          plot_bgcolor='#0f172a', paper_bgcolor='#0f172a', font_color='#f8fafc',
                          margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")
st.markdown("**Data Sources**: Zillow Research Data, Redfin Data Center, City of Austin Open Data Portal")
