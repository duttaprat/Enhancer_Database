import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Functional Genomics Browser",
    page_icon="🧬",
    layout="wide"
)

# Custom CSS
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
    h1 {
        color: #1a1a1a;
        font-weight: 700;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .info-box {
        background: #e0f2fe;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0284c7;
        margin: 1rem 0;
    }
    .clinical-tag {
        background: #dcfce7;
        color: #166534;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data():
    datasets = {
        'Enhancer GOF': pd.read_csv('Enhancer_GOF.csv'),
        'Enhancer LOF': pd.read_csv('Enhancer_LOF.csv'),
        'Non-enhancer GOF': pd.read_csv('Non-enhancer_GOF.csv'),
        'TF Enhancer LOF': pd.read_csv('TF-Enhancer_LOF.csv')
    }
    return datasets

# Initialize session state
if 'datasets' not in st.session_state:
    st.session_state.datasets = load_data()

# Dataset descriptions
dataset_info = {
    'Enhancer GOF': {
        'description': 'Gain-of-Function variants that INCREASE enhancer activity',
        'color': '#10b981',
        'icon': '📈'
    },
    'Enhancer LOF': {
        'description': 'Loss-of-Function variants that DECREASE enhancer activity',
        'color': '#ef4444',
        'icon': '📉'
    },
    'Non-enhancer GOF': {
        'description': 'Variants that CREATE new enhancer activity in non-enhancer regions',
        'color': '#8b5cf6',
        'icon': '✨'
    },
    'TF Enhancer LOF': {
        'description': 'Variants affecting Transcription Factor binding sites',
        'color': '#f59e0b',
        'icon': '🔗'
    }
}

# Sidebar
with st.sidebar:
    st.markdown("### 🧬 Functional Genomics Browser")
    st.markdown("**Variant Impact Analysis**")
    st.divider()
    
    # Dataset selector
    selected_dataset = st.selectbox(
        "Select Dataset",
        list(st.session_state.datasets.keys()),
        format_func=lambda x: f"{dataset_info[x]['icon']} {x}"
    )
    
    st.markdown(f"<div class='info-box'>{dataset_info[selected_dataset]['description']}</div>", 
                unsafe_allow_html=True)
    
    st.divider()
    
    page = st.radio(
        "Navigation",
        ["📊 Browse Data", "📈 Visualize", "🔬 Analysis", "ℹ️ About"],
        label_visibility="collapsed"
    )

# Get current dataset
current_data = st.session_state.datasets[selected_dataset].copy()

# Main content
if page == "📊 Browse Data":
    # Header
    st.title(f"{dataset_info[selected_dataset]['icon']} {selected_dataset}")
    st.markdown(f'<p class="subtitle">{dataset_info[selected_dataset]["description"]}</p>', 
                unsafe_allow_html=True)
    
    # Initialize filtered data
    filtered_data = current_data.copy()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Variants", f"{len(current_data):,}")
    with col2:
        if 'is_clinically_significant' in current_data.columns:
            clin_sig = len(current_data[current_data['is_clinically_significant'] == 'yes'])
            st.metric("Clinically Significant", clin_sig)
        else:
            st.metric("Dataset", selected_dataset.split()[-2])
    with col3:
        if 'chr' in current_data.columns:
            unique_chroms = current_data['chr'].nunique()
            st.metric("Chromosomes", unique_chroms)
        else:
            st.metric("Records", f"{len(current_data):,}")
    with col4:
        # Will update after filtering
        st.metric("Filtered Results", "—")
    
    st.divider()
    
    # Layout: Filters on left, Table on right
    col_filter, col_table = st.columns([1, 3])
    
    with col_filter:
        st.markdown("### 🔍 Filter Data")
        
        # Chromosome filter
        if 'chr' in current_data.columns:
            chromosomes = ['All'] + sorted(current_data['chr'].astype(str).unique().tolist())
            selected_chromosome = st.selectbox("Chromosome", chromosomes)
            if selected_chromosome != 'All':
                filtered_data = filtered_data[filtered_data['chr'].astype(str) == selected_chromosome]
        
        # Position range filter
        if 'variant_start' in current_data.columns:
            st.markdown("**Position Range**")
            min_pos = int(current_data['variant_start'].min())
            max_pos = int(current_data['variant_end'].max())
            
            pos_range = st.slider(
                "Select Range",
                min_value=min_pos,
                max_value=max_pos,
                value=(min_pos, max_pos),
                format="%d"
            )
            filtered_data = filtered_data[
                (filtered_data['variant_start'] >= pos_range[0]) & 
                (filtered_data['variant_end'] <= pos_range[1])
            ]
        
        # ScoreChange filter
        if 'ScoreChange' in current_data.columns:
            st.markdown("**Score Change**")
            score_min = float(current_data['ScoreChange'].min())
            score_max = float(current_data['ScoreChange'].max())
            
            score_range = st.slider(
                "Score Range",
                min_value=score_min,
                max_value=score_max,
                value=(score_min, score_max),
                format="%.3f"
            )
            filtered_data = filtered_data[
                (filtered_data['ScoreChange'] >= score_range[0]) & 
                (filtered_data['ScoreChange'] <= score_range[1])
            ]
        
        # Clinical significance filter
        if 'is_clinically_significant' in current_data.columns:
            clin_filter = st.radio(
                "Clinical Significance",
                ["All", "Yes only", "No only"]
            )
            if clin_filter == "Yes only":
                filtered_data = filtered_data[filtered_data['is_clinically_significant'] == 'yes']
            elif clin_filter == "No only":
                filtered_data = filtered_data[filtered_data['is_clinically_significant'] == 'no']
        
        # Transcription Factor filter (TF dataset only)
        if 'transcription_factor' in current_data.columns:
            tfs = ['All'] + sorted(current_data['transcription_factor'].unique().tolist())
            selected_tf = st.selectbox("Transcription Factor", tfs)
            if selected_tf != 'All':
                filtered_data = filtered_data[filtered_data['transcription_factor'] == selected_tf]
        
        # External links filter
        if 'gwas_url' in current_data.columns:
            st.markdown("**Has External Links**")
            if st.checkbox("GWAS"):
                filtered_data = filtered_data[filtered_data['gwas_url'] != '-']
            if st.checkbox("ClinVar"):
                filtered_data = filtered_data[filtered_data['clinvar_url'] != '-']
            if st.checkbox("eQTL"):
                filtered_data = filtered_data[filtered_data['eqtl_url'] != '-']
        
        # Search by dbSNP ID
        if 'dbsnp_id' in current_data.columns:
            search_term = st.text_input("Search dbSNP ID", placeholder="rs...")
            if search_term:
                filtered_data = filtered_data[
                    filtered_data['dbsnp_id'].str.contains(search_term, case=False, na=False)
                ]
        
        # Reset button
        if st.button("❌ Reset Filters", use_container_width=True):
            st.rerun()
    
    with col_table:
        # Update filtered results metric
        col4.metric("Filtered Results", f"{len(filtered_data):,}")
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label=f"⬇️ Download Filtered Data ({len(filtered_data):,} variants)",
            data=csv,
            file_name=f"{selected_dataset.replace(' ', '_')}_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Display table with appropriate columns
        if selected_dataset == 'TF Enhancer LOF':
            display_cols = ['transcription_factor', 'chr', 'dbsnp_id', 'variant_start', 
                          'reference_nucleotide', 'alternative_nucleotide', 'ScoreChange', 'LogOddRatio']
        else:
            display_cols = ['chr', 'dbsnp_id', 'variant_start', 'variant_end',
                          'reference_nucleotide', 'alternative_nucleotide', 'ScoreChange', 
                          'is_clinically_significant']
        
        # Only show columns that exist
        display_cols = [col for col in display_cols if col in filtered_data.columns]
        
        st.dataframe(
            filtered_data[display_cols],
            use_container_width=True,
            height=600,
            hide_index=True
        )

elif page == "📈 Visualize":
    st.title("Data Visualization")
    st.markdown(f"Visualizing patterns in **{selected_dataset}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ScoreChange distribution
        st.subheader("Score Change Distribution")
        if 'ScoreChange' in current_data.columns:
            fig = go.Figure(data=[
                go.Histogram(
                    x=current_data['ScoreChange'], 
                    marker_color=dataset_info[selected_dataset]['color'],
                    nbinsx=30
                )
            ])
            fig.update_layout(
                xaxis_title="Score Change",
                yaxis_title="Count",
                height=350,
                template="plotly_white",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ScoreChange data available")
    
    with col2:
        # Chromosome distribution
        st.subheader("Variants per Chromosome")
        if 'chr' in current_data.columns:
            chrom_counts = current_data['chr'].value_counts().sort_index()
            fig = go.Figure(data=[
                go.Bar(
                    x=chrom_counts.index.astype(str), 
                    y=chrom_counts.values, 
                    marker_color=dataset_info[selected_dataset]['color']
                )
            ])
            fig.update_layout(
                xaxis_title="Chromosome",
                yaxis_title="Number of Variants",
                height=350,
                template="plotly_white",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Clinical significance (if available)
    if 'is_clinically_significant' in current_data.columns:
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Clinical Significance")
            clin_counts = current_data['is_clinically_significant'].value_counts()
            fig = go.Figure(data=[
                go.Pie(
                    labels=clin_counts.index,
                    values=clin_counts.values,
                    marker=dict(colors=['#10b981', '#94a3b8']),
                    hole=0.4
                )
            ])
            fig.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            st.subheader("External Database Links")
            link_data = {
                'Database': ['GWAS', 'ClinVar', 'eQTL'],
                'Count': [
                    len(current_data[current_data['gwas_url'] != '-']),
                    len(current_data[current_data['clinvar_url'] != '-']),
                    len(current_data[current_data['eqtl_url'] != '-'])
                ]
            }
            fig = go.Figure(data=[
                go.Bar(
                    x=link_data['Database'],
                    y=link_data['Count'],
                    marker_color=['#3b82f6', '#8b5cf6', '#f59e0b']
                )
            ])
            fig.update_layout(
                yaxis_title="Number of Links",
                height=350,
                template="plotly_white",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # TF-specific visualization
    if 'transcription_factor' in current_data.columns:
        st.subheader("Top Transcription Factors")
        tf_counts = current_data['transcription_factor'].value_counts().head(15)
        fig = go.Figure(data=[
            go.Bar(
                y=tf_counts.index,
                x=tf_counts.values,
                orientation='h',
                marker_color=dataset_info[selected_dataset]['color']
            )
        ])
        fig.update_layout(
            xaxis_title="Number of Variants",
            yaxis_title="Transcription Factor",
            height=500,
            template="plotly_white",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "🔬 Analysis":
    st.title("Comparative Analysis")
    st.markdown("Compare functional impacts across datasets")
    
    # Summary statistics
    st.subheader("Dataset Overview")
    
    summary_data = []
    for name, df in st.session_state.datasets.items():
        row = {
            'Dataset': name,
            'Total Variants': len(df),
            'Chromosomes': df['chr'].nunique() if 'chr' in df.columns else 'N/A'
        }
        
        if 'ScoreChange' in df.columns:
            row['Avg Score Change'] = f"{df['ScoreChange'].mean():.3f}"
            row['Score Range'] = f"{df['ScoreChange'].min():.3f} to {df['ScoreChange'].max():.3f}"
        
        if 'is_clinically_significant' in df.columns:
            row['Clinical Sig'] = len(df[df['is_clinically_significant'] == 'yes'])
        
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Comparative Score Change Distribution
    st.subheader("Score Change Comparison")
    
    fig = go.Figure()
    for name, df in st.session_state.datasets.items():
        if 'ScoreChange' in df.columns:
            fig.add_trace(go.Box(
                y=df['ScoreChange'],
                name=name,
                marker_color=dataset_info[name]['color']
            ))
    
    fig.update_layout(
        yaxis_title="Score Change",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    st.subheader("Key Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Gain-of-Function (GOF)**
        - Positive ScoreChange values
        - Increases regulatory activity
        - May enhance gene expression
        """)
    
    with col2:
        st.markdown("""
        **Loss-of-Function (LOF)**
        - Negative ScoreChange values
        - Decreases regulatory activity
        - May reduce gene expression
        """)

else:  # About page
    st.title("About")
    st.markdown("""
    ### Functional Genomics Browser
    
    This application provides comprehensive analysis of genomic variants with functional predictions.
    
    **Datasets:**
    
    1. **Enhancer GOF** (1,918 variants)
       - Variants that increase enhancer activity
       - Positive score changes indicate gain of function
    
    2. **Enhancer LOF** (2,681 variants)
       - Variants that decrease enhancer activity
       - Negative score changes indicate loss of function
    
    3. **Non-enhancer GOF** (5,468 variants)
       - Variants creating new enhancer activity
       - Occurs in regions not normally active as enhancers
    
    4. **TF Enhancer LOF** (9,417 variants)
       - Variants affecting transcription factor binding
       - Includes 301 unique transcription factors
    
    **Features:**
    - Advanced filtering by chromosome, position, score change
    - Clinical significance filtering
    - External database links (GWAS, ClinVar, eQTL)
    - Transcription factor analysis
    - Comparative visualizations
    - Downloadable filtered results
    
    **Interpretation:**
    - **ScoreChange**: Magnitude of functional impact
    - **LogOddRatio**: Statistical confidence in prediction
    - **Clinical Significance**: Known disease associations
    
    Built with Streamlit 🎈
    """)