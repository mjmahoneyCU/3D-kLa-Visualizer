import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from scipy import interpolate # For interpolating scattered data onto a grid
import os

st.set_page_config(layout="wide") # Use wide layout for better plot display

# --- App Title ---
st.title("KLa 3D Visualization App")
st.markdown("Upload your KLa data to visualize the mass transfer coefficient as a 3D surface!")

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose your KLa data CSV file (e.g., kladata.csv)", type="csv")

if uploaded_file is not None:
    # Read the uploaded CSV file
    try:
        df_kla = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        st.dataframe(df_kla.head()) # Display first few rows of the dataframe
    except Exception as e:
        st.error(f"Error reading file: {e}. Please ensure it's a valid CSV.")
        st.stop() # Stop execution if file cannot be read

    # --- Section: Prepare Data for 3D Plotting ---
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

    # Validate selected columns are numeric
    if not all(pd.api.types.is_numeric_dtype(df_kla[col]) for col in [x_column_name, y_column_name, z_column_name]):
        st.error("Selected columns must contain numeric data. Please check your data.")
        st.stop()

    X_data = df_kla[x_column_name].to_numpy()
    Y_data = df_kla[y_column_name].to_numpy()
    Z_data = df_kla[z_column_name].to_numpy()

    # --- Interpolate scattered data onto a regular grid for a smoother surface ---
    # Define a grid for interpolation
    # Adjust resolution (e.g., 50) for smoother or finer mesh
    grid_res = 50
    xi = np.linspace(X_data.min(), X_data.max(), grid_res)
    yi = np.linspace(Y_data.min(), Y_data.max(), grid_res)
    
    # Create a 2D meshgrid
    Xi, Yi = np.meshgrid(xi, yi)

    # Interpolate Z_data onto the new grid
    # method can be 'linear', 'nearest', 'cubic'
    Zi = interpolate.griddata((X_data, Y_data), Z_data, (Xi, Yi), method='cubic')
    
    # Handle NaNs that might occur if grid points are outside convex hull of data points
    Zi[np.isnan(Zi)] = 0 # Or a more suitable placeholder if desired, e.g., extrapolate, or filter data before interpolation

    # --- Section: Create Interactive 3D Surface Plot (using Plotly) ---

    # Create a directory to save static plots if needed (not directly used by Streamlit)
    plots_dir = "kla_3d_plotly_plots"
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
        st.sidebar.info(f"Created directory: {plots_dir} for plot saving if needed.")


    # Create the 3D surface trace using the interpolated (gridded) data
    surface_trace = go.Surface(
        x=Xi, # Use interpolated grid for X
        y=Yi, # Use interpolated grid for Y
        z=Zi, # Use interpolated grid for Z
        colorscale='Viridis', # Color scheme for the surface
        # Make mesh lines visible along all axes
        contours_z=dict(
            show=True,
            usecolormap=True,
            highlightcolor="white",
            project_z=True,
            start=np.min(Z_data), end=np.max(Z_data), size=(np.max(Z_data)-np.min(Z_data))/20 # Increased density
        ),
        contours_x=dict(
            show=True,
            usecolormap=False, # Don't use color map for X-contours
            highlightcolor="lightgrey", # Highlight X contours
            project_x=True,
            start=np.min(X_data), end=np.max(X_data), size=(np.max(X_data)-np.min(X_data))/10
        ),
        contours_y=dict(
            show=True,
            usecolormap=False, # Don't use color map for Y-contours
            highlightcolor="lightgrey", # Highlight Y contours
            project_y=True,
            start=np.min(Y_data), end=np.max(Y_data), size=(np.max(Y_data)-np.min(Y_data))/10
        ),
        showscale=True, # Show color scale for the surface
        name='KLa Surface',
        opacity=0.9 # Slightly transparent to see points underneath
    )

    # Create a scatter trace for the individual data points (red dots)
    scatter_trace = go.Scatter3d(
        x=X_data,
        y=Y_data,
        z=Z_data,
        mode='markers', # Show as markers
        marker=dict(
            size=5,
            color='red', # Red color for data points
            opacity=1.0
        ),
        name='Data Points' # Name for legend
    )

    # Create the figure object and add the traces
    fig = go.Figure(data=[surface_trace, scatter_trace])

    # Update layout for axis labels and title
    fig.update_layout(
        scene=dict(
            xaxis_title=x_column_name,
            yaxis_title=y_column_name,
            zaxis_title=z_column_name,
            # Ensure grid lines are visible for mesh effect if desired on axes
            xaxis=dict(showgrid=True, gridcolor="lightgrey"),
            yaxis=dict(showgrid=True, gridcolor="lightgrey"),
            zaxis=dict(showgrid=True, gridcolor="lightgrey"),
        ),
        title_text=f'{z_column_name} vs. {x_column_name} and {y_column_name}',
        showlegend=True,
        height=700 # Adjust height for better display
    )

    # --- Display Plotly chart in Streamlit ---
    st.plotly_chart(fig, use_container_width=True)

    st.success("Interactive 3D plot generated! You can rotate, zoom, and pan with your mouse.")

else:
    st.info("Please upload your KLa data CSV file to generate the 3D plot.")

