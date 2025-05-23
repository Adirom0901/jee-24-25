import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

st.set_page_config(layout="wide")
st.title("Actual vs Predicted JoSAA Closing Ranks (2024 vs 2025)")

# Upload files
actual_file = pd.read_csv('josaa_closing_ranks_2024.csv')
predicted_file = pd.read_excel('cr_25_corrected (1).xlsx')

@st.cache_data
def load_data(actual_file, predicted_file):
    actual_df = pd.read_csv(actual_file)
    predicted_df = pd.read_excel(predicted_file)

    actual_df.rename(columns={"Closing Rank": "Actual Closing Rank"}, inplace=True)
    predicted_df.rename(columns={"Closing Rank 2025": "Predicted Closing Rank 2025"}, inplace=True)

    merged_df = pd.merge(
        actual_df,
        predicted_df,
        on=["Institute", "Academic Program Name", "Seat Type", "Gender"],
        how="inner"
    )
    return merged_df

if actual_file and predicted_file:
    df_merged = load_data(actual_file, predicted_file)

    # Sidebar Filters
    institutes = df_merged["Institute"].unique()
    seat_types = df_merged["Seat Type"].unique()
    genders = df_merged["Gender"].unique()

    selected_institute = st.sidebar.selectbox("Select Institute", sorted(institutes))
    selected_seat_type = st.sidebar.selectbox("Select Seat Type", sorted(seat_types))
    selected_gender = st.sidebar.selectbox("Select Gender", sorted(genders))

    # Filter Data
    df_filtered = df_merged[
        (df_merged["Institute"] == selected_institute) &
        (df_merged["Seat Type"] == selected_seat_type) &
        (df_merged["Gender"] == selected_gender)
    ]
    df_filtered["Actual Closing Rank"] = pd.to_numeric(df_filtered["Actual Closing Rank"], errors='coerce')
    df_filtered["Predicted Closing Rank 2025"] = pd.to_numeric(df_filtered["Predicted Closing Rank 2025"], errors='coerce')

    df_filtered = df_filtered.replace(999999, np.nan).dropna(subset=["Actual Closing Rank", "Predicted Closing Rank 2025"])
    df_filtered = df_filtered.sort_values("Actual Closing Rank")

    if df_filtered.empty:
        st.warning("⚠️ No data available for the selected filters.")
    else:
        fig, ax = plt.subplots(figsize=(20, 10))
        index = np.arange(len(df_filtered))
        width = 0.3

        ax.bar(index - width/2, df_filtered["Actual Closing Rank"], width, label="Actual 2024", alpha=0.7, color='blue')
        ax.bar(index + width/2, df_filtered["Predicted Closing Rank 2025"], width, label="Predicted 2025", alpha=0.7, color='orange')

        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{int(y):,}'))
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

        ax.set_xlabel("Academic Programs")
        ax.set_ylabel("Closing Ranks")
        ax.set_title(f"Actual vs Predicted Ranks - {selected_institute}")
        ax.set_xticks(index)
        ax.set_xticklabels(df_filtered["Academic Program Name"], rotation=90)
        ax.legend()

        plt.tight_layout()
        st.pyplot(fig)
else:
    st.info("👈 Please upload both the actual and predicted rank files to begin.")
