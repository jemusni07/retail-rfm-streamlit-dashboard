import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
from databricks import sql
import numpy as np
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Retail Analytics Dashboard",
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
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 8px;
        border: 2px solid #000000;
        color: #000000;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #000000;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_rfm_data():
    """Load RFM segmentation data from Databricks"""
    try:
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
        st.error(f"Error loading RFM data: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_transaction_data():
    """Load transaction data for time-series analysis"""
    try:
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
        
        # Query for time-series analysis - FIXED: Added InvoiceNo to SELECT
        query = """
        SELECT 
            InvoiceNo,
            InvoiceDate,
            Year,
            Month,
            CustomerID,
            TotalPrice,
            Quantity,
            Country,
            IsCancellation,
            ingestion_timestamp,
            processing_date
        FROM retail_analytics.dlt.retail_transactions_silver
        WHERE IsCancellation = false 
        AND CustomerID IS NOT NULL
        ORDER BY InvoiceDate
        """
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        
        df = pd.DataFrame(data, columns=columns)
        
        # Convert date columns
        if not df.empty:
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
            df['processing_date'] = pd.to_datetime(df['processing_date'])
            df['ingestion_timestamp'] = pd.to_datetime(df['ingestion_timestamp'])
        
        cursor.close()
        connection.close()
        
        return df
    except Exception as e:
        st.error(f"Error loading transaction data: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_data_freshness_metrics(df):
    """Calculate data freshness metrics"""
    try:
        # Convert all datetime columns to timezone-naive
        latest_ingestion = pd.to_datetime(df['ingestion_timestamp'].max()).tz_localize(None)
        latest_transaction = pd.to_datetime(df['InvoiceDate'].max()).tz_localize(None)
        oldest_transaction = pd.to_datetime(df['InvoiceDate'].min()).tz_localize(None)
        
        # Data coverage
        date_range = (latest_transaction - oldest_transaction).days
        
        # Processing lag
        df_temp = df.copy()
        df_temp['InvoiceDate'] = pd.to_datetime(df_temp['InvoiceDate']).dt.tz_localize(None)
        df_temp['ingestion_timestamp'] = pd.to_datetime(df_temp['ingestion_timestamp']).dt.tz_localize(None)
        
        processing_lag = df_temp.groupby('InvoiceDate').agg({
            'ingestion_timestamp': 'first',
            'processing_date': 'first'
        }).reset_index()
        processing_lag['lag_days'] = (processing_lag['ingestion_timestamp'] - processing_lag['InvoiceDate']).dt.days
        avg_lag = processing_lag['lag_days'].mean()
        
        return {
            'latest_ingestion': latest_ingestion,
            'latest_transaction': latest_transaction,
            'oldest_transaction': oldest_transaction,
            'date_range_days': date_range,
            'avg_processing_lag': avg_lag,
            'total_records': len(df)
        }
    except Exception as e:
        st.error(f"Error calculating freshness metrics: {str(e)}")
        return None

def create_customer_growth_chart(df):
    """Create cumulative customer growth over time"""
    # Get unique customers by first purchase date
    customer_first_purchase = df.groupby('CustomerID')['InvoiceDate'].min().reset_index()
    customer_first_purchase.columns = ['CustomerID', 'FirstPurchaseDate']
    
    # Create daily customer counts
    daily_new_customers = customer_first_purchase.groupby('FirstPurchaseDate').size().reset_index()
    daily_new_customers.columns = ['Date', 'NewCustomers']
    daily_new_customers = daily_new_customers.sort_values('Date')
    daily_new_customers['CumulativeCustomers'] = daily_new_customers['NewCustomers'].cumsum()
    
    # Create figure with dual y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add cumulative customers line
    fig.add_trace(
        go.Scatter(
            x=daily_new_customers['Date'],
            y=daily_new_customers['CumulativeCustomers'],
            name='Total Customers',
            line=dict(color='#3b82f6', width=3),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ),
        secondary_y=False
    )
    
    # Add new customers bar chart
    fig.add_trace(
        go.Bar(
            x=daily_new_customers['Date'],
            y=daily_new_customers['NewCustomers'],
            name='New Customers',
            marker_color='#10b981',
            opacity=0.6
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Customer Growth Over Time',
        xaxis_title='Date',
        height=450,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="Total Customers", secondary_y=False, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(title_text="New Customers per Day", secondary_y=True)
    
    return fig

def create_revenue_trend_chart(df):
    """Create revenue trend over time"""
    # Monthly revenue aggregation
    monthly_revenue = df.groupby(df['InvoiceDate'].dt.to_period('M')).agg({
        'TotalPrice': 'sum',
        'CustomerID': 'nunique',
        'InvoiceNo': 'nunique'
    }).reset_index()
    
    monthly_revenue['InvoiceDate'] = monthly_revenue['InvoiceDate'].dt.to_timestamp()
    monthly_revenue.columns = ['Month', 'Revenue', 'UniqueCustomers', 'Orders']
    
    # Calculate growth rates
    monthly_revenue['RevenueGrowth'] = monthly_revenue['Revenue'].pct_change() * 100
    monthly_revenue['CustomerGrowth'] = monthly_revenue['UniqueCustomers'].pct_change() * 100
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Monthly Revenue', 'Month-over-Month Growth Rate'),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )
    
    # Revenue bars
    fig.add_trace(
        go.Bar(
            x=monthly_revenue['Month'],
            y=monthly_revenue['Revenue'],
            name='Revenue',
            marker_color='#667eea',
            text=monthly_revenue['Revenue'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Growth rate line
    fig.add_trace(
        go.Scatter(
            x=monthly_revenue['Month'],
            y=monthly_revenue['RevenueGrowth'],
            name='Revenue Growth %',
            line=dict(color='#f59e0b', width=3),
            mode='lines+markers'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12)
    )
    
    fig.update_xaxes(title_text="Month", row=2, col=1)
    fig.update_yaxes(title_text="Revenue ($)", gridcolor='rgba(128,128,128,0.2)', row=1, col=1)
    fig.update_yaxes(title_text="Growth Rate (%)", gridcolor='rgba(128,128,128,0.2)', row=2, col=1)
    
    return fig

def create_customer_cohort_chart(df):
    """Create customer cohort retention analysis"""
    # Prepare cohort data - work with a copy to avoid modifying original
    df_cohort = df.copy()
    df_cohort['CohortMonth'] = df_cohort.groupby('CustomerID')['InvoiceDate'].transform('min').dt.to_period('M')
    df_cohort['InvoiceMonth'] = df_cohort['InvoiceDate'].dt.to_period('M')
    
    # Calculate cohort periods
    df_cohort['CohortPeriod'] = (df_cohort['InvoiceMonth'] - df_cohort['CohortMonth']).apply(lambda x: x.n)
    
    # Create cohort matrix
    cohort_data = df_cohort.groupby(['CohortMonth', 'CohortPeriod'])['CustomerID'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='CohortMonth', columns='CohortPeriod', values='CustomerID')
    
    # Calculate retention rates
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0) * 100
    
    # Convert Period index to string to avoid JSON serialization issues
    retention_display = retention.iloc[:12, :12].copy()
    retention_display.index = retention_display.index.astype(str)
    
    # Create heatmap
    fig = px.imshow(
        retention_display,
        labels=dict(x="Months Since First Purchase", y="Cohort Month", color="Retention %"),
        title='Customer Retention Cohort Analysis (First 12 Months)',
        color_continuous_scale='RdYlGn',
        aspect='auto'
    )
    
    fig.update_layout(height=500)
    
    return fig

def create_active_customers_chart(df):
    """Create monthly active customers trend"""
    monthly_active = df.groupby(df['InvoiceDate'].dt.to_period('M')).agg({
        'CustomerID': 'nunique',
        'TotalPrice': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()
    
    monthly_active['InvoiceDate'] = monthly_active['InvoiceDate'].dt.to_timestamp()
    monthly_active.columns = ['Month', 'ActiveCustomers', 'Revenue', 'Orders']
    monthly_active['AvgRevenuePerCustomer'] = monthly_active['Revenue'] / monthly_active['ActiveCustomers']
    
    # Create dual-axis chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=monthly_active['Month'],
            y=monthly_active['ActiveCustomers'],
            name='Active Customers',
            marker_color='#4facfe'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=monthly_active['Month'],
            y=monthly_active['AvgRevenuePerCustomer'],
            name='Avg Revenue per Customer',
            line=dict(color='#f5576c', width=3),
            mode='lines+markers'
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Monthly Active Customers & Average Revenue',
        xaxis_title='Month',
        height=450,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_yaxes(title_text="Active Customers", secondary_y=False, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(title_text="Avg Revenue per Customer ($)", secondary_y=True)
    
    return fig

def create_country_revenue_chart(df):
    """Create top countries by revenue"""
    country_revenue = df.groupby('Country').agg({
        'TotalPrice': 'sum',
        'CustomerID': 'nunique',
        'InvoiceNo': 'nunique'
    }).reset_index()
    
    country_revenue.columns = ['Country', 'Revenue', 'Customers', 'Orders']
    country_revenue = country_revenue.sort_values('Revenue', ascending=False).head(10)
    
    fig = px.bar(
        country_revenue,
        x='Revenue',
        y='Country',
        orientation='h',
        title='Top 10 Countries by Revenue',
        color='Revenue',
        color_continuous_scale='Blues',
        text='Revenue'
    )
    
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(
        height=450,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)')
    )
    
    return fig

# RFM Visualization Functions (from original code)
def create_segment_count_chart(df):
    """Create customer count visualization by segment"""
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
    """Create revenue visualization by segment"""
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
    table_df = df[[
        'Segment', 'recommendation', 'Customer_Count', 
        'Total_Revenue', 'Pct_of_Customers', 'Pct_of_Revenue',
        'Avg_Monetary', 'Avg_Frequency', 'Avg_Recency'
    ]].copy()
    
    table_df['Customer_Count'] = table_df['Customer_Count'].apply(lambda x: f"{x:,}")
    table_df['Total_Revenue'] = table_df['Total_Revenue'].apply(lambda x: f"${x:,.2f}")
    table_df['Pct_of_Customers'] = table_df['Pct_of_Customers'].apply(lambda x: f"{x:.1f}%")
    table_df['Pct_of_Revenue'] = table_df['Pct_of_Revenue'].apply(lambda x: f"{x:.1f}%")
    table_df['Avg_Monetary'] = table_df['Avg_Monetary'].apply(lambda x: f"${x:.2f}")
    table_df['Avg_Frequency'] = table_df['Avg_Frequency'].apply(lambda x: f"{x:.1f}")
    table_df['Avg_Recency'] = table_df['Avg_Recency'].apply(lambda x: f"{x:.1f}")
    
    table_df.columns = [
        'Segment', 'Recommendation', 'Customer Count', 
        'Total Revenue', '% of Customers', '% of Revenue',
        'Avg Monetary', 'Avg Frequency', 'Avg Recency'
    ]
    
    return table_df

def render_rfm_tab(df_rfm):
    """Render RFM Segmentation tab content"""
    st.markdown("""
    <div class="main-header">
        <h1>RFM Customer Segmentation Dashboard</h1>
        <p>Group customers into distinct segments based on their Recency, Frequency, and Monetary Value to enable targeted marketing campaigns, optimize resource allocation and improve customer retention.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar filters
    st.sidebar.header("RFM Filters")
    
    all_segments = sorted(df_rfm['Segment'].unique().tolist())
    
    filter_type = st.sidebar.radio(
        "Filter Type:",
        options=["All Segments", "Custom Selection"],
        index=0,
        key='rfm_filter'
    )
    
    if filter_type == "All Segments":
        df_filtered = df_rfm.copy()
        st.sidebar.info(f"Showing all {len(all_segments)} segments")
    else:
        selected_segments = st.sidebar.multiselect(
            "Choose one or more segments:",
            options=all_segments,
            default=all_segments[:1] if all_segments else [],
            key='rfm_segments'
        )
        
        if len(selected_segments) > 0:
            df_filtered = df_rfm[df_rfm['Segment'].isin(selected_segments)].copy()
            st.sidebar.success(f"Showing {len(selected_segments)} segment(s)")
        else:
            df_filtered = df_rfm.copy()
            st.sidebar.warning("No segments selected - showing all data")
    
    # Visualizations
    st.markdown('<div class="section-header">Customer Segment Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_count = create_segment_count_chart(df_filtered)
        st.plotly_chart(fig_count, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        fig_revenue = create_segment_revenue_chart(df_filtered)
        st.plotly_chart(fig_revenue, use_container_width=True, config={'displayModeBar': False})
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_customer_pie = create_customer_distribution_pie(df_filtered)
        st.plotly_chart(fig_customer_pie, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        fig_revenue_pie = create_revenue_distribution_pie(df_filtered)
        st.plotly_chart(fig_revenue_pie, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('<div class="section-header">RFM Metrics Analysis</div>', unsafe_allow_html=True)
    fig_heatmap = create_rfm_heatmap(df_filtered)
    st.plotly_chart(fig_heatmap, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('<div class="section-header">Segment Performance & Recommendations</div>', unsafe_allow_html=True)
    table_df = create_segment_performance_table(df_filtered)
    st.dataframe(table_df, use_container_width=True, hide_index=True)

def render_insights_tab(df_trans):
    """Render Customer & Revenue Insights tab content"""
    st.markdown("""
    <div class="main-header">
        <h1>Customer Growth & Revenue Insights</h1>
        <p>Track customer acquisition, revenue trends, and data freshness to understand business performance over time.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data freshness metrics
    freshness = get_data_freshness_metrics(df_trans)
    
    if freshness:
        st.markdown('<div class="section-header">Data Freshness & Quality</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Latest Transaction</h3>
                <div class="metric-value">{freshness['latest_transaction'].strftime('%Y-%m-%d')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Last Ingestion</h3>
                <div class="metric-value">{freshness['latest_ingestion'].strftime('%Y-%m-%d')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Data Coverage</h3>
                <div class="metric-value">{freshness['date_range_days']} days</div>
            </div>
            """, unsafe_allow_html=True)
        
    
    # Customer and revenue metrics
    st.markdown('<div class="section-header">Business Performance Metrics</div>', unsafe_allow_html=True)
    
    total_customers = df_trans['CustomerID'].nunique()
    total_revenue = df_trans['TotalPrice'].sum()
    total_orders = df_trans['InvoiceNo'].nunique()
    avg_order_value = total_revenue / total_orders
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Customers</h3>
            <div class="metric-value">{total_customers:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Revenue</h3>
            <div class="metric-value">${total_revenue:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Orders</h3>
            <div class="metric-value">{total_orders:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg Order Value</h3>
            <div class="metric-value">${avg_order_value:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Customer growth analysis
    st.markdown('<div class="section-header">Customer Growth Analysis</div>', unsafe_allow_html=True)
    fig_growth = create_customer_growth_chart(df_trans)
    st.plotly_chart(fig_growth, use_container_width=True, config={'displayModeBar': False})
    
    # Revenue trends
    st.markdown('<div class="section-header">Revenue Trends & Growth</div>', unsafe_allow_html=True)
    fig_revenue = create_revenue_trend_chart(df_trans)
    st.plotly_chart(fig_revenue, use_container_width=True, config={'displayModeBar': False})
    
    # Active customers and country analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Monthly Active Customers</div>', unsafe_allow_html=True)
        fig_active = create_active_customers_chart(df_trans)
        st.plotly_chart(fig_active, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<div class="section-header">Top Countries</div>', unsafe_allow_html=True)
        fig_country = create_country_revenue_chart(df_trans)
        st.plotly_chart(fig_country, use_container_width=True, config={'displayModeBar': False})
    
    # Cohort analysis
    st.markdown('<div class="section-header">Customer Cohort Retention</div>', unsafe_allow_html=True)
    fig_cohort = create_customer_cohort_chart(df_trans)
    st.plotly_chart(fig_cohort, use_container_width=True, config={'displayModeBar': False})

def main():
    # Create tabs
    tab1, tab2 = st.tabs(["📊 RFM Segmentation", "📈 Customer & Revenue Insights"])
    
    with tab1:
        df_rfm = load_rfm_data()
        if df_rfm is not None:
            render_rfm_tab(df_rfm)
        else:
            st.error("Unable to load RFM segmentation data. Please check your Databricks configuration.")
    
    with tab2:
        df_trans = load_transaction_data()
        if df_trans is not None:
            render_insights_tab(df_trans)
        else:
            st.error("Unable to load transaction data. Please check your Databricks configuration.")

if __name__ == "__main__":
    main()