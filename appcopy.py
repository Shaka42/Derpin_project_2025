import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import numpy as np
from pathlib import Path
import json
import requests
from datetime import datetime, timedelta
import altair as alt

try:
    from streamlit_option_menu import option_menu
    OPTION_MENU_AVAILABLE = True
except ImportError:
    OPTION_MENU_AVAILABLE = False

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

st.set_page_config(page_title="DERPIn Vulnerability Explorer", layout="wide")
st.title("DERPIn Community Vulnerability Explorer")

# ---------------- DATA LOADING WITH ERROR HANDLING ---------------- #
@st.cache_data
def load_data():
    """Load data with comprehensive error handling"""
    try:
        # Try to load the main datasets
        vulnerability = pd.read_csv('merged_index.csv')
        nutrients = pd.read_csv('merged_nutrients.csv')
        
        # Create sample data if files don't exist
        if vulnerability.empty or nutrients.empty:
            raise FileNotFoundError("Data files not found")
            
    except FileNotFoundError:
        # Create sample data for demonstration
        st.warning("\u26a0\ufe0f Data files not found. Using sample data for demonstration.")
        
        districts = ["KAMPALA", "WAKISO", "MUKONO", "JINJA", "MBALE", "GULU", "LIRA", 
                    "MASAKA", "MBARARA", "KASESE", "FORT PORTAL", "ARUA"]
        
        vulnerability = pd.DataFrame({
            'Region': districts,
            'Composite Vulnerability Index': np.random.uniform(0.2, 0.9, len(districts)),
            'Health System Vulnerability Index': np.random.uniform(0.1, 0.8, len(districts)),
            'Mean Adequacy Ratio Index': np.random.uniform(0.3, 0.9, len(districts)),
            'Per Capita Food Consumption Index': np.random.uniform(0.2, 0.8, len(districts)),
            'Vulnerability to Climate Change Index': np.random.uniform(0.1, 0.9, len(districts)),
            'latitude': np.random.uniform(-1.5, 4.2, len(districts)),
            'longitude': np.random.uniform(29.5, 35.0, len(districts))
        })
        
        nutrients = pd.DataFrame({
            'district': districts,
            'Average Consumption adequacy/Vitamin A': np.random.uniform(0.3, 1.2, len(districts)),
            'Average Consumption adequacy/Iron': np.random.uniform(0.4, 1.1, len(districts)),
            'Average Consumption adequacy/Zinc': np.random.uniform(0.2, 1.0, len(districts)),
            'Average Consumption adequacy/Calcium': np.random.uniform(0.5, 1.3, len(districts)),
            'Average Consumption adequacy/Protein': np.random.uniform(0.6, 1.4, len(districts))
        })
    
    # Remove map data loading, always use coordinate-based fallback
    uganda_map = None
    return vulnerability, nutrients, uganda_map

# Load data
vulnerability, nutrients, uganda_map = load_data()

# ---------------- UTILITY FUNCTIONS ---------------- #
def get_risk_level(value, thresholds=[0.3, 0.6]):
    """Determine risk level based on vulnerability value"""
    if value >= thresholds[1]:
        return "High", "🔴"
    elif value >= thresholds[0]:
        return "Medium", "🟡"
    else:
        return "Low", "🟢"

