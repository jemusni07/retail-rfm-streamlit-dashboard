import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
from databricks import sql
import numpy as np

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="RFM Customer Segmentation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for unique styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f2937;
        --secondary-color: #3b82f6;
        --accent-color: #f59e0b;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --background-color: #f8fafc;
        --card-background: #ffffff;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
    }
    
    /* Custom header styling */
    .main-header {
        background: white;
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 3px solid #000000;
    }
    
    .main-header h1 {
        color: #000000;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .main-header p {
        color: #1f2937;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        text-align: center;
        font-weight: 400;
    }
    
    /* Custom metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        color: #000000;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 2px solid #000000;
        margin-bottom: 1rem;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .metric-card h3 {
        color: #6b7280;
        font-size: 0.75rem;
        margin: 0 0 0.5rem 0;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card .metric-value {
        color: #000000;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    
    /* Custom section headers */
    .section-header {
        background: white;
        color: #000000;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 2rem 0 1rem 0;
        font-size: 1.3rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 2px solid #000000;
    }
    
    /* Custom sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Custom plotly chart containers */
    .plotly-chart-container {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 2px solid #000000;
    }
    
    /* Custom table styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 2px solid #000000;
    }
    
    /* Custom insights cards */
    .insight-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #000000;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .insight-card h4 {
        color: #000000;
        margin: 0 0 0.5rem 0;
        font-weight: 600;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: white;
        color: #000000;
        border: 2px solid #000000;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        background: #f8fafc;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom loading spinner */
    .stSpinner > div {
        border-top-color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load data from Databricks"""
    try:
        # Use warehouse ID if available, otherwise use HTTP path
        warehouse_id = os.getenv('DATABRICKS_WAREHOUSE_ID')
        if warehouse_id:
            http_path = f"/sql/1.0/warehouses/{warehouse_id}"
        else:
            http_path = os.getenv('DATABRICKS_HTTP_PATH')
        
        connection = sql.connect(
            server_hostname=os.getenv('DATABRICKS_SERVER_HOSTNAME'),
            http_path=http_path,
            access_token=os.getenv('DATABRICKS_ACCESS_TOKEN')
        )
        
        cursor = connection.cursor()
        query = f"""
        SELECT * FROM {os.getenv('DATABASE_NAME', 'retail_analytics')}.{os.getenv('TABLE_NAME', 'dlt.segment_summary')}
        ORDER BY Total_Revenue DESC
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        
        df = pd.DataFrame(data, columns=columns)
        cursor.close()
        connection.close()
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_segment_count_chart(df):
    """Create customer count visualization by segment"""
    # Custom color palette - vibrant gradient
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7']
    
    fig = px.bar(
        df, 
        x='Segment', 
        y='Customer_Count',
        title='Customer Count by Segment',
        color='Segment',
        color_discrete_sequence=colors
    )
    fig.update_layout(
        xaxis_title="Customer Segment",
        yaxis_title="Number of Customers",
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        title=dict(font=dict(size=16, color='#1f2937')),
        xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    return fig

def create_segment_revenue_chart(df):
    """Create total revenue visualization by segment"""
    # Custom color palette - cool tones
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7']
    
    fig = px.bar(
        df, 
        x='Segment', 
        y='Total_Revenue',
        title='Total Revenue by Segment',
        color='Segment',
        color_discrete_sequence=colors
    )
    fig.update_layout(
        xaxis_title="Customer Segment",
        yaxis_title="Total Revenue ($)",
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        title=dict(font=dict(size=16, color='#1f2937')),
        xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    return fig

def create_revenue_distribution_pie(df):
    """Create pie chart showing revenue distribution across segments"""
    # Custom color palette - matching bar charts
    custom_colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7']
    
    fig = px.pie(
        df,
        values='Total_Revenue',
        names='Segment',
        title='Revenue Distribution by Segment',
        color_discrete_sequence=custom_colors
    )
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        title=dict(font=dict(size=16, color='#1f2937'))
    )
    return fig

def create_customer_distribution_pie(df):
    """Create pie chart showing customer distribution across segments"""
    # Custom color palette - matching bar charts
    custom_colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7']
    
    fig = px.pie(
        df,
        values='Customer_Count',
        names='Segment',
        title='Customer Distribution by Segment',
        color_discrete_sequence=custom_colors
    )
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        title=dict(font=dict(size=16, color='#1f2937'))
    )
    return fig

def create_rfm_heatmap(df):
    """Create RFM metrics heatmap"""
    # Create a pivot table for RFM metrics
    metrics_df = df[['Segment', 'Avg_Recency', 'Avg_Frequency', 'Avg_Monetary']].copy()
    metrics_df = metrics_df.set_index('Segment')
    
    fig = px.imshow(
        metrics_df.T,
        title='RFM Metrics Heatmap (Average Values)',
        color_continuous_scale='RdYlBu_r',
        aspect='auto'
    )
    fig.update_layout(height=400)
    return fig

def create_segment_performance_table(df):
    """Create styled segment performance table"""
    # Select key columns for the table
    table_df = df[[
        'Segment', 'recommendation', 'Customer_Count', 
        'Total_Revenue', 'Pct_of_Customers', 'Pct_of_Revenue',
        'Avg_Monetary', 'Avg_Frequency', 'Avg_Recency'
    ]].copy()
    
    # Format columns for better display
    table_df['Customer_Count'] = table_df['Customer_Count'].apply(lambda x: f"{x:,}")
    table_df['Total_Revenue'] = table_df['Total_Revenue'].apply(lambda x: f"${x:,.2f}")
    table_df['Pct_of_Customers'] = table_df['Pct_of_Customers'].apply(lambda x: f"{x:.1f}%")
    table_df['Pct_of_Revenue'] = table_df['Pct_of_Revenue'].apply(lambda x: f"{x:.1f}%")
    table_df['Avg_Monetary'] = table_df['Avg_Monetary'].apply(lambda x: f"${x:.2f}")
    table_df['Avg_Frequency'] = table_df['Avg_Frequency'].apply(lambda x: f"{x:.1f}")
    table_df['Avg_Recency'] = table_df['Avg_Recency'].apply(lambda x: f"{x:.1f}")
    
    # Rename columns for better display
    table_df.columns = [
        'Segment', 'Recommendation', 'Customer Count', 
        'Total Revenue', '% of Customers', '% of Revenue',
        'Avg Monetary', 'Avg Frequency', 'Avg Recency'
    ]
    
    return table_df

def main():
    # Custom header
    st.markdown("""
    <div class="main-header">
        <h1>RFM Customer Segmentation Dashboard</h1>
        <p>Group customers into distinct segments based on their shared characteristics and behavior to enable targeted marketing campaigns, optimize resource allocation and improve customer retention.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df is None:
        st.error("Unable to load data. Please check your Databricks configuration.")
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Get all unique segments
    all_segments = sorted(df['Segment'].unique().tolist())
    
    # Radio button to choose between All or Custom
    filter_type = st.sidebar.radio(
        "Filter Type:",
        options=["All Segments", "Custom Selection"],
        index=0
    )
    
    # Show multiselect only if Custom Selection is chosen
    if filter_type == "All Segments":
        df_filtered = df.copy()
        st.sidebar.info(f"Showing all {len(all_segments)} segments")
    else:
        # Custom selection - allow picking one or more segments
        selected_segments = st.sidebar.multiselect(
            "Choose one or more segments:",
            options=all_segments,
            default=all_segments[:1] if all_segments else []
        )
        
        # Filter data based on selection
        if len(selected_segments) > 0:
            df_filtered = df[df['Segment'].isin(selected_segments)].copy()
            st.sidebar.success(f"Showing {len(selected_segments)} segment(s)")
        else:
            df_filtered = df.copy()
            st.sidebar.warning("No segments selected - showing all data")
    
    # Key metrics with custom styling
    st.markdown('<div class="section-header">Key Performance Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Customers</h3>
            <div class="metric-value">{df_filtered['Customer_Count'].sum():,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Revenue</h3>
            <div class="metric-value">${df_filtered['Total_Revenue'].sum():,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_monetary = df_filtered['Avg_Monetary'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg Customer Value</h3>
            <div class="metric-value">${avg_monetary:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        top_segment = df_filtered.loc[df_filtered['Total_Revenue'].idxmax(), 'Segment']
        st.markdown(f"""
        <div class="metric-card">
            <h3>Top Revenue Segment</h3>
            <div class="metric-value">{top_segment}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main visualizations
    st.markdown('<div class="section-header">Customer Segment Analysis</div>', unsafe_allow_html=True)
    
    # Row 1: Count and Revenue charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_count = create_segment_count_chart(df_filtered)
        st.plotly_chart(fig_count, config={'displayModeBar': False})
    
    with col2:
        fig_revenue = create_segment_revenue_chart(df_filtered)
        st.plotly_chart(fig_revenue, config={'displayModeBar': False})
    
    # Row 2: Distribution pie charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_customer_pie = create_customer_distribution_pie(df_filtered)
        st.plotly_chart(fig_customer_pie, config={'displayModeBar': False})
    
    with col2:
        fig_revenue_pie = create_revenue_distribution_pie(df_filtered)
        st.plotly_chart(fig_revenue_pie, config={'displayModeBar': False})
    
    # RFM Heatmap
    st.markdown('<div class="section-header">RFM Metrics Analysis</div>', unsafe_allow_html=True)
    fig_heatmap = create_rfm_heatmap(df_filtered)
    st.plotly_chart(fig_heatmap, config={'displayModeBar': False})
    
    # Segment Performance Table
    st.header("Segment Performance & Recommendations")
    table_df = create_segment_performance_table(df_filtered)
    st.dataframe(
        table_df,
        width='stretch',
        hide_index=True
    )
    
    # Business Insights
    st.header("Business Insights")
    
    # Calculate insights
    total_customers = df_filtered['Customer_Count'].sum()
    total_revenue = df_filtered['Total_Revenue'].sum()
    
    # Top performing segment
    top_revenue_segment = df_filtered.loc[df_filtered['Total_Revenue'].idxmax()]
    
    # Segment with most customers
    top_customer_segment = df_filtered.loc[df_filtered['Customer_Count'].idxmax()]
    
    # High-value segments (above average revenue per customer)
    avg_revenue_per_customer = total_revenue / total_customers
    high_value_segments = df_filtered[df_filtered['Avg_Monetary'] > avg_revenue_per_customer]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Findings")
        st.write(f"**Top Revenue Segment:** {top_revenue_segment['Segment']}")
        st.write(f"- Generates ${top_revenue_segment['Total_Revenue']:,.2f} ({top_revenue_segment['Pct_of_Revenue']:.1f}% of total revenue)")
        st.write(f"- Contains {top_revenue_segment['Customer_Count']:,} customers ({top_revenue_segment['Pct_of_Customers']:.1f}% of total)")
        st.write(f"- Recommendation: {top_revenue_segment['recommendation']}")
        
        st.write(f"**Largest Customer Base:** {top_customer_segment['Segment']}")
        st.write(f"- {top_customer_segment['Customer_Count']:,} customers ({top_customer_segment['Pct_of_Customers']:.1f}% of total)")
        st.write(f"- Generates ${top_customer_segment['Total_Revenue']:,.2f} in revenue")
        st.write(f"- Recommendation: {top_customer_segment['recommendation']}")
    
    with col2:
        st.subheader("Strategic Recommendations")
        
        if len(high_value_segments) > 0:
            st.write("**High-Value Segments to Focus On:**")
            for _, segment in high_value_segments.iterrows():
                st.write(f"- **{segment['Segment']}**: ${segment['Avg_Monetary']:.2f} avg value")
                st.write(f"  Recommendation: {segment['recommendation']}")
        
        # Identify segments with growth potential
        low_frequency_segments = df_filtered[df_filtered['Avg_Frequency'] < df_filtered['Avg_Frequency'].median()]
        if len(low_frequency_segments) > 0:
            st.write("**Segments with Growth Potential:**")
            for _, segment in low_frequency_segments.head(3).iterrows():
                st.write(f"- **{segment['Segment']}**: Low frequency ({segment['Avg_Frequency']:.1f})")
                st.write(f"  Recommendation: {segment['recommendation']}")

if __name__ == "__main__":
    main()