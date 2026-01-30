import streamlit as st
import pandas as pd

# Load full datasets
coeff = pd.read_csv("coefficients_full.csv")
refs = pd.read_csv("ref_ranges_full.csv")

st.set_page_config(page_title="Tumor Marker Harmonization Tool", layout="centered")
st.title("🔬 Tumor Marker Converter — Multi-Platform Harmonization")

# User selects marker
marker = st.selectbox("Select Tumor Marker", sorted(coeff["marker"].unique()))

# Filter platform options based on selected marker
platform_options = coeff[coeff["marker"] == marker]
source_platform = st.selectbox("Source Platform", sorted(platform_options["source_platform"].unique()))
target_platforms = platform_options[platform_options["source_platform"] == source_platform]["target_platform"].unique()
target_platform = st.selectbox("Target Platform", sorted(target_platforms))

# Input value
value = st.number_input("Enter Measured Value", min_value=0.0, value=10.0, format="%.2f")

# Lookup conversion coefficients
row = coeff[(coeff["marker"] == marker) & (coeff["source_platform"] == source_platform) & (coeff["target_platform"] == target_platform)]
if not row.empty:
    slope = row.iloc[0]["slope"]
    intercept = row.iloc[0]["intercept"]
    converted = slope * value + intercept
    st.metric("Converted Value", f"{converted:.2f}")

    # Reference range lookup and interpretation
    ref_row = refs[(refs["marker"] == marker) & (refs["platform"] == target_platform)]
    if not ref_row.empty:
        low = ref_row.iloc[0]["lower_ref"]
        high = ref_row.iloc[0]["upper_ref"]
        units = ref_row.iloc[0]["units"]
        st.write(f"Reference Range on {target_platform}: **{low} – {high} {units}**")
        if converted < low:
            st.warning("Interpretation: Below normal range")
        elif converted > high:
            st.error("Interpretation: Above normal range")
        else:
            st.success("Interpretation: Within normal range")

    percent_bias = ((converted - value) / value) * 100 if value else 0
    st.caption(f"Estimated Platform Bias: {percent_bias:+.1f}%")
else:
    st.error("No conversion data found for selected combination.")