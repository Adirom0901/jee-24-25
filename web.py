import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

# Page layout
st.set_page_config(layout="wide")
st.title("📊 Actual vs Predicted JoSAA Closing Ranks (2024 vs 2025)")
st.markdown(
    """
    <a href="https://collegemap.in/" target="_blank">
        <img src="https://collegemap.in/static/media/collegeMapLogo.a38ff4563b8339e9f214.png" alt="Company Logo" style="height:100px;">
    </a>
    """,
    unsafe_allow_html=True
)
# Load files directly
actual_file = pd.read_csv('josaa_closing_ranks_2024.csv')
predicted_file = pd.read_excel('cr_25_corrected (1).xlsx')

@st.cache_data
def load_data(actual_df, predicted_df):
    actual_df = actual_df.rename(columns={"Closing Rank": "Actual Closing Rank"})
    predicted_df = predicted_df.rename(columns={"Closing Rank 2025": "Predicted Closing Rank 2025"})

    merged_df = pd.merge(
        actual_df,
        predicted_df,
        on=["Institute", "Academic Program Name", "Seat Type", "Gender"],
        how="inner"
    )
    return merged_df

# Load merged dataset
df_merged = load_data(actual_file, predicted_file)

# Sidebar filters
st.sidebar.header("🎯 Filter Options")
selected_institute = st.sidebar.selectbox("Select Institute", sorted(df_merged["Institute"].unique()))
selected_seat_type = st.sidebar.selectbox("Select Seat Type", sorted(df_merged["Seat Type"].unique()))
selected_gender = st.sidebar.selectbox("Select Gender", sorted(df_merged["Gender"].unique()))

# Filter data
df_filtered = df_merged[
    (df_merged["Institute"] == selected_institute) &
    (df_merged["Seat Type"] == selected_seat_type) &
    (df_merged["Gender"] == selected_gender)
]

# Clean data
df_filtered["Actual Closing Rank"] = pd.to_numeric(df_filtered["Actual Closing Rank"], errors='coerce')
df_filtered["Predicted Closing Rank 2025"] = pd.to_numeric(df_filtered["Predicted Closing Rank 2025"], errors='coerce')
df_filtered = df_filtered.replace(999999, np.nan).dropna(subset=["Actual Closing Rank", "Predicted Closing Rank 2025"])
df_filtered = df_filtered.sort_values("Actual Closing Rank")

if df_filtered.empty:
    st.warning("⚠️ No data available for the selected filters.")
else:
    # Show filtered table
    st.subheader("📋 Filtered Data Table")
    st.dataframe(df_filtered[[
        "Academic Program Name", "Actual Closing Rank", "Predicted Closing Rank 2025"
    ]].reset_index(drop=True), use_container_width=True)

    # Bar chart
    st.subheader("📈 Comparison Chart")
    fig, ax = plt.subplots(figsize=(20, 20))
    index = np.arange(len(df_filtered))
    width = 0.35

    ax.bar(index - width/2, df_filtered["Actual Closing Rank"], width, label="Actual 2024", color='blue', alpha=0.7)
    ax.bar(index + width/2, df_filtered["Predicted Closing Rank 2025"], width, label="Predicted 2025", color='orange', alpha=0.7)

    ax.set_xlabel("Academic Programs")
    ax.set_ylabel("Closing Ranks")
    ax.set_title(f"Actual vs Predicted Closing Ranks - {selected_institute}")
    ax.set_xticks(index)
    ax.set_xticklabels(df_filtered["Academic Program Name"], rotation=90)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{int(y):,}'))
    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

    plt.tight_layout()
    st.pyplot(fig)

