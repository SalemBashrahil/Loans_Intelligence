import streamlit as st

import Loan_Intelligence.Loan_Analysis as Loan_Analysis

st.set_page_config(layout="wide")


def main():
    Navigation = st.sidebar.title("fsg")
    Page = ["Loan_Analysis"]
    Select = st.sidebar.selectbox("fg",Page)


    if Select=="Loan_Analysis":
        Loan_Analysis.show()

main()