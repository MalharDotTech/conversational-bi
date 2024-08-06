import time
import streamlit as st
from vanna_calls import (
    add_conversation_to_training,
    generate_questions_cached,
    generate_sql_cached,
    run_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
    generate_followup_cached,
    should_generate_chart_cached,
    is_sql_valid_cached,
    generate_summary_cached,
    add_training_data,
    get_training_data,
    remove_training_data,
    generate_basic_questions,
    generate_and_connect_new_db,
    switch_model
)
from streamlit_mic_recorder import speech_to_text

st.set_page_config(layout="wide")

st.sidebar.title("Output Settings")
st.sidebar.checkbox("Show SQL", value=False, key="show_sql")
st.sidebar.checkbox("Show Table", value=True, key="show_table")
st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
st.sidebar.checkbox("Show Summary", value=True, key="show_summary")
st.sidebar.checkbox("Show Follow-up Questions", value=False, key="show_followup")
st.sidebar.title("Database and Model Settings")
model_options = ["ibm_acc", "sales_model"]
selected_model = st.sidebar.selectbox("Select Model", model_options, key="model_selector")

if selected_model != st.session_state.get("current_model"):
    switch_model(selected_model)
    st.rerun()

st.sidebar.title("Training Mode Toggle")
auto_train = st.sidebar.toggle("Add Conversation To Train Toggle", value=False)
st.sidebar.title("Training Data Management")
train_data = st.sidebar.toggle("Show Training Data", value=False)
if train_data:
    training_data_option = st.sidebar.selectbox(
        "Choose an action",
        ("View Training Data", "Add Training Data", "Remove Training Data")
    )

    if training_data_option == "View Training Data":
        st.subheader("Current Training Data")
        training_data = get_training_data()
        st.dataframe(training_data)

    elif training_data_option == "Add Training Data":
        st.subheader("Add New Training Data")
        data_type = st.selectbox("Select data type", ["ddl", "documentation", "sql", "question_sql"])
        content = st.text_area("Enter the content")
        if st.button("Add Training Data"):
            result = add_training_data(data_type, content)
            st.success(result)

    elif training_data_option == "Remove Training Data":
        st.subheader("Remove Training Data")
        training_data = get_training_data()
        st.dataframe(training_data)
        id_to_remove = st.text_input("Enter the ID of the training data to remove")
        if st.button("Remove Training Data"):
            result = remove_training_data(id_to_remove)
            st.success(result)

#    use_custom_db = st.sidebar.checkbox("Use Custom Database")
#
#    if use_custom_db:
#        uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
#        generate_and_connect_new_db(uploaded_file)
#        basic_questions = generate_basic_questions()
main_container = st.container()

input_container = st.container()


def set_question(question):
    st.session_state["my_question"] = question

assistant_message_suggested = st.chat_message("assistant")

if assistant_message_suggested.button("Click to show suggested questions"):
    st.session_state["my_question"] = None
    questions = generate_questions_cached()
    for i, question in enumerate(questions):
        time.sleep(0.05)
        #button = st.button(
        #    question,
        #    on_click=set_question,
        #    args=(question,),
        #)
        st.write(question)

# Initialize conversation history in session state if it doesn't exist
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

with main_container:
    st.title("💬 Conversational BI 📊 ")
    # st.sidebar.write(st.session_state)
    # Display all previous conversations and responses
    for conversation in st.session_state.conversation_history:
        user_message = st.chat_message("user")
        user_message.write(conversation["question"])
        
        for response in conversation["responses"]:
            assistant_message = st.chat_message("assistant")
            if response["type"] == "sql":
                assistant_message.code(response["content"], language="sql", line_numbers=True)
            elif response["type"] == "table":
                assistant_message.dataframe(response["content"])
            elif response["type"] == "chart":
                assistant_message.plotly_chart(response["content"])
            elif response["type"] == "summary":
                assistant_message.markdown(f'**Summary**\n\n{response["content"]}')
            elif response["type"] == "followup":
                assistant_message.text("Here are some possible follow-up questions")
                for question in response["content"][:5]:
                    assistant_message.button(question, on_click=set_question, args=(question,))

