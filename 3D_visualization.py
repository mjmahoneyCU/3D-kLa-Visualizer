import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy import interpolate

st.set_page_config(layout="wide")

# --- App Title ---
st.title("KLa 3D Visualization App")
st.markdown("""
Paste or type your KLa data directly into the table below.  
Each row should contain: **Agitation (RPM)**, **Gas Flow (SLPM)**, and **kLa (h⁻¹)**.
""")

# --- Initialize default empty DataFrame for data entry ---
default_data = pd.DataFrame({
    "Agitation (RPM)": [300, 450, 600],
    "Gas Flow (SLPM)": [1.0, 2.0, 3.0],
    "kLa (h⁻¹)": [150, 220, 310]
})

# --- Data Editor (spreadsheet-style input) ---
df_input = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    key="kla_input_table"
)

# --- Generate Plot Button ---
if st.button("Generate 3D Plot"):
    # Validate numeric data
    try:
        df_kla = df_input.astype(float)
    except Exception:
        st.error("All entries must be numeric. Please correct the data.")
        st.stop()

    if df_kla.shape[0] < 3:
        st.warning("Please provide at least three data points for interpolation.")
        st.stop()

    # Extract columns
    X_data = df_kla["Agitation (RPM)"].to_numpy()
    Y_data = df_kla["Gas Flow (SLPM)"].to_numpy()
    Z_data = df_kla["kLa (h⁻¹)"].to_numpy()

    # --- Interpolate onto a grid ---
    grid_res = 50
    xi = np.linspace(X_data.min(), X_data.max(), grid_res)
    yi = np.linspace(Y_data.min(), Y_data.max(), grid_res)
    Xi, Yi = np.meshgrid(xi, yi)
    Zi = interpolate.griddata((X_data, Y_data), Z_data, (Xi, Yi), method='cubic')
    Zi[np.isnan(Zi)] = 0

    # --- Create 3D surface and scatter plot ---
    surface_trace = go.Surface(
        x=Xi,
        y=Yi,
        z=Zi,
        colorscale='Viridis',
        opacity=0.9,
        contours_z=dict(show=True, usecolormap=True, project_z=True),
        name="Interpolated Surface"
    )

    scatter_trace = go.Scatter3d(
        x=X_data,
        y=Y_data,
        z=Z_data,
        mode="markers",
        marker=dict(size=5, color="red", opacity=1.0),
        name="Data Points"
    )

    fig = go.Figure(data=[surface_trace, scatter_trace])
    fig.update_layout(
        scene=dict(
            xaxis_title="Agitation (RPM)",
            yaxis_title="Gas Flow (SLPM)",
            zaxis_title="kLa (h⁻¹)",
            xaxis=dict(showgrid=True, gridcolor="lightgrey"),
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            zaxis=dict(showgrid=True, gridcolor="lightgrey"),
        ),
        title_text="kLa (h⁻¹) vs. Agitation (RPM) and Gas Flow (SLPM)",
        showlegend=True,
        height=700
    )

    # --- Display Plot ---
    st.plotly_chart(fig, use_container_width=True)
    st.success("Interactive 3D plot generated! You can rotate, zoom, and pan with your mouse.")

else:
    st.info("Enter or paste your data above, then click **Generate 3D Plot** to visualize kLa.")
