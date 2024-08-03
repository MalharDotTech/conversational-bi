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
    remove_training_data
)

avatar_url = "./themlco_logo.jpeg"

st.set_page_config(layout="wide")

st.sidebar.title("Output Settings")
st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
st.sidebar.checkbox("Show Table", value=True, key="show_table")
st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
st.sidebar.checkbox("Show Summary", value=True, key="show_summary")
st.sidebar.checkbox("Show Follow-up Questions", value=False, key="show_followup")
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

st.sidebar.button("Reset", on_click=lambda: set_question(None), use_container_width=True)


st.title("💬 Conversational BI 📊 ")
# st.sidebar.write(st.session_state)

def set_question(question):
    st.session_state["my_question"] = question

assistant_message_suggested = st.chat_message(
    "assistant", avatar=avatar_url
)
if assistant_message_suggested.button("Click to show suggested questions"):
    st.session_state["my_question"] = None
    questions = generate_questions_cached()
    for i, question in enumerate(questions):
        time.sleep(0.05)
        button = st.button(
            question,
            on_click=set_question,
            args=(question,),
        )

my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    my_question = st.chat_input(
        "Ask me a question about your data",
    )

if my_question:
    st.session_state["my_question"] = my_question
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = generate_sql_cached(question=my_question)

    if sql:
        if is_sql_valid_cached(sql=sql):
            if st.session_state.get("show_sql", True):
                assistant_message_sql = st.chat_message(
                    "assistant", avatar=avatar_url
                )
                assistant_message_sql.code(sql, language="sql", line_numbers=True)
            if auto_train:
                assistant_message = st.chat_message( "assistant", avatar=avatar_url )
                assistant_message.write("Were the reports correct ?, Add this to Training Data" )
                if (yes := assistant_message.button("Yes")) or (no := assistant_message.button("No")):
                    if yes: 
                        training_result = add_conversation_to_training(my_question, sql)
                        st.sidebar.success(training_result)
                    if no:
                        pass
        else:
            assistant_message = st.chat_message(
                "assistant", avatar=avatar_url
            )
            assistant_message.write(sql)
            st.stop()

        df = run_sql_cached(sql=sql)

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("show_table", True):
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                if len(df) > 10:
                    assistant_message_table.text("First 10 rows of data")
                    assistant_message_table.dataframe(df.head(10))
                else:
                    assistant_message_table.dataframe(df)

            if should_generate_chart_cached(question=my_question, sql=sql, df=df):

                code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)

                if st.session_state.get("show_plotly_code", False):
                    assistant_message_plotly_code = st.chat_message(
                        "assistant",
                        avatar=avatar_url,
                    )
                    assistant_message_plotly_code.code(
                        code, language="python", line_numbers=True
                    )

                if code is not None and code != "":
                    if st.session_state.get("show_chart", True):
                        assistant_message_chart = st.chat_message(
                            "assistant",
                            avatar=avatar_url,
                        )
                        fig = generate_plot_cached(code=code, df=df)
                        if fig is not None:
                            assistant_message_chart.plotly_chart(fig)
                        else:
                            assistant_message_chart.error("I couldn't generate a chart")

            if st.session_state.get("show_summary", True):
                assistant_message_summary = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                summary = generate_summary_cached(question=my_question, df=df)
                if summary is not None:
                    assistant_message_summary.text(summary)

            if st.session_state.get("show_followup", True):
                assistant_message_followup = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                followup_questions = generate_followup_cached(
                    question=my_question, sql=sql, df=df
                )
                st.session_state["df"] = None

                if len(followup_questions) > 0:
                    assistant_message_followup.text(
                        "Here are some possible follow-up questions"
                    )
                    # Print the first 5 follow-up questions
                    for question in followup_questions[:5]:
                        assistant_message_followup.button(question, on_click=set_question, args=(question,))

    else:
        assistant_message_error = st.chat_message(
            "assistant", avatar=avatar_url
        )
        assistant_message_error.error("I wasn't able to generate SQL for that question")
