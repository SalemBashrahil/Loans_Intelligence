import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels
import pandas as pd
import numpy as np
import scipy

def show():

    st.title('Loan Analysis')

    # Initialize or load loan data in session state
    if 'loan_data' not in st.session_state:
        st.session_state.loan_data = []

    # Function to add a new loan
    def add_loan(name, principal, rate, term, start_date):
        loan = {
            'Name': name,
            'Principal': principal,
            'Rate': rate,
            'Term (Years)': term,
            'Start Date': start_date,
            'Remaining Balance': principal,
            'Status': 'Active'
        }
        st.session_state.loan_data.append(loan)

    # Function to close a loan
    def close_loan(name):
        for loan in st.session_state.loan_data:
            if loan['Name'] == name:
                loan['Status'] = 'Closed'
                loan['Remaining Balance'] = 0

    # Function to calculate WACC
    def calculate_wacc(loan_data):
        total_debt = sum([loan['Remaining Balance'] for loan in loan_data if loan['Status'] == 'Active'])
        if total_debt == 0:
            return 0.0
        weighted_rates = [loan['Rate'] * loan['Remaining Balance'] / total_debt for loan in loan_data if loan['Status'] == 'Active']
        return sum(weighted_rates)

    # Function to calculate total interest for each loan
    def calculate_total_interest(loan):
        monthly_rate = loan['Rate'] / 100 / 12
        num_payments = loan['Term (Years)'] * 12
        if monthly_rate == 0:
            return loan['Principal']
        return loan['Principal'] * monthly_rate * num_payments / (1 - (1 + monthly_rate) ** -num_payments)

    # Function to generate time series data for loan payments
    def generate_time_series(loan):
        monthly_rate = loan['Rate'] / 100 / 12
        num_payments = loan['Term (Years)'] * 12
        dates = pd.date_range(start=loan['Start Date'], periods=num_payments, freq='M')
        payments = []
        remaining_balance = loan['Principal']
        for _ in range(num_payments):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = (loan['Principal'] * monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1) - interest_payment
            remaining_balance -= principal_payment
            payments.append({
                'Date': dates[_],
                'Principal Payment': principal_payment,
                'Interest Payment': interest_payment,
                'Remaining Balance': remaining_balance
            })
        return pd.DataFrame(payments)

    # Layout for adding new loans
    st.header('Add New Loan')

    with st.form(key='loan_form'):
        loan_name = st.text_input('Loan Name')
        loan_principal = st.number_input('Principal Amount', min_value=0.0)
        loan_rate = st.number_input('Interest Rate (%)', min_value=0.0, max_value=100.0)
        loan_term = st.number_input('Term (Years)', min_value=1, max_value=30)
        loan_start_date = st.date_input('Start Date')
        submit_button = st.form_submit_button(label='Add Loan')

        if submit_button:
            add_loan(loan_name, loan_principal, loan_rate, loan_term, loan_start_date)
            st.success(f"Loan '{loan_name}' added successfully!")

    # Show existing loans
    st.header('Existing Loans')
    loan_df = pd.DataFrame(st.session_state.loan_data)

    if not loan_df.empty:
        st.dataframe(loan_df)

        # Option to close a loan
        st.subheader('Close a Loan')
        loan_to_close = st.selectbox('Select a loan to close:', loan_df[loan_df['Status'] == 'Active']['Name'])
        close_button = st.button('Close Loan')

        if close_button:
            close_loan(loan_to_close)
            st.success(f"Loan '{loan_to_close}' closed successfully!")

        # Calculate WACC
        st.subheader('Weighted Average Cost of Capital (WACC)')
        wacc = calculate_wacc(st.session_state.loan_data)
        st.metric(label="WACC", value=f"{wacc:.2f}%")

        # Calculate and display total interest for each loan
        st.subheader('Total Interest on Loans')
        loan_df['Total Interest'] = loan_df.apply(calculate_total_interest, axis=1)
        st.write(loan_df[['Name', 'Total Interest']])

        # Sensitivity Analysis: Show impact of varying interest rates
        st.subheader('Sensitivity Analysis')
        sensitivity_rates = np.arange(0, 20, 0.5)
        sensitivities = [calculate_wacc([{**loan, 'Rate': rate} for loan in st.session_state.loan_data]) for rate in sensitivity_rates]
        plt.figure(figsize=(10, 6))
        plt.plot(sensitivity_rates, sensitivities, label='WACC')
        plt.xlabel('Interest Rate (%)')
        plt.ylabel('WACC (%)')
        plt.title('Sensitivity Analysis of WACC to Interest Rates')
        plt.grid(True)
        st.pyplot(plt)

        # Generate time series for selected loan
        st.subheader('Loan Payment Time Series')
        loan_for_time_series = st.selectbox('Select a loan for time series analysis:', loan_df['Name'])
        selected_loan = next(loan for loan in st.session_state.loan_data if loan['Name'] == loan_for_time_series)
        time_series_df = generate_time_series(selected_loan)
        st.line_chart(time_series_df.set_index('Date')[['Principal Payment', 'Interest Payment', 'Remaining Balance']])

        # Download time series data
        st.subheader('Download Monthly Payment Data')
        csv = time_series_df.to_csv(index=False)
        st.download_button(label="Download data as CSV", data=csv, file_name=f'{loan_for_time_series}_monthly_payments.csv', mime='text/csv')
    else:
        st.write("No loans available.")
        