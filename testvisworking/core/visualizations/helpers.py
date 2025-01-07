"""Helper functions for visualization-related operations"""

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional, Tuple

def validate_columns(df: pd.DataFrame, columns: List[str]) -> Tuple[bool, str]:
    """Validate that required columns exist in the DataFrame"""
    missing = [col for col in columns if col not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    return True, ""

def validate_numeric_columns(df: pd.DataFrame, columns: List[str]) -> Tuple[bool, str]:
    """Validate that specified columns contain numeric data"""
    non_numeric = [col for col in columns if not pd.api.types.is_numeric_dtype(df[col])]
    if non_numeric:
        return False, f"Non-numeric columns: {', '.join(non_numeric)}"
    return True, ""

def apply_aggregation(df: pd.DataFrame, group_cols: List[str], y_col: str, agg_func: str) -> pd.DataFrame:
    """Apply aggregation to the DataFrame based on specified function"""
    if agg_func == "count":
        return df.groupby(group_cols).size().reset_index(name=y_col)
    return df.groupby(group_cols)[y_col].agg(agg_func).reset_index()

def apply_filters(df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
    """Apply filters to the DataFrame"""
    if not filters:
        return df
        
    df_filtered = df.copy()
    for f in filters:
        col, op, val = f['column'], f['operator'], f['value']
        if op == '==':
            df_filtered = df_filtered[df_filtered[col] == val]
        elif op == '!=':
            df_filtered = df_filtered[df_filtered[col] != val]
        elif op == '>':
            df_filtered = df_filtered[df_filtered[col] > float(val)]
        elif op == '<':
            df_filtered = df_filtered[df_filtered[col] < float(val)]
        elif op == 'contains':
            df_filtered = df_filtered[df_filtered[col].str.contains(val, case=False)]
        elif op == 'between':
            low, high = val
            df_filtered = df_filtered[(df_filtered[col] >= low) & (df_filtered[col] <= high)]
    
    return df_filtered

def create_plotly_figure(
    df: pd.DataFrame,
    viz_type: str,
    x_col: str,
    y_col: Optional[str] = None,
    color_col: Optional[str] = None,
    **kwargs
) -> go.Figure:
    """Create a Plotly figure based on the specified visualization type"""
    
    # Basic chart parameters
    chart_params = {
        'data_frame': df,
        'x': x_col,
        'title': kwargs.get('title', f'{viz_type.title()} Chart'),
        'height': kwargs.get('height', 500),
    }
    
    if y_col:
        chart_params['y'] = y_col
    
    if color_col:
        chart_params['color'] = color_col
    
    # Handle specific chart types
    if viz_type == 'scatter':
        fig = px.scatter(**chart_params)
    elif viz_type == 'line':
        fig = px.line(**chart_params)
    elif viz_type == 'bar':
        fig = px.bar(**chart_params)
    elif viz_type == 'area':
        fig = px.area(**chart_params)
    elif viz_type == 'histogram':
        fig = px.histogram(**chart_params)
    elif viz_type == 'box':
        fig = px.box(**chart_params)
    elif viz_type == 'violin':
        fig = px.violin(**chart_params)
    else:
        raise ValueError(f"Unsupported visualization type: {viz_type}")
    
    # Apply any custom layout updates
    layout_updates = kwargs.get('layout_updates', {})
    fig.update_layout(**layout_updates)
    
    return fig

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to be safe for filesystem operations"""
    # Remove potentially dangerous characters
    safe_chars = "".join(c if c.isalnum() or c in "._- " else "_" for c in filename)
    return safe_chars.strip()

def get_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """Get the data types of DataFrame columns in a human-readable format"""
    type_map = {
        'int64': 'integer',
        'float64': 'decimal',
        'object': 'text',
        'bool': 'boolean',
        'datetime64[ns]': 'date/time',
        'category': 'category'
    }
    return {col: type_map.get(str(dtype), str(dtype)) for col, dtype in df.dtypes.items()}

def get_column_stats(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """Get basic statistics for specified columns"""
    if columns is None:
        columns = df.columns.tolist()
    
    stats = {}
    for col in columns:
        col_stats = {
            'type': str(df[col].dtype),
            'missing': int(df[col].isna().sum()),
            'unique': int(df[col].nunique())
        }
        
        if pd.api.types.is_numeric_dtype(df[col]):
            col_stats.update({
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'mean': float(df[col].mean()),
                'median': float(df[col].median())
            })
        elif pd.api.types.is_string_dtype(df[col]):
            col_stats['sample_values'] = df[col].dropna().sample(min(5, len(df))).tolist()
            
        stats[col] = col_stats
    
    return stats