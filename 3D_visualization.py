import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy import interpolate
import io
import os

st.set_page_config(layout="wide")

st.title("KLa 3D Visualization App")
st.markdown("Paste your KLa data below (including headers) and click **Generate Plot**.")

pasted_data = st.text_area("Paste your CSV-style data here:", height=250)

if st.button("Generate Plot"):
    if pasted_data.strip() == "":
        st.warning("Please paste your data first.")
        st.stop()

    try:
        df_kla = pd.read_csv(io.StringIO(pasted_data))
        st.success("Data parsed successfully!")
        st.dataframe(df_kla.head())
    except Exception as e:
        st.error(f"Error reading data: {e}. Please check formatting (commas between columns).")
        st.stop()

    x_column_name = st.selectbox(
        "Select Agitation Rate Column (X-axis)",
        options=df_kla.columns.tolist(),
        index=df_kla.columns.tolist().index('Agitation RPM') if 'Agitation RPM' in df_kla.columns else 0
    )
    y_column_name = st.selectbox(
        "Select Gas Flow Rate Column (Y-axis)",
        options=df_kla.columns.tolist(),
        index=df_kla.columns.tolist().index('Gas Flow (L/min)') if 'Gas Flow (L/min)' in df_kla.columns else 0
    )
    z_column_name = st.selectbox(
        "Select KLa Column (Z-axis)",
        options=df_kla.columns.tolist(),
        index=df_kla.columns.tolist().index('kLa (s-1)') if 'kLa (s-1)' in df_kla.columns else 0
    )

    if not all(pd.api.types.is_numeric_dtype(df_kla[col]) for col in [x_column_name, y_column_name, z_column_name]):
        st.error("Selected columns must contain numeric data. Please check your data.")
        st.stop()

    X_data = df_kla[x_column_name].to_numpy()
    Y_data = df_kla[y_column_name].to_numpy()
    Z_data = df_kla[z_column_name].to_numpy()

    grid_res = 50
    xi = np.linspace(X_data.min(), X_data.max(), grid_res)
    yi = np.linspace(Y_data.min(), Y_data.max(), grid_res)
    Xi, Yi = np.meshgrid(xi, yi)
    Zi = interpolate.griddata((X_data, Y_data), Z_data, (Xi, Yi), method='cubic')
    Zi[np.isnan(Zi)] = 0

    surface_trace = go.Surface(
        x=Xi,
        y=Yi,
        z=Zi,
        colorscale='Viridis',
        contours_z=dict(
            show=True,
            usecolormap=True,
            highlightcolor="white",
            project_z=True
        ),
        opacity=0.9,
        name='Interpolated Surface'
    )

    scatter_trace = go.Scatter3d(
        x=X_data,
        y=Y_data,
        z=Z_data,
        mode='markers',
        marker=dict(size=5, color='red', opacity=1.0),
        name='Data Points'
    )

    fig = go.Figure(data=[surface_trace, scatter_trace])

    fig.update_layout(
        scene=dict(
            xaxis_title=x_column_name,
            yaxis_title=y_column_name,
            zaxis_title=z_column_name,
            xaxis=dict(showgrid=True, gridcolor="lightgrey"),
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            zaxis=dict(showgrid=True, gridcolor="lightgrey"),
        ),
        title_text=f'{z_column_name} vs. {x_column_name} and {y_column_name}',
        showlegend=True,
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)
    st.success("Interactive 3D plot generated! You can rotate, zoom, and pan with your mouse.")

else:
    st.info("Paste your data above and click **Generate Plot** to create the 3D visualization.")
