import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class ChartGenerator:
    """Generates various charts for inflation analysis"""
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
    
    def create_cpi_chart(self, cpi_data, title="Consumer Price Index (CPI)"):
        """Create CPI chart with inflation rate"""
        try:
            # Calculate inflation rate
            inflation_rate = cpi_data['value'].pct_change(periods=12) * 100
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                subplot_titles=('CPI Level', 'Year-over-Year Inflation Rate'),
                vertical_spacing=0.1,
                row_heights=[0.6, 0.4]
            )
            
            # CPI Level
            fig.add_trace(
                go.Scatter(
                    x=cpi_data.index,
                    y=cpi_data['value'],
                    mode='lines',
                    name='CPI',
                    line=dict(color=self.color_palette['primary'], width=2),
                    hovertemplate='<b>Date</b>: %{x}<br><b>CPI</b>: %{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Inflation Rate
            fig.add_trace(
                go.Scatter(
                    x=cpi_data.index,
                    y=inflation_rate,
                    mode='lines',
                    name='Inflation Rate',
                    line=dict(color=self.color_palette['danger'], width=2),
                    hovertemplate='<b>Date</b>: %{x}<br><b>Inflation</b>: %{y:.2f}%<extra></extra>'
                ),
                row=2, col=1
            )
            
            # Add horizontal line at 2% inflation target
            fig.add_hline(
                y=2.0,
                line_dash="dash",
                line_color=self.color_palette['success'],
                annotation_text="2% Target",
                row=2, col=1
            )
            
            fig.update_layout(
                title=title,
                height=600,
                showlegend=True,
                hovermode='x unified'
            )
            
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="CPI", row=1, col=1)
            fig.update_yaxes(title_text="Inflation Rate (%)", row=2, col=1)
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating CPI chart: {str(e)}")
            return go.Figure()
    
    def create_m2_chart(self, m2_data, title="M2 Money Supply"):
        """Create M2 money supply chart with growth rate"""
        try:
            # Calculate growth rate
            growth_rate = m2_data['value'].pct_change(periods=12) * 100
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                subplot_titles=('M2 Money Supply (Billions)', 'Year-over-Year Growth Rate'),
                vertical_spacing=0.1,
                row_heights=[0.6, 0.4]
            )
            
            # M2 Level
            fig.add_trace(
                go.Scatter(
                    x=m2_data.index,
                    y=m2_data['value'],
                    mode='lines',
                    name='M2 Money Supply',
                    line=dict(color=self.color_palette['secondary'], width=2),
                    hovertemplate='<b>Date</b>: %{x}<br><b>M2</b>: $%{y:.0f}B<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Growth Rate
            fig.add_trace(
                go.Scatter(
                    x=m2_data.index,
                    y=growth_rate,
                    mode='lines',
                    name='Growth Rate',
                    line=dict(color=self.color_palette['warning'], width=2),
                    hovertemplate='<b>Date</b>: %{x}<br><b>Growth</b>: %{y:.2f}%<extra></extra>'
                ),
                row=2, col=1
            )
            
            # Add zero line
            fig.add_hline(
                y=0,
                line_dash="dash",
                line_color=self.color_palette['dark'],
                row=2, col=1
            )
            
            fig.update_layout(
                title=title,
                height=600,
                showlegend=True,
                hovermode='x unified'
            )
            
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="M2 Money Supply (Billions $)", row=1, col=1)
            fig.update_yaxes(title_text="Growth Rate (%)", row=2, col=1)
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating M2 chart: {str(e)}")
            return go.Figure()
    
    def create_bitcoin_chart(self, bitcoin_data, title="Bitcoin Price"):
        """Create Bitcoin price chart"""
        try:
            fig = go.Figure()
            
            # Bitcoin price
            fig.add_trace(
                go.Scatter(
                    x=bitcoin_data.index,
                    y=bitcoin_data['price'],
                    mode='lines',
                    name='Bitcoin Price',
                    line=dict(color=self.color_palette['warning'], width=2),
                    hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: $%{y:,.2f}<extra></extra>'
                )
            )
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=400,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating Bitcoin chart: {str(e)}")
            return go.Figure()
    
    def create_dual_axis_chart(self, data1, data2, title="Dual Axis Chart", 
                              y1_title="Series 1", y2_title="Series 2"):
        """Create dual axis chart for comparing two different scaled datasets"""
        try:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # First dataset
            fig.add_trace(
                go.Scatter(
                    x=data1.index,
                    y=data1['value'],
                    mode='lines',
                    name=y1_title,
                    line=dict(color=self.color_palette['primary'], width=2),
                    hovertemplate=f'<b>Date</b>: %{{x}}<br><b>{y1_title}</b>: %{{y:.2f}}<extra></extra>'
                ),
                secondary_y=False,
            )
            
            # Second dataset
            fig.add_trace(
                go.Scatter(
                    x=data2.index,
                    y=data2['price'],
                    mode='lines',
                    name=y2_title,
                    line=dict(color=self.color_palette['secondary'], width=2),
                    hovertemplate=f'<b>Date</b>: %{{x}}<br><b>{y2_title}</b>: $%{{y:,.2f}}<extra></extra>'
                ),
                secondary_y=True,
            )
            
            # Update layout
            fig.update_layout(
                title=title,
                height=500,
                hovermode='x unified'
            )
            
            # Set y-axes titles
            fig.update_yaxes(title_text=y1_title, secondary_y=False)
            fig.update_yaxes(title_text=y2_title, secondary_y=True)
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating dual axis chart: {str(e)}")
            return go.Figure()
    
    def create_correlation_heatmap(self, correlation_matrix, title="Correlation Matrix"):
        """Create correlation heatmap"""
        try:
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=correlation_matrix.values.round(3),
                texttemplate="%{text}",
                textfont={"size": 12},
                hoverongaps=False,
                hovertemplate='<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=title,
                height=400,
                width=500
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating correlation heatmap: {str(e)}")
            return go.Figure()
    
    def create_volatility_chart(self, data, window=30, title="Volatility Analysis"):
        """Create volatility chart"""
        try:
            # Calculate rolling volatility
            returns = data.pct_change().dropna()
            volatility = returns.rolling(window=window).std() * np.sqrt(252) * 100  # Annualized
            
            fig = go.Figure()
            
            # Volatility
            fig.add_trace(
                go.Scatter(
                    x=volatility.index,
                    y=volatility,
                    mode='lines',
                    name=f'{window}-Day Volatility',
                    line=dict(color=self.color_palette['danger'], width=2),
                    hovertemplate='<b>Date</b>: %{x}<br><b>Volatility</b>: %{y:.2f}%<extra></extra>'
                )
            )
            
            # Add average line
            avg_volatility = volatility.mean()
            fig.add_hline(
                y=avg_volatility,
                line_dash="dash",
                line_color=self.color_palette['info'],
                annotation_text=f"Average: {avg_volatility:.2f}%"
            )
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Volatility (%)",
                height=400,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating volatility chart: {str(e)}")
            return go.Figure()
    
    def create_distribution_chart(self, data, title="Distribution Analysis"):
        """Create distribution chart (histogram)"""
        try:
            fig = go.Figure()
            
            # Histogram
            fig.add_trace(
                go.Histogram(
                    x=data,
                    nbinsx=30,
                    name='Distribution',
                    marker_color=self.color_palette['primary'],
                    opacity=0.7,
                    hovertemplate='<b>Range</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
                )
            )
            
            # Add mean line
            mean_val = data.mean()
            fig.add_vline(
                x=mean_val,
                line_dash="dash",
                line_color=self.color_palette['danger'],
                annotation_text=f"Mean: {mean_val:.2f}"
            )
            
            fig.update_layout(
                title=title,
                xaxis_title="Value",
                yaxis_title="Frequency",
                height=400,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating distribution chart: {str(e)}")
            return go.Figure()
    
    def create_comparison_chart(self, datasets, title="Comparison Chart"):
        """Create comparison chart for multiple datasets"""
        try:
            fig = go.Figure()
            
            colors = [self.color_palette['primary'], self.color_palette['secondary'], 
                     self.color_palette['success'], self.color_palette['danger']]
            
            for i, (name, data) in enumerate(datasets.items()):
                color = colors[i % len(colors)]
                
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data,
                        mode='lines',
                        name=name,
                        line=dict(color=color, width=2),
                        hovertemplate=f'<b>Date</b>: %{{x}}<br><b>{name}</b>: %{{y:.2f}}<extra></extra>'
                    )
                )
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Value",
                height=500,
                hovermode='x unified'
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating comparison chart: {str(e)}")
            return go.Figure()
    
    def create_gauge_chart(self, value, title="Gauge Chart", min_val=0, max_val=10):
        """Create gauge chart for single metric"""
        try:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': title},
                delta={'reference': (min_val + max_val) / 2},
                gauge={
                    'axis': {'range': [min_val, max_val]},
                    'bar': {'color': self.color_palette['primary']},
                    'steps': [
                        {'range': [min_val, max_val * 0.3], 'color': self.color_palette['success']},
                        {'range': [max_val * 0.3, max_val * 0.7], 'color': self.color_palette['warning']},
                        {'range': [max_val * 0.7, max_val], 'color': self.color_palette['danger']}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': max_val * 0.8
                    }
                }
            ))
            
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating gauge chart: {str(e)}")
            return go.Figure()
