import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
import time

# Set page config
st.set_page_config(
    page_title="AI Content Analytics - Observability Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 AI Content Analytics - Observability Dashboard")

# Sidebar for configuration
st.sidebar.header("Dashboard Configuration")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, 10)
show_raw_data = st.sidebar.checkbox("Show Raw Metrics Data")

# Auto-refresh
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > refresh_interval:
    st.session_state.last_refresh = time.time()
    st.rerun()

# Load metrics data
def load_metrics():
    metrics_file = "logs/metrics.json"
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, 'r') as f:
                return json.load(f)
        except:
            return {
                'queries_processed': 0,
                'total_response_time': 0.0,
                'query_count': 0,
                'rag_retrieval_count': 0,
                'file_upload_count': 0,
                'agent_workflow_count': 0,
                'error_count': 0,
                'request_history': []
            }
    else:
        return {
            'queries_processed': 0,
            'total_response_time': 0.0,
            'query_count': 0,
            'rag_retrieval_count': 0,
            'file_upload_count': 0,
            'agent_workflow_count': 0,
            'error_count': 0,
            'request_history': []
        }

metrics = load_metrics()

# Create columns for key metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Queries",
        value=metrics['queries_processed'],
        delta="+" + str(len([r for r in metrics['request_history'] if r.get('type') == 'query' and datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) > datetime.now() - timedelta(hours=1)])) + " (last hour)"
    )

with col2:
    avg_response_time = metrics['total_response_time'] / metrics['query_count'] if metrics['query_count'] > 0 else 0
    st.metric(
        label="Avg Response Time (s)",
        value=f"{avg_response_time:.2f}",
        delta="seconds"
    )

with col3:
    st.metric(
        label="RAG Retrievals",
        value=metrics['rag_retrieval_count'],
        delta="+" + str(len([r for r in metrics['request_history'] if r.get('type') == 'rag_retrieval' and datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) > datetime.now() - timedelta(hours=1)])) + " (last hour)"
    )

with col4:
    st.metric(
        label="File Uploads",
        value=metrics['file_upload_count'],
        delta="+" + str(len([r for r in metrics['request_history'] if r.get('type') == 'file_upload' and datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) > datetime.now() - timedelta(hours=1)])) + " (last hour)"
    )

with col5:
    st.metric(
        label="Agent Workflows",
        value=metrics['agent_workflow_count'],
        delta="+" + str(len([r for r in metrics['request_history'] if r.get('type') == 'agent_workflow' and datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) > datetime.now() - timedelta(hours=1)])) + " (last hour)"
    )

# Create tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "⏱️ Performance", "📊 Request Types", "⚠️ Errors"])

with tab1:
    # Create a dataframe for visualization
    if metrics['request_history']:
        df = pd.DataFrame(metrics['request_history'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Group by hour for visualization
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_counts = df.groupby(['hour', 'type']).size().reset_index(name='count')
        
        # Create line chart
        fig = px.line(
            hourly_counts, 
            x='hour', 
            y='count', 
            color='type',
            title='Request Volume Over Time',
            labels={'hour': 'Time', 'count': 'Number of Requests', 'type': 'Request Type'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No metrics data available yet. Process some requests to see metrics.")

with tab2:
    if metrics['request_history']:
        df = pd.DataFrame(metrics['request_history'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter for queries with response time
        query_data = df[df['type'] == 'query']
        if not query_data.empty and 'response_time' in query_data.columns:
            # Response time trend
            fig_response = px.line(
                query_data,
                x='timestamp',
                y='response_time',
                title='Query Response Time Trend',
                labels={'response_time': 'Response Time (s)', 'timestamp': 'Time'}
            )
            st.plotly_chart(fig_response, use_container_width=True)
            
            # Response time histogram
            fig_hist = px.histogram(
                query_data,
                x='response_time',
                nbins=20,
                title='Distribution of Response Times',
                labels={'response_time': 'Response Time (s)', 'count': 'Frequency'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No query response time data available.")
    else:
        st.info("No metrics data available yet.")

with tab3:
    if metrics['request_history']:
        df = pd.DataFrame(metrics['request_history'])
        
        # Pie chart of request types
        type_counts = df['type'].value_counts()
        fig_pie = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title='Distribution of Request Types'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Bar chart of request types
        fig_bar = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            title='Request Count by Type',
            labels={'y': 'Count', 'x': 'Request Type'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No metrics data available yet.")

with tab4:
    if metrics['request_history']:
        df = pd.DataFrame(metrics['request_history'])
        error_data = df[df['type'] == 'error']
        
        if not error_data.empty:
            st.subheader("Error Overview")
            
            # Error count over time
            error_data['hour'] = pd.to_datetime(error_data['timestamp']).dt.floor('H')
            hourly_errors = error_data.groupby('hour').size().reset_index(name='error_count')
            
            fig_errors = px.line(
                hourly_errors,
                x='hour',
                y='error_count',
                title='Errors Over Time',
                labels={'error_count': 'Number of Errors', 'hour': 'Time'}
            )
            st.plotly_chart(fig_errors, use_container_width=True)
            
            # Error types
            if 'error_type' in error_data.columns:
                error_type_counts = error_data['error_type'].value_counts()
                fig_error_types = px.bar(
                    x=error_type_counts.index,
                    y=error_type_counts.values,
                    title='Error Types Distribution',
                    labels={'y': 'Count', 'x': 'Error Type'}
                )
                st.plotly_chart(fig_error_types, use_container_width=True)
            
            # Recent errors table
            st.subheader("Recent Errors")
            recent_errors = error_data.nlargest(10, 'timestamp')
            if not recent_errors.empty:
                st.dataframe(
                    recent_errors[['timestamp', 'error_type', 'error_message']].rename(
                        columns={
                            'error_type': 'Type',
                            'error_message': 'Message',
                            'timestamp': 'Timestamp'
                        }
                    ),
                    use_container_width=True
                )
        else:
            st.info("No errors recorded yet.")
    else:
        st.info("No metrics data available yet.")

# Show raw data if requested
if show_raw_data and metrics['request_history']:
    st.subheader("Raw Metrics Data")
    st.json(metrics)

# Auto-refresh indicator
st.sidebar.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Add a refresh button
if st.sidebar.button("Refresh Data"):
    st.session_state.last_refresh = 0  # Force refresh
    st.rerun()