def create_alert_card(title, message, alert_type="info"):
    """Create styled alert cards"""
    alert_class = f"alert-{alert_type}"
    st.markdown(f"""
    <div class="{alert_class}">
        <h4> 🚨 {title}</h4>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- SIDEBAR NAVIGATION ---------------- #
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h2 style='color: #2563eb; margin-bottom: 0.5rem;'>🌍 DERPIn</h2>
        <p style='color: #64748b; font-size: 0.9rem;'>Community Vulnerability Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    if OPTION_MENU_AVAILABLE:
        selected = option_menu(
            menu_title="Navigation",
            options=["🏠 Dashboard", "🗺️ Vulnerability", "🥗 Nutrition", "📋 Reports"],
            icons=["house", "map", "clipboard-data", "bar-chart", "exclamation-triangle", "file-earmark-text"],
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#2563eb", "font-size": "18px"},
                "nav-link": {"font-size": "14px", "text-align": "left", "--hover-color": "#e2e8f0"},
                "nav-link-selected": {"background-color": "#2563eb"},
            }
        )
    else:
        selected = st.selectbox(
            "Navigate to:",
            ["🏠 Dashboard", "🗺️ Vulnerability", "🥗 Nutrition", "📋 Reports"]
        )
    
    # Quick stats in sidebar
    st.markdown("---")
    st.markdown("**📈 Quick Stats**")
    avg_vuln = vulnerability['Composite Vulnerability Index'].mean()
    high_risk_count = len(vulnerability[vulnerability['Composite Vulnerability Index'] >= 0.6])
    
    st.metric("Avg Vulnerability", f"{avg_vuln:.2f}")
    st.metric("High Risk Areas", high_risk_count)
    st.metric("Last Updated", "2024-08-21")

# ---------------- MAIN DASHBOARD ---------------- #
if selected == "🏠 Dashboard":
    # Enhanced Header with Context
    st.markdown("""
    <div class="dashboard-header">
        <div class="dashboard-title">DERPIn Community Vulnerability Dashboard</div>
        <div class="dashboard-subtitle">Comprehensive monitoring of food security, health system resilience, and climate vulnerability across Uganda's regions</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add explanatory context
    st.markdown("""
    ### 📊 What This Dashboard Shows
    This dashboard integrates multiple vulnerability indicators to provide a comprehensive view of community resilience across Uganda:
    - **Composite Vulnerability**: Combined score from health, nutrition, food access, and climate factors
    - **Health System Capacity**: Infrastructure and service delivery capabilities
    - **Nutrition Adequacy**: Population-level micronutrient and macronutrient sufficiency
    - **Food Security**: Access to adequate caloric intake and dietary diversity
    - **Climate Resilience**: Exposure and adaptive capacity to climate change impacts
    
    **Scale Interpretation**: Most indices range from 0-1, where higher values typically indicate greater vulnerability or risk.
    """)
    
    # Key Performance Indicators with enhanced explanations
    st.markdown("### 🎯 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_regions = len(vulnerability['Region'].unique())
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_regions}</div>
            <div class="metric-label">Monitored Regions</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Geographic coverage representing major administrative regions across Uganda")
    
    with col2:
        avg_vuln = vulnerability['Composite Vulnerability Index'].mean()
        risk_level, icon = get_risk_level(avg_vuln)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_vuln:.2f} {icon}</div>
            <div class="metric-label">National Average Vulnerability</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Overall risk level: **{risk_level}** (0.0=lowest, 1.0=highest risk)")
    
    with col3:
        high_risk = len(vulnerability[vulnerability['Composite Vulnerability Index'] >= 0.6])
        percentage_high_risk = (high_risk / total_regions) * 100 if total_regions > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{high_risk}</div>
            <div class="metric-label">High-Risk Regions</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"**{percentage_high_risk:.1f}%** of regions require immediate intervention (≥0.6 vulnerability)")
    
    with col4:
        most_vulnerable = vulnerability.loc[vulnerability['Composite Vulnerability Index'].idxmax(), 'Region']
        highest_score = vulnerability['Composite Vulnerability Index'].max()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="font-size: 1.2rem;">{most_vulnerable}</div>
            <div class="metric-label">Most Vulnerable Region</div>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Vulnerability score: **{highest_score:.2f}** - Priority for resource allocation")
    
    # Enhanced Alert System with Context
    st.markdown("### 🚨 Vulnerability Alert System")
    st.markdown("""
    **Alert Thresholds:**
    - 🔴 **Critical (≥0.7)**: Immediate intervention required - multiple systems at risk
    - 🟡 **High (0.6-0.69)**: Enhanced monitoring needed - early warning stage  
    - 🟢 **Moderate (<0.6)**: Standard monitoring - maintain current programs
    """)
    
    high_vuln_regions = vulnerability[vulnerability['Composite Vulnerability Index'] >= 0.7]
    medium_vuln_regions = vulnerability[(vulnerability['Composite Vulnerability Index'] >= 0.6) & 
                                       (vulnerability['Composite Vulnerability Index'] < 0.7)]
    
    if not high_vuln_regions.empty:
        st.markdown("#### 🔴 Critical Alerts")
        for _, region in high_vuln_regions.iterrows():
            # Calculate which dimensions are driving vulnerability
            dimensions = []
            if 'Health System Vulnerability Index' in region and region['Health System Vulnerability Index'] >= 0.6:
                dimensions.append("Health System")
            if 'Vulnerability to Climate Change Index' in region and region['Vulnerability to Climate Change Index'] >= 0.6:
                dimensions.append("Climate")
            if 'Mean Adequacy Ratio Index' in region and region['Mean Adequacy Ratio Index'] <= 0.4:
                dimensions.append("Nutrition")
            
            primary_drivers = ", ".join(dimensions) if dimensions else "Multiple factors"
            
            create_alert_card(
                f"Critical Vulnerability - {region['Region']}",
                f"Composite Score: **{region['Composite Vulnerability Index']:.2f}** | Primary Drivers: {primary_drivers} | Recommendation: Deploy multi-sectoral emergency response teams",
                "high"
            )
    
    if not medium_vuln_regions.empty:
        st.markdown("#### 🟡 High-Risk Monitoring")
        for _, region in medium_vuln_regions.iterrows():
            create_alert_card(
                f"Enhanced Monitoring - {region['Region']}",
                f"Composite Score: **{region['Composite Vulnerability Index']:.2f}** | Status: Early warning stage | Action: Strengthen existing programs and prepare contingency plans",
                "medium"
            )
    
    if high_vuln_regions.empty and medium_vuln_regions.empty:
        create_alert_card("System Status: Stable", 
                         "No regions currently exceed critical thresholds. Continue standard monitoring protocols.", 
                         "low")
    
    # Enhanced Vulnerability Analysis with Insights
    st.markdown("### 📈 Vulnerability Analysis & Insights")
    
    # Calculate additional metrics for insights
    vulnerability_stats = {
        'mean': vulnerability['Composite Vulnerability Index'].mean(),
        'std': vulnerability['Composite Vulnerability Index'].std(),
        'min': vulnerability['Composite Vulnerability Index'].min(),
        'max': vulnerability['Composite Vulnerability Index'].max()
    }
    
    best_region = vulnerability.loc[vulnerability['Composite Vulnerability Index'].idxmin(), 'Region']
    vulnerability_gap = vulnerability_stats['max'] - vulnerability_stats['min']
    
    st.markdown(f"""
    #### 🔍 Key Insights:
    - **Regional Disparity**: Vulnerability gap of **{vulnerability_gap:.2f}** points between highest ({most_vulnerable}) and lowest ({best_region}) risk regions
    - **System Variability**: Standard deviation of **{vulnerability_stats['std']:.2f}** indicates {'high' if vulnerability_stats['std'] > 0.2 else 'moderate'} regional inequality
    - **Resource Targeting**: Focusing on top {high_risk} high-risk regions could address **{percentage_high_risk:.1f}%** of critical vulnerabilities
    - **Best Practices**: {best_region} (score: {vulnerability_stats['min']:.2f}) represents model practices for replication
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Enhanced top vulnerable regions chart
        st.markdown("#### Most Vulnerable Regions")
        top_vulnerable = vulnerability.nlargest(10, 'Composite Vulnerability Index')
        fig_bar = px.bar(
            top_vulnerable,
            x='Composite Vulnerability Index',
            y='Region',
            orientation='h',
            color='Composite Vulnerability Index',
            color_continuous_scale=['green', 'yellow', 'red'],
            title="Priority Regions for Intervention"
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=12)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("**Policy Implication**: These regions should receive priority in resource allocation and intervention design.")
    
    with col2:
        # Enhanced distribution chart with interpretive zones
        st.markdown("#### National Risk Distribution")
        fig_hist = px.histogram(
            vulnerability,
            x='Composite Vulnerability Index',
            nbins=15,
            title="Population Distribution Across Risk Levels",
            color_discrete_sequence=['#2563eb']
        )
        
        # Add risk zone annotations
        fig_hist.add_vline(x=0.6, line_dash="dash", line_color="orange", 
                          annotation_text="High Risk Threshold", annotation_position="top")
        fig_hist.add_vline(x=0.7, line_dash="dash", line_color="red", 
                          annotation_text="Critical Threshold", annotation_position="top")
        
        fig_hist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", size=12)
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption("**Interpretation**: Most regions cluster in moderate risk; outliers require targeted interventions.")
    
    # Additional Strategic Insights
    st.markdown("### 💡 Strategic Recommendations")
    
    # Calculate correlation insights if multiple indices available
    if len([col for col in vulnerability.columns if 'Index' in col]) > 1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 🎯 **Immediate Actions** (0-6 months)
            - Deploy rapid response teams to critical regions
            - Establish emergency supply chains for high-risk areas
            - Activate community early warning systems
            - Coordinate with local leaders for intervention access
            """)
        
        with col2:
            st.markdown("""
            #### 📅 **Medium-term Strategy** (6-18 months)
            - Strengthen health system capacity in vulnerable regions
            - Implement nutrition supplementation programs
            - Build climate-resilient infrastructure
            - Establish regional coordination mechanisms
            """)
        
        with col3:
            st.markdown("""
            #### 🏗️ **Long-term Development** (18+ months)
            - Invest in education and capacity building
            - Develop sustainable livelihood programs
            - Build institutional resilience and governance
            - Create knowledge transfer from best-practice regions
            """)
    
    # Data Quality and Update Information
    st.markdown("### 📋 Data Quality & Updates")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Data Sources:**
        - FS-COR Platform (Food Security)
        - AGWAA API (Agricultural & Weather)
        - Ministry of Health (Health Systems)
        - Uganda Bureau of Statistics (Demographics)
        """)
    
    with col2:
        st.markdown(f"""
        **Coverage & Quality:**
        - **Regions Covered**: {total_regions}/15 administrative regions
        - **Data Completeness**: 95%+ for core indicators
        - **Update Frequency**: Monthly for rapid indicators, Quarterly for comprehensive metrics
        - **Last Validation**: August 2024
        """)

# ---------------- ENHANCED Vulnerability and Nutrition---------------- #


elif selected == "🗺️ Vulnerability":
    st.title("🗺️ Vulnerability & Nutrition Analytics")

    st.markdown("""
    ### Composite Vulnerability Index by Region
    The **Composite Vulnerability Index (CVI)** is the average of four dimensions:
    - Health System Vulnerability
    - Mean Adequacy Ratio (nutrition adequacy)
    - Per Capita Food Consumption
    - Vulnerability to Climate Change
    This provides a single measure (0 = low, 1 = high) to compare regions.
    """)
    if 'Composite Vulnerability Index' in vulnerability.columns:
        composite = vulnerability[['Region','Composite Vulnerability Index']].drop_duplicates(subset=['Region']).sort_values(by='Composite Vulnerability Index', ascending=False).reset_index(drop=True)
        fig = px.bar(
            composite,
            x="Region",
            y="Composite Vulnerability Index",
            color="Composite Vulnerability Index",
            title="Composite Vulnerability Index by Region"
        )
        fig.update_layout(xaxis_tickangle=-45, coloraxis_colorbar=dict(title="Vulnerability Index"))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(composite)
    else:
        st.warning("Composite Vulnerability Index data not available.")

    st.markdown("""
    ---
    ### Health System Vulnerability Index by Region
    The **Health System Vulnerability Index** measures a region’s susceptibility to health system challenges. (0 = low, 1 = high)
    """)
    if 'Health System Vulnerability Index' in vulnerability.columns:
        health = vulnerability[['Region','Health System Vulnerability Index']].drop_duplicates(subset=['Region']).sort_values(by='Health System Vulnerability Index', ascending=False).reset_index(drop=True)
        fig = px.scatter(
            health,
            x="Health System Vulnerability Index",
            y="Region",
            size="Health System Vulnerability Index",
            color="Health System Vulnerability Index",
            title="Health System Vulnerability Index by Region"
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(health)
    else:
        st.warning("Health System Vulnerability Index data not available.")

    st.markdown("""
    ---
    ### Nutrition Adequacy vs Food Consumption by Region
    This chart compares **per capita food consumption** with the **mean adequacy ratio of nutrients** across regions.
    - Higher on the chart: better nutrient adequacy
    - Further right: higher food consumption (not always adequate nutrition)
    """)
    if 'Mean Adequacy Ratio Index' in vulnerability.columns and 'Per Capita Food Consumption Index' in vulnerability.columns:
        food_sec = vulnerability[['Region','Mean Adequacy Ratio Index','Per Capita Food Consumption Index']].drop_duplicates(subset=['Region']).reset_index(drop=True)
        fig = px.scatter(
            food_sec,
            x='Per Capita Food Consumption Index',
            y='Mean Adequacy Ratio Index',
            color='Region',
            hover_data=['Region'],
            title='Nutrition Adequacy vs Food Consumption by Region'
        )
        fig.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=2, color='DarkSlateGrey')))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(food_sec)
    else:
        st.warning("Food security data not available.")

    st.markdown("""
    ---
    ### Vulnerability to Climate Change Index by Region
    This chart shows how different regions are exposed to the risks of **climate change**, with values ranging from 0 (low) to 1 (high).
    """)
    if 'Vulnerability to Climate Change Index' in vulnerability.columns:
        climate = vulnerability[['Region','Vulnerability to Climate Change Index']].drop_duplicates(subset=['Region']).sort_values(by='Vulnerability to Climate Change Index', ascending=False).reset_index(drop=True)
        fig = px.bar(
            climate,
            x="Region",
            y="Vulnerability to Climate Change Index",
            color="Vulnerability to Climate Change Index",
            title="Vulnerability to Climate Change Index by Region"
        )
        fig.update_layout(xaxis_tickangle=-45, coloraxis_colorbar=dict(title="Vulnerability Index"))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(climate)
    else:
        st.warning("Climate Change Vulnerability Index data not available.")

    st.markdown("""
    ---
    ### Merged Nutrient Data Table
    Below is the merged nutrient adequacy data for all districts.
    """)
    if nutrients is not None:
        st.dataframe(nutrients)
    else:
        st.warning("Nutrient data not available.")

# ---------------- NUTRITION ANALYSIS (FROM NOTEBOOK) ---------------- #
elif selected == "🥗 Nutrition":
    st.title("🥗 Nutritional Adequacy Analysis")
    
    # Make a copy and standardize column names
    merged_nutrients = nutrients.copy()
    
    # First, let's see what columns we actually have
    #st.markdown("### Debug: Current Columns")
    #st.write("Available columns:", merged_nutrients.columns.tolist())
    
    # Standardize column names to ensure uniformity
    column_mapping = {}
    for col in merged_nutrients.columns:
        if 'district' in col.lower():
            continue  # Keep district column as is
        elif 'adequacy' in col.lower() and 'kilocaleries' in col.lower():
            column_mapping[col] = 'Consumption adequacy of Kilocalories (kcal)'
        elif 'adequacy' in col.lower():
            # Standardize all other adequacy columns
            if 'calcium' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Calcium (mg)'
            elif 'folate' in col.lower() or 'foliate' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Folate (mcg)'
            elif 'iron' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Iron (mg)'
            elif 'protein' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Proteins (mg)'
            elif 'riboflavin' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Riboflavin (mg)'
            elif 'thiamin' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Thiamin (mg)'
            elif 'vitamin a' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Vitamin A (mcg)'
            elif 'vitamin b12' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Vitamin B12 (mcg)'
            elif 'vitamin b6' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Vitamin B6 (mg)'
            elif 'vitamin c' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Vitamin C (mg)'
            elif 'zinc' in col.lower():
                column_mapping[col] = 'Average Consumption adequacy of Zinc (mg)'
    
    # Apply the column mapping
    merged_nutrients = merged_nutrients.rename(columns=column_mapping)
    
    st.markdown("### After Standardization:")
    #st.write("Standardized columns:", merged_nutrients.columns.tolist())
    
    st.markdown("## Average Consumption adequacy of Nutrients")
    
    # Display merged nutrients data
    st.dataframe(merged_nutrients)
    
    #st.markdown("### Exploring Districts with the lowest adequacy in various nutrients in Uganda")
    
    #Define nutrients to analyze (standardized names)
    nutrients_to_analyze = [
        "Average Consumption adequacy of Calcium (mg)",
        "Average Consumption adequacy of Folate (mcg)",
        "Average Consumption adequacy of Iron (mg)",
        "Consumption adequacy of Kilocalories (kcal)",
        "Average Consumption adequacy of Proteins (mg)",
        "Average Consumption adequacy of Riboflavin (mg)",
        "Average Consumption adequacy of Thiamin (mg)",
        "Average Consumption adequacy of Vitamin A (mcg)",
        "Average Consumption adequacy of Vitamin B12 (mcg)",
        "Average Consumption adequacy of Vitamin B6 (mg)",
        "Average Consumption adequacy of Vitamin C (mg)",
        "Average Consumption adequacy of Zinc (mg)"
    ]
    
    # Filter to only available nutrients
    available_nutrients = [n for n in nutrients_to_analyze if n in merged_nutrients.columns]
    #st.write(f"Found {len(available_nutrients)} matching nutrients:", available_nutrients)
    
    # Get district column name
    district_col = 'district'
    for col in merged_nutrients.columns:
        if 'district' in col.lower():
            district_col = col
            break
    
    for nutrient in available_nutrients:
        # Clean nutrient name for display
        nutrient_display = nutrient.replace('Average Consumption adequacy of ', '').replace('Consumption adequacy of ', '')
        st.markdown(f"### {nutrient_display}")
        
        if nutrient in merged_nutrients.columns and district_col in merged_nutrients.columns:
            # Check for missing values
            non_null_data = merged_nutrients[[district_col, nutrient]].dropna()
            
            if len(non_null_data) >= 5:
                bottom5 = non_null_data.nsmallest(5, nutrient).copy()
                bottom5["Group"] = "Bottom 5"
                
                # Horizontal bar chart
                fig = px.bar(
                    bottom5,
                    x=nutrient,
                    y=district_col,
                    color="Group",
                    text=nutrient,
                    orientation="h",
                    color_discrete_map={"Bottom 5": "red"}
                )
                
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    title=f"Bottom 5 Districts by {nutrient_display}",
                    xaxis_title="Adequacy",
                    yaxis_title="District",
                    yaxis=dict(categoryorder="total ascending"),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Insufficient data for {nutrient_display} (only {len(non_null_data)} non-null values)")
    
    # Hidden Hunger Analysis
    st.markdown("### Hidden Hunger: Calories vs Iron Adequacy")
    kilocalories_col = 'Consumption adequacy of Kilocalories (kcal)'
    iron_col = 'Average Consumption adequacy of Iron (mg)'
    
    if kilocalories_col in merged_nutrients.columns and iron_col in merged_nutrients.columns:
        scatter_data = merged_nutrients[[district_col, kilocalories_col, iron_col]].dropna()
        
        if len(scatter_data) > 0:
            fig_scatter = px.scatter(
                scatter_data,
                x=kilocalories_col,
                y=iron_col,
                title="Hidden Hunger: Calories vs Iron Adequacy",
                hover_data=[district_col]
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            st.markdown("""
            **Hidden Hunger Insight:** This scatter plot reveals districts that may have adequate calorie intake 
            but insufficient iron adequacy, indicating micronutrient deficiencies despite energy sufficiency.
            Districts in the bottom-right quadrant are particularly at risk for hidden hunger.
            """)
        else:
            st.warning("No data available for Hidden Hunger analysis")
    else:
        st.warning(f"Required columns not found. Looking for: {kilocalories_col} and {iron_col}")
        st.write("Available columns:", merged_nutrients.columns.tolist())

# ---------------- ENHANCED REPORTS ---------------- #
elif selected == "📋 Reports":
    st.title("📋 Comprehensive Reporting")
    
    # Report generation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 Download Data Reports")
        
        # Vulnerability report
        with st.expander("🛡️ Vulnerability Assessment Report"):
            st.markdown("Complete vulnerability analysis across all regions")
            csv_vuln = vulnerability.to_csv(index=False)
            st.download_button(
                "📄 Download Vulnerability Report (CSV)",
                csv_vuln,
                file_name=f"vulnerability_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # Nutrition report  
        with st.expander("🥗 Nutritional Adequacy Report"):
            st.markdown("Detailed nutrition adequacy analysis")
            csv_nutr = nutrients.to_csv(index=False)
            st.download_button(
                "📄 Download Nutrition Report (CSV)",
                csv_nutr,
                file_name=f"nutrition_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        st.markdown("### 🎯 Custom Report Builder")
        
        # Custom report options
        report_type = st.selectbox("Report Type", 
                                  ["Executive Summary", "Detailed Analysis", "Alert Status", "Trend Analysis"])
        
        regions_filter = st.multiselect("Select Regions", 
                                      options=vulnerability['Region'].tolist(),
                                      default=vulnerability['Region'].tolist()[:5])
        
        if st.button("🔄 Generate Custom Report"):
            filtered_data = vulnerability[vulnerability['Region'].isin(regions_filter)]
            
            # Generate executive summary
            if report_type == "Executive Summary":
                st.markdown("### 📊 Executive Summary Report")
                
                avg_vuln = filtered_data['Composite Vulnerability Index'].mean()
                high_risk_count = len(filtered_data[filtered_data['Composite Vulnerability Index'] >= 0.6])
                
                
                summary_report = f"""
                # Community Vulnerability Executive Summary
                **Report Date:** {datetime.now().strftime('%B %d, %Y')}
                **Regions Analyzed:** {len(filtered_data)}
                
                ## Key Findings
                - **Average Vulnerability Index:** {avg_vuln:.2f}
                - **High-Risk Regions:** {high_risk_count}
                
                
                ## Risk Classification
                """
                
                for _, region in filtered_data.iterrows():
                    risk_level, icon = get_risk_level(region['Composite Vulnerability Index'])
                    summary_report += f"- **{region['Region']}**: {region['Composite Vulnerability Index']:.2f} ({risk_level} {icon})\n"
                
                summary_report += f"""
                
                ## Recommendations
                1. **Immediate Action Required** for {high_risk_count} high-risk regions
                2. **Enhanced monitoring** for medium-risk areas
                3. **Resource allocation** prioritization based on population density
                4. **Community resilience** building programs
                
                ---
                *Generated by DERPIn Community Vulnerability Dashboard*
                """
                
                st.markdown(summary_report)
                
                # Download option
                st.download_button(
                    "📄 Download Executive Summary",
                    summary_report,
                    file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            
            elif report_type == "Detailed Analysis":
                st.markdown("### 🔍 Detailed Analysis Report")
                
                # Show detailed statistics
                st.dataframe(
                    filtered_data.describe(),
                    use_container_width=True
                )
                
                # Generate detailed CSV
                detailed_csv = filtered_data.to_csv(index=False)
                st.download_button(
                    "📄 Download Detailed Analysis (CSV)",
                    detailed_csv,
                    file_name=f"detailed_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            elif report_type == "Alert Status":
                st.markdown("### 🚨 Alert Status Report")
                
                high_risk = filtered_data[filtered_data['Composite Vulnerability Index'] >= 0.6]
                medium_risk = filtered_data[(filtered_data['Composite Vulnerability Index'] >= 0.3) & 
                                          (filtered_data['Composite Vulnerability Index'] < 0.6)]
                low_risk = filtered_data[filtered_data['Composite Vulnerability Index'] < 0.3]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🔴 High Risk", len(high_risk))
                    if not high_risk.empty:
                        st.write("**Regions:**")
                        for region in high_risk['Region']:
                            st.write(f"- {region}")
                
                with col2:
                    st.metric("🟡 Medium Risk", len(medium_risk))
                    if not medium_risk.empty:
                        st.write("**Regions:**")
                        for region in medium_risk['Region']:
                            st.write(f"- {region}")
                
                with col3:
                    st.metric("🟢 Low Risk", len(low_risk))
                    if not low_risk.empty:
                        st.write("**Regions:**")
                        for region in low_risk['Region']:
                            st.write(f"- {region}")


# ---------------- FOOTER WITH INSIGHTS ---------------- #
st.markdown("---")
st.markdown("""
<div style='background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 2rem; border-radius: 15px; margin-top: 2rem;'>
    <h3 style='color: #2563eb; margin-bottom: 1rem;'>💡 Key Insights & Recommendations</h3>
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;'>
        <div>
            <h4>🎯 For Policymakers</h4>
            <ul style='color: #64748b;'>
                <li>Prioritize high-vulnerability regions for resource allocation</li>
                <li>Implement early warning systems in critical areas</li>
                <li>Strengthen health system capacity in vulnerable districts</li>
            </ul>
        </div>
        <div>
            <h4>🏥 For NGOs</h4>
            <ul style='color: #64748b;'>
                <li>Focus nutrition programs on deficient regions</li>
                <li>Coordinate with government for maximum impact</li>
                <li>Monitor progress using vulnerability indicators</li>
            </ul>
        </div>
        <div>
            <h4>👥 For Communities</h4>
            <ul style='color: #64748b;'>
                <li>Build local resilience through community programs</li>
                <li>Improve food security and nutrition practices</li>
                <li>Participate in vulnerability monitoring initiatives</li>
            </ul>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- TECHNICAL FOOTER ---------------- #
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #64748b; border-top: 1px solid #e2e8f0; margin-top: 2rem;'>
    <p><strong>DERPIn Community Vulnerability Dashboard</strong> | Built with Streamlit & Plotly</p>
    <p>Data Sources: FS-COR Platform | AGWAA API | Last Updated: {}</p>
    <p style='font-size: 0.8rem;'>For technical support or data inquiries, contact the development team</p>
</div>
""".format(datetime.now().strftime('%B %d, %Y at %I:%M %p')), unsafe_allow_html=True)
