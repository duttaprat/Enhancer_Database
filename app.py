import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="GenomicsBrowser",
    page_icon="🧬",
    layout="wide"
)

# Custom CSS to match Base44 design
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background-color: #f8f9fa;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1a1a1a;
        font-weight: 700;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data():
    df = pd.read_csv('subset_enhancer.csv')
    return df

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# Sidebar
with st.sidebar:
    st.markdown("### 🧬 GenomicsBrowser")
    st.markdown("**Enhancer Research Platform**")
    st.divider()
    
    page = st.radio(
        "Navigation",
        ["📊 Browse Data", "📈 Visualize", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.markdown("### Dataset Info")
    st.markdown("**Public Access:** Open")
    st.markdown("**Version:** 2024.1")

# Main content
if page == "📊 Browse Data":
    # Header
    st.title("Enhancer Region Browser")
    st.markdown('<p class="subtitle">Explore and download genomic enhancer data with advanced filtering</p>', 
                unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Regions", len(st.session_state.data))
    with col2:
        st.metric("Filtered Results", len(st.session_state.data))
    with col3:
        unique_chroms = st.session_state.data['Chromosome'].nunique()
        st.metric("Chromosomes", unique_chroms)
    
    st.divider()
    
    # Layout: Filters on left, Table on right
    col_filter, col_table = st.columns([1, 3])
    
    with col_filter:
        st.markdown("### 🔍 Filter Data")
        
        # Chromosome filter
        chromosomes = ['All'] + sorted(st.session_state.data['Chromosome'].unique().tolist())
        selected_chromosome = st.selectbox("Chromosome", chromosomes)
        
        # Position range
        st.markdown("**Position Range**")
        col_start, col_end = st.columns(2)
        with col_start:
            start_pos = st.number_input("Start", value=0, step=1000)
        with col_end:
            end_pos = st.number_input("End", value=1000000, step=1000)
        
        # Variant Type filter
        variant_types = ['All variants'] + st.session_state.data['Variant_Type'].unique().tolist()
        selected_variant = st.selectbox("Variant Type", variant_types)
        
        # Predicted Effect (placeholder)
        st.selectbox("Predicted Effect", ["All effects"])
        
        # Search
        search_term = st.text_input("Search", placeholder="Search by target genes...")
        
        # Reset button
        if st.button("❌ Reset Filters", use_container_width=True):
            st.rerun()
    
    with col_table:
        # Apply filters
        filtered_data = st.session_state.data.copy()
        
        if selected_chromosome != 'All':
            filtered_data = filtered_data[filtered_data['Chromosome'] == selected_chromosome]
        
        filtered_data = filtered_data[
            (filtered_data['Start'] >= start_pos) & 
            (filtered_data['End'] <= end_pos)
        ]
        
        if selected_variant != 'All variants':
            filtered_data = filtered_data[filtered_data['Variant_Type'] == selected_variant]
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label=f"⬇️ Download CSV ({len(filtered_data)})",
            data=csv,
            file_name="genomics_data.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Display table with custom styling
        st.dataframe(
            filtered_data[['Chromosome', 'Start', 'End', 'dbSNP_ID', 'Variant_Type', 
                          'Quality_Score', 'Enhancer_Length', 'Patient_Count']],
            use_container_width=True,
            height=600,
            hide_index=True
        )

elif page == "📈 Visualize":
    st.title("Data Visualization")
    st.markdown("Visualize genomic data patterns and distributions")
    
    # Chromosome distribution chart
    st.subheader("Variants per Chromosome")
    chrom_counts = st.session_state.data['Chromosome'].value_counts().sort_index()
    
    fig = go.Figure(data=[
        go.Bar(x=chrom_counts.index, y=chrom_counts.values, marker_color='#8b5cf6')
    ])
    fig.update_layout(
        xaxis_title="Chromosome",
        yaxis_title="Number of Variants",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Enhancer length distribution
    st.subheader("Enhancer Length Distribution")
    fig2 = go.Figure(data=[
        go.Histogram(x=st.session_state.data['Enhancer_Length'], 
                     marker_color='#06b6d4', nbinsx=20)
    ])
    fig2.update_layout(
        xaxis_title="Enhancer Length (bp)",
        yaxis_title="Count",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig2, use_container_width=True)

else:  # About page
    st.title("About")
    st.markdown("""
    ### Enhancer Region Browser
    
    This application provides an interface for exploring genomic enhancer regions with 
    advanced filtering and visualization capabilities.
    
    **Features:**
    - Browse and filter genomic data
    - Download filtered results
    - Visualize data distributions
    - Search by various genomic parameters
    
    **Data Structure:**
    The application works with genomic variant data including:
    - Chromosome positions
    - dbSNP IDs
    - Variant types and annotations
    - Enhancer regions and scores
    - Patient counts
    
    Built with Streamlit 🎈
    """)