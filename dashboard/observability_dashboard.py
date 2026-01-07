#!/usr/bin/env python3
"""
Observability Dashboard for AI Content Analytics Platform
Provides real-time visualization of metrics, logs, and system health
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import altair as alt

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
REFRESH_INTERVAL = 5  # seconds

def get_metrics():
    """Fetch metrics from the backend API"""
    try:
        response = requests.get(f"{API_BASE_URL}/logging/metrics/detailed", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch metrics: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

def get_metrics_history():
    """Fetch metrics history"""
    try:
        response = requests.get(f"{API_BASE_URL}/logging/metrics/history", timeout=5)
        if response.status_code == 200:
            return response.json().get('history', [])
        else:
            return []
    except Exception:
        return []

def get_health_status():
    """Check system health"""
    try:
        response = requests.get(f"{API_BASE_URL}/logging/health", timeout=3)
        return response.status_code == 200
    except Exception:
        return False

def main():
    st.set_page_config(
        page_title="AI Content Analytics - Observability Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Title and header
    st.title("📊 AI Content Analytics - Observability Dashboard")
    st.markdown("---")
    
    # Health status indicator
    health_col1, health_col2 = st.columns([1, 5])
    with health_col1:
        is_healthy = get_health_status()
        if is_healthy:
            st.success("✓ System Healthy")
        else:
            st.error("✗ System Unhealthy")
    
    with health_col2:
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fetch metrics
    metrics = get_metrics()
    if not metrics:
        st.error("Unable to fetch metrics. Please ensure the backend is running.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview", 
        "Performance Metrics", 
        "Error Analysis", 
        "Endpoint Metrics"
    ])
    
    with tab1:
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Queries Processed", 
                metrics.get('queries_processed', 0),
                delta=None
            )
        
        with col2:
            avg_response = metrics.get('average_response_time', 0)
            st.metric(
                "Avg Response Time (s)", 
                f"{avg_response:.3f}",
                delta=None
            )
        
        with col3:
            st.metric(
                "Success Rate (%)", 
                f"{metrics.get('success_rate', 0):.1f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Active Users", 
                metrics.get('active_users', 0),
                delta=None
            )
        
        st.markdown("---")
        
        # Response time percentiles
        st.subheader("Response Time Percentiles")
        percentiles = metrics.get('response_time_percentiles', {})
        if percentiles:
            percentile_data = pd.DataFrame({
                'Percentile': ['50th', '90th', '95th', '99th'],
                'Response Time (s)': [
                    percentiles.get('p50', 0),
                    percentiles.get('p90', 0),
                    percentiles.get('p95', 0),
                    percentiles.get('p99', 0)
                ]
            })
            
            fig = px.bar(
                percentile_data,
                x='Percentile',
                y='Response Time (s)',
                color='Percentile',
                color_discrete_map={
                    '50th': '#2E8B57',
                    '90th': '#FFA500',
                    '95th': '#FF6347',
                    '99th': '#DC143C'
                }
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Operation counts
        st.subheader("Operation Counts")
        operation_counts = {
            'RAG Retrievals': metrics.get('rag_retrieval_count', 0),
            'File Uploads': metrics.get('file_upload_count', 0),
            'Agent Workflows': metrics.get('agent_workflow_count', 0),
            'API Requests': metrics.get('api_request_count', 0)
        }
        
        op_df = pd.DataFrame({
            'Operation': list(operation_counts.keys()),
            'Count': list(operation_counts.values())
        })
        
        fig2 = px.pie(op_df, values='Count', names='Operation', title='Operations Distribution')
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.subheader("Performance Metrics")
        
        # Performance metrics in columns
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            st.metric("Total Processing Time (s)", f"{metrics.get('total_processing_time', 0):.2f}")
            st.metric("Peak Concurrent Users", metrics.get('peak_concurrent_users', 0))
        
        with perf_col2:
            st.metric("Successful Requests", metrics.get('successful_requests', 0))
            st.metric("Failed Requests", metrics.get('failed_requests', 0))
        
        # Response time trend (if we had historical data)
        st.subheader("Recent Activity")
        history = get_metrics_history()
        if history:
            # Filter recent entries for visualization
            recent_history = history[-50:]  # Last 50 entries
            
            # Create dataframe for plotting
            history_df = pd.DataFrame(recent_history)
            if not history_df.empty:
                # Convert timestamps
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
                
                # Response time chart
                response_times = history_df[history_df['type'] == 'query']
                if not response_times.empty:
                    st.subheader("Recent Query Response Times")
                    response_fig = px.line(
                        response_times,
                        x='timestamp',
                        y='response_time',
                        title='Query Response Times Over Time'
                    )
                    st.plotly_chart(response_fig, use_container_width=True)
                
                # Activity timeline
                st.subheader("Activity Timeline")
                activity_counts = history_df['type'].value_counts()
                activity_fig = px.bar(
                    x=activity_counts.index,
                    y=activity_counts.values,
                    title='Activity Distribution'
                )
                activity_fig.update_layout(xaxis_title='Activity Type', yaxis_title='Count')
                st.plotly_chart(activity_fig, use_container_width=True)
    
    with tab3:
        st.subheader("Error Analysis")
        
        error_metrics = {
            'Total Errors': metrics.get('error_count', 0),
            'Failed Requests': metrics.get('failed_requests', 0)
        }
        
        # Error metrics
        error_col1, error_col2 = st.columns(2)
        with error_col1:
            st.metric("Total Errors", error_metrics['Total Errors'])
        with error_col2:
            st.metric("Failed Requests", error_metrics['Failed Requests'])
        
        # Error types breakdown
        error_types = metrics.get('error_types', {})
        if error_types:
            st.subheader("Error Types Breakdown")
            error_df = pd.DataFrame({
                'Error Type': list(error_types.keys()),
                'Count': list(error_types.values())
            })
            
            error_fig = px.bar(
                error_df,
                x='Error Type',
                y='Count',
                title='Error Types Distribution',
                color='Count'
            )
            st.plotly_chart(error_fig, use_container_width=True)
        
        # Recent errors table
        history = get_metrics_history()
        if history:
            error_entries = [entry for entry in history[-20:] if entry.get('type') == 'error']
            if error_entries:
                st.subheader("Recent Errors")
                error_table = pd.DataFrame(error_entries)
                st.dataframe(
                    error_table[['timestamp', 'error_type', 'error_message']].head(10),
                    use_container_width=True
                )
    
    with tab4:
        st.subheader("Endpoint Metrics")
        
        endpoint_metrics = metrics.get('endpoint_metrics', {})
        if endpoint_metrics:
            # Endpoint performance table
            endpoint_data = []
            for endpoint, data in endpoint_metrics.items():
                success_rate = (data['successful_requests'] / data['total_requests'] * 100) if data['total_requests'] > 0 else 0
                avg_response_time = (data['total_response_time'] / data['total_requests']) if data['total_requests'] > 0 else 0
                
                endpoint_data.append({
                    'Endpoint': endpoint,
                    'Total Requests': data['total_requests'],
                    'Success Rate (%)': round(success_rate, 2),
                    'Avg Response Time (s)': round(avg_response_time, 3),
                    'Successful': data['successful_requests'],
                    'Failed': data['failed_requests']
                })
            
            endpoint_df = pd.DataFrame(endpoint_data)
            
            # Sort by total requests
            endpoint_df = endpoint_df.sort_values('Total Requests', ascending=False)
            
            st.dataframe(endpoint_df, use_container_width=True)
            
            # Endpoint success rate chart
            st.subheader("Endpoint Success Rates")
            success_fig = px.bar(
                endpoint_df,
                x='Endpoint',
                y='Success Rate (%)',
                title='Endpoint Success Rates',
                color='Success Rate (%)',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(success_fig, use_container_width=True)
        else:
            st.info("No endpoint metrics available yet.")
    
    # Auto-refresh
    st.markdown("---")
    if st.button("🔄 Refresh Now"):
        st.experimental_rerun()
    
    # Auto-refresh timer
    time.sleep(REFRESH_INTERVAL)
    st.experimental_rerun()

if __name__ == "__main__":
    main()