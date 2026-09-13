import os
import pandas as pd
import streamlit as st
import main

# Page Configuration for Mobile & Desktop
st.set_page_config(
    page_title="IntelliNiche — Market Gap Detector",
    page_icon="✨",
    layout="wide"
)

# Dark Aesthetic Custom Styling
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #38BDF8; }
    </style>
""", unsafe_allow_html=True)

DATA_PATH = os.path.join("data", "gap_results.csv")

st.title("✨ IntelliNiche — Market Gap Detector")
st.write("Identify high-demand product opportunities using NLP analysis.")

# File Upload Section
uploaded_file = st.file_uploader("📁 Upload Review CSV File", type=["csv"])

if uploaded_file is not None:
    temp_path = os.path.join("data", "raw_reviews.csv")
    os.makedirs("data", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("Processing dataset... Please wait..."):
        main.run_pipeline_for_file(temp_path)
    st.success("Analysis Complete!")

# Load and Display Data & Graphs
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    top_df = df.head(50)

    # Layout: Two Columns (Metrics/List & Graphs)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Top Ranked Categories")
        selected_category = st.selectbox("Select a Category:", top_df["category"].tolist())
        
        row = top_df[top_df["category"] == selected_category].iloc[0]
        
        # Display Score Cards
        m1, m2, m3 = st.columns(3)
        m1.metric("Demand Score", f"{row['demand_score']:.2f}")
        m2.metric("Supply Score", f"{row['supply_score']:.2f}")
        m3.metric("Gap Score", f"{row['gap_score']:.2f}")

        st.markdown("**Supporting Customer Evidence:**")
        st.info(f"\"{row['evidence_1']}\"")

    with col2:
        st.subheader("Top 5 Market Opportunities")
        top_5 = top_df.head(5)
        st.bar_chart(data=top_5, x="category", y="gap_score", color="#38BDF8")
else:
    st.info("Upload a CSV file to generate market gap analytics.")