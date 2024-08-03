import streamlit as st
from dotenv import load_dotenv
from vanna.remote import VannaDefault
import os
load_dotenv()

@st.cache_resource(ttl=3600)
def setup_vanna():
    vn = VannaDefault(api_key=os.getenv("VANNA_API_KEY"), model='ibm_acc')
    vn.connect_to_sqlite("./ibm_acc.database.sqlite")
    return vn

@st.cache_data(show_spinner="Generating sample questions ...")
def generate_questions_cached():
    vn = setup_vanna()
    return vn.generate_questions()

@st.cache_data(show_spinner="Generating SQL query ...")
def generate_sql_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="Checking for valid SQL ...")
def is_sql_valid_cached(sql: str):
    vn = setup_vanna()
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Checking if we should generate a chart ...")
def should_generate_chart_cached(question, sql, df):
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Generating Plotly code ...")
def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code

@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)

@st.cache_data(show_spinner="Generating followup questions ...")
def generate_followup_cached(question, sql, df):
    vn = setup_vanna()
    return vn.generate_followup_questions(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="Generating summary ...")
def generate_summary_cached(question, df):
    vn = setup_vanna()
    return vn.generate_summary(question=question, df=df)

@st.cache_data(show_spinner="Adding training data...")
def add_training_data(data_type, content):
    vn = setup_vanna()
    if data_type == 'ddl':
        vn.train(ddl=content)
    elif data_type == 'documentation':
        vn.train(documentation=content)
    elif data_type == 'sql':
        vn.train(sql=content)
    elif data_type == 'question_sql':
        question, sql = content.split('|||')
        vn.train(question=question.strip(), sql=sql.strip())
    return "Training data added successfully!"

@st.cache_data(show_spinner="Fetching training data...")
def get_training_data():
    vn = setup_vanna()
    return vn.get_training_data()

@st.cache_data(show_spinner="Removing training data...")
def remove_training_data(id):
    vn = setup_vanna()
    vn.remove_training_data(id=id)
    return f"Training data with ID {id} removed successfully!"


@st.cache_data(show_spinner="Adding conversation to training data...")
def add_conversation_to_training(question: str, sql: str):
    vn = setup_vanna()
    vn.train(question=question, sql=sql)
    return "Conversation added to training data successfully!"


'''
# Add DDL statement
add_training_data('ddl', """
CREATE TABLE data (
    countryCode INTEGER,
    customerID TEXT,
    PaperlessDate DATE,
    invoiceNumber TEXT,
    InvoiceDate DATE,
    DueDate DATE,
    InvoiceAmount DECIMAL(10,2),
    Disputed TEXT,
    SettledDate DATE,
    PaperlessBill TEXT,
    DaysToSettle INTEGER,
    DaysLate INTEGER
);
""")

# Add example SQL queries
example_queries = [
    "SELECT customerID, InvoiceAmount, InvoiceDate, DueDate FROM data LIMIT 10;",
    "SELECT countryCode, COUNT(*) as invoice_count, AVG(InvoiceAmount) as avg_amount FROM data GROUP BY countryCode;",
    "SELECT * FROM data WHERE Disputed = 'Yes' AND DaysLate > 0;",
    "SELECT customerID, InvoiceDate, DueDate, SettledDate, julianday(SettledDate) - julianday(DueDate) as actual_days_to_settle FROM data WHERE SettledDate > DueDate;",
    "SELECT PaperlessBill, COUNT(*) as bill_count, AVG(DaysToSettle) as avg_days_to_settle, AVG(DaysLate) as avg_days_late FROM data GROUP BY PaperlessBill;",
    """
    SELECT 
        CASE 
            WHEN DaysLate = 0 THEN 'On Time'
            WHEN DaysLate BETWEEN 1 AND 7 THEN '1-7 Days Late'
            WHEN DaysLate BETWEEN 8 AND 30 THEN '8-30 Days Late'
            ELSE 'More than 30 Days Late'
        END as payment_status,
        COUNT(*) as invoice_count,
        AVG(InvoiceAmount) as avg_invoice_amount
    FROM data
    GROUP BY payment_status;
    """
]

for query in example_queries:
    add_training_data('sql', query)
'''
