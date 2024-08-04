import streamlit as st
from csv_to_sqlite import csv_to_sqlite
from dotenv import load_dotenv
from vanna.remote import VannaDefault
import os
import sqlite3
import pandas as pd
load_dotenv()

@st.cache_resource(ttl=3600)
def setup_vanna(db_path="./sales_db.sqlite", model_name='sales_model'):
    vn = VannaDefault(api_key=os.getenv("VANNA_API_KEY"), model=model_name)
    vn.connect_to_sqlite(db_path)
    return vn

def switch_model(model_name):
    setup_vanna(db_path="./sales_db.sqlite", model_name=model_name)

@st.cache_data(show_spinner="Connecting Custom Database...")
def generate_and_connect_new_db(uploaded_file,db_path="./ibm_acc.database.sqlite", model_name='ibm_acc'):
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Convert CSV to SQLite
        db_path = "custom_db.sqlite"
        csv_to_sqlite("temp.csv", db_path)
        st.sidebar.success("Custom database created successfully!")
    reset_model()
    setup_vanna(db_path=db_path, model_name=model_name)

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

@st.cache_data(show_spinner="Resetting model...")
def reset_model():
    vn = setup_vanna()
    training_data = vn.get_training_data()
    for item in training_data:
        vn.remove_training_data(id=item['id'])
    return "Model reset successfully. All training data removed."

@st.cache_data(show_spinner="Adding conversation to training data...")
def add_conversation_to_training(question: str, sql: str):
    vn = setup_vanna()
    vn.train(question=question, sql=sql)
    return "Conversation added to training data successfully!"

def generate_basic_questions(table_name="data"):
    return [
        f"What are the column names in the {table_name} table?",
        f"Show me the first 5 rows of the {table_name} table.",
        f"How many rows are in the {table_name} table?",
        f"What are the unique values in each column of the {table_name} table?",
        f"What is the data type of each column in the {table_name} table?"
    ]