with input_container:
    # Get new question from chat input or speech-to-text
    col1, col2 = st.columns([3, 1])
    with col1:
        new_question = st.chat_input("Ask me a question about your data")
    with col2:
        speech_input = speech_to_text(start_prompt="🎤 Voice",stop_prompt="🟥 Stop",language='en', use_container_width=False, just_once=True, key='STT')

if new_question or speech_input:
    question = speech_input if speech_input else new_question
    # Process the new question
    user_message = st.chat_message("user")
    user_message.write(f"{question}")

    # Initialize a new conversation entry
    current_conversation = {"question": question, "responses": []}

    sql = generate_sql_cached(question=question)

    if sql:
        if is_sql_valid_cached(sql=sql):
            if st.session_state.get("show_sql", True):
                assistant_message_sql = st.chat_message("assistant") 
                assistant_message_sql.code(sql, language="sql", line_numbers=True)
                current_conversation["responses"].append({"type": "sql", "content": sql})
            if auto_train:
                assistant_message = st.chat_message("assistant")
                assistant_message.write("Were the reports correct ?, Add this to Training Data" )
                if assistant_message.button("Add this to Training Data"):
                    training_result = add_conversation_to_training(question, sql)
                    st.sidebar.success(training_result)
        else:
            assistant_message = st.chat_message("assistant")
            assistant_message.write(sql)
            st.stop()

        df = run_sql_cached(sql=sql)

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("show_table", True):
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message("assistant")
                if len(df) > 10:
                    assistant_message_table.text("First 10 rows of data")
                    assistant_message_table.dataframe(df.head(10))
                else:
                    assistant_message_table.dataframe(df)
                current_conversation["responses"].append({"type": "table", "content": df.head(10) if len(df) > 10 else df})

            if should_generate_chart_cached(question=question, sql=sql, df=df):

                code = generate_plotly_code_cached(question=question, sql=sql, df=df)

                if st.session_state.get("show_plotly_code", False):
                    assistant_message_plotly_code = st.chat_message("assistant")
                    assistant_message_plotly_code.code(
                        code, language="python", line_numbers=True
                    )

                if code is not None and code != "":
                    if st.session_state.get("show_chart", True):
                        assistant_message_chart = st.chat_message("assistant")
                        fig = generate_plot_cached(code=code, df=df)
                        if fig is not None:
                            assistant_message_chart.plotly_chart(fig)
                            current_conversation["responses"].append({"type": "chart", "content": fig})
                        else:
                            assistant_message_chart.error("I couldn't generate a chart")

            if st.session_state.get("show_summary", True):
                assistant_message_summary = st.chat_message("assistant")
                summary = generate_summary_cached(question=question, df=df)
                if summary is not None:
                    assistant_message_summary.markdown(f"**Summary:**\n\n{summary}")
                    current_conversation["responses"].append({"type": "summary", "content": summary})

                if st.session_state.get("show_followup", True):
                    assistant_message_followup = st.chat_message("assistant")
                    followup_questions = generate_followup_cached(question=question, sql=sql, df=df)
                    if len(followup_questions) > 0:
                        assistant_message_followup.text("Here are some possible follow-up questions")
                        for question in followup_questions[:5]:
                            assistant_message_followup.button(question, on_click=set_question, args=(question,))
                        current_conversation["responses"].append({"type": "followup", "content": followup_questions[:5]})

            # Add the current conversation to the history
            st.session_state.conversation_history.append(current_conversation)

        else:
            assistant_message = st.chat_message("assistant")
            assistant_message.write(sql)
    else:
        assistant_message_error = st.chat_message("assistant")
        assistant_message_error.error("I wasn't able to generate SQL for that question")

if st.sidebar.button("Reset"):
    st.session_state.conversation_history = []
    st.session_state.df = None
    st.rerun()
