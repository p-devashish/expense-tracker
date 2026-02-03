import streamlit as st
import datetime

st.title("Expense Tracker")

if "expenses" not in st.session_state:
    st.session_state.expenses = []

st.header("Add Expense")

notes = st.text_input("Notes")
amount = st.number_input("Amount", min_value=0.0, step=0.01)
date = st.date_input("Date", value=datetime.date.today())
time = st.time_input("Time", value=datetime.datetime.now().time())

if st.button("Add Expense"):
    dt = datetime.datetime.combine(date, time)
    expense = {"notes": notes, "amount": amount, "datetime": dt}
    st.session_state.expenses.append(expense)
    st.success("Expense added!")

st.header("Expenses")

if st.session_state.expenses:
    for exp in st.session_state.expenses:
        st.write(f"{exp['datetime']}: {exp['notes']} - ${exp['amount']}")
else:
    st.write("No expenses yet.")