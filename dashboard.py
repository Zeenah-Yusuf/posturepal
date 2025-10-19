import streamlit as st
import pandas as pd
import os

def load_all_user_data():
    data = []
    for file in os.listdir("history"):
        if file.endswith(".xlsx"):
            username = file.split("_")[0]
            df = pd.read_excel(f"history/{file}")
            df["Username"] = username
            data.append(df)
    return pd.concat(data, ignore_index=True)

dashboard_df = load_all_user_data()
st.dataframe(dashboard_df)

summary = dashboard_df.groupby("Username")["Score"].agg(["mean", "count"]).reset_index()
st.bar_chart(summary.set_index("Username"))
