import json
import streamlit as st
from time import sleep
import os
from config_reader import fetch_config_dict
import generate_quiz_from_prompt
import generate_quiz_on_file
from streamlit_modal import Modal
import streamlit.components.v1 as components

# from dotenv import load_dotenv
# from src.mcq_generator.utils import read_file, get_table_data
# from src.mcq_generator.logger import logging
def app_setup():
    # set page/theme info
    st.set_page_config(
        page_title="QuizCraft - AI Generated Quizzes 🧠📚❓",
        page_icon="📝",
        layout="centered",
        initial_sidebar_state="auto",
        menu_items=None)

    # resize logo
    st.html("""
    <style>
        [alt=Logo] {
        height: 10rem;
        }
    </style>
            """)

    st.logo(
        image="images/logo/quiz-craft-logo.png",
        size="large"
        )


    #app title
    st.title("QuizCraft 🧠📚❓")

    #description
    description = st.text("QuizCraft is an AI-powered tool that generates different questions from text.\n"
                        "Simply input some text or upload a PDF/text file, and adjust some parameters.\n"
                        "QuizCraft will generate a quiz for you in seconds! 🚀")

# Delete Source files from Data directory
def delete_files_in_directory(config_dict):
    list_of_files = os.listdir(config_dict.get("data_directory", "EMPTY_DATA_DIRECTORY"))

    if len(list_of_files) > 0:
        for each_file in list_of_files:
            os.remove(os.path.join(config_dict.get("data_directory", "EMPTY_DATA_DIRECTORY"), each_file))

# Download Files from data directory
def download_files(uploaded_file, config_dict):
    
    delete_files_in_directory(config_dict)

    file_details = {
        'FileName' : uploaded_file.name,
        'FileType' : uploaded_file.type
    }

    with open(os.path.join(config_dict.get("data_directory", "EMPTY_DATA_DIRECTORY"), file_details['FileName']), "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Your file has been saved")

def evaluate_scores(question_list, answer_list):
    """
    Function to evaluate scores based on user answers.
    """
    correct_count = sum(1 for user_ans, correct_ans in zip(question_list, answer_list) if user_ans == correct_ans)
    st.write(f"You scored {correct_count}/{len(answer_list)} correct answers!")
    print("SESISON STATE 3 :", st.session_state, '\n')

def display_output_quiz_fake():
    """
    Function to create the output body with the JSON response for the quiz.
    """
    answer_list = []
    question_list = []

    quiz_json = st.session_state.quiz_json
    

    if "quiz_json" not in st.session_state:
        st.error("Quiz not generated. Please generate a quiz first.")
        return

    quiz_json = st.session_state.quiz_json
    if type(quiz_json) != 'json':
        quiz_json = str(quiz_json)
        quiz_json = json.loads(quiz_json)
        
    # Ensure quiz_json is a dict
    if isinstance(quiz_json, str):
        quiz_json = json.loads(quiz_json)

    answer_list = []
    question_list = []

    # Create a form for user answers
    with st.form("user_answers"):
        for idx, each_question in enumerate(quiz_json.get("quiz", [])):
            # Extract question and options
            question = each_question.get("question", "NO QUESTION")
            options = each_question.get("options", ["NO OPTIONS"])
            answer = each_question.get("answer", "NO ANSWER")
            
            # Use st.radio to display options
            user_answer = st.radio(f"***Q{idx + 1}: {question}***", options, key=f"question_{idx}")
            question_list.append(user_answer)
            answer_list.append(answer)

        # Add the submit button (outside the loop)
        submit = st.form_submit_button("Submit Quiz", on_click=evaluate_scores, args=(question_list, answer_list))

        # Display message after submission
        if submit:
            st.write("Calculating your scores")

def evaluate_scores_fake(question_list, answer_list):
    """
    Function to evaluate scores based on user answers.
    """
    correct_count = sum(1 for user_ans, correct_ans in zip(question_list, answer_list) if user_ans == correct_ans)
    st.write(f"You scored {correct_count}/{len(answer_list)} correct answers!")


def display_output_quiz(quiz_json):
    """
    Function to create the output body with the JSON response for the quiz.
    """
    print("SESISON STATE :", st.session_state, '\n')
    answer_list = []
    question_list = []

    modal = Modal(
    "Demo Modal", 
    key="demo-modal",
    
    # Optional
    padding=20,    # default value
    max_width=744  # default value
    )

    # quiz_json = st.session_state.quiz_json
    if type(quiz_json) != 'json':
        quiz_json = str(quiz_json)
        quiz_json = json.loads(quiz_json)

    
    # Create a form for user answers
    with st.form("user_answers"):
        

        for idx, each_question in enumerate(quiz_json.get("quiz", [])):
            # print("Processing question:", each_question)

            # Extract question and options
            question = each_question.get("question", "NO QUESTION")
            options = each_question.get("options", ["NO OPTIONS"])
            answer = each_question.get("answer", "NO ANSWER")
            
            # Use st.radio to display options
            user_answer = st.radio("***" + f"Q{idx + 1}: {question}" + "***", options, index = None)
            question_list.append(user_answer)
            answer_list.append(answer)

        submit = st.form_submit_button("Submit Quiz", on_click=lambda: evaluate_scores)
        


#create form
def create_form(config_dict):

    with st.form("user_inputs"):
        #text input
        text_area = st.text_area("Text Input", height=200, max_chars=4000, help="Enter your text here")

        #file upload
        uploaded_file = st.file_uploader("Upload your PDF file here")

        #subject
        # subject = st.text_input("Subject name:", max_chars=20, placeholder="Machine Learning")

        #question type
        # question_types = st.multiselect("Question Types", ["Multiple Choice", "True/False", "Fill in the Blanks"],
        #                                 default=["Multiple Choice"], help="Select the type of questions you want in the quiz")

        # user will be able to select the number of questions for each type
        # based on what available question types were selected above
        # #input fields
        # mcq_count=st.number_input("No. of MCQs: ", min_value=3, max_value=50, placeholder= "10")

        #quiz difficulty
        difficulty_level = st.select_slider("Quiz Difficulty", options=["Easy", "Medium", "Hard"],
                                            value="Medium", help="Select the difficulty level of the quiz")

        #number of questions
        number_of_questions = st.slider("Number of Questions", min_value=5, max_value=50, value=10,
                                        help="Select the number of questions you want in the quiz")

        #Create button
        submit = st.form_submit_button("Generate Quiz")
        text_widget = st.empty()
        progress_widget = st.empty()

        user_does_something_flag = False

        # User clicks on submit
        if submit:

            # Case - User uploads a file, download it.
            if uploaded_file is not None:
                download_files(uploaded_file, config_dict)
                user_does_something_flag = True
                quiz_json = generate_quiz_on_file.main(difficulty_level, number_of_questions, text_area)
                # st.session_state.quiz_json = quiz_json  # Store in session state
                # display_output_quiz(quiz_json)

            # Case - User uploads a text
            elif text_area not in  [None, '']:
                st.success('Generating Quiz on your prompt')
                user_does_something_flag = True
                quiz_json = generate_quiz_from_prompt.main(difficulty_level, number_of_questions, text_area)
                # st.session_state.quiz_json = quiz_json  # Store in session state
                # display_output_quiz(quiz_json)

            # Case - User does nothing
            else:
                st.error('Either enter a prompt text, or upload a pdf file or do both')
        
    # Display Quiz
    # return user_does_something_flag
    if user_does_something_flag:
        display_output_quiz(quiz_json)

        # Display Progress Bar
        # for i in range(101):
        #     sleep(0.01)
        #     text_widget.write(i)
        #     progress_widget.progress(i / 100)
    return user_does_something_flag


# implement the logic for generating the quiz (this is a placeholder)
# #Check if the button has been clicked and all fields have input
# if button and uploaded_file is not None and subject and tone:
#     with st.spinner("Generating MCQs..."):
#         try:
#             text = read_file(uploaded_file)
#             #count tokens and the cost of API call
#             with get_openai_callback() as cb:
#                 response = generate_evaluate_chain(
#                     {
#                         "text": text,
#                         "number": mcq_count,
#                         "subject": subject,
#                         "tone": tone,
#                         "response_json": json.dumps(RESPONSE_JSON)
#                     }
#                 )

#         except Exception as e:
#             traceback.print_exception(type(e), e, e.__traceback__)
#             st.error("An error was encountered!!") 

#         else:
#             print(f"Total Tokens: {cb.total_tokens}")
#             print(f"Prompt Tokens: {cb.prompt_tokens}")
#             print(f"Completion Tokens: {cb.completion_tokens}")
#             print(f"Total Cost: Only {cb.total_cost}")
#             if isinstance(response, dict):
#                 #Extract the quiz data from the response
#                 quiz=response.get("Quiz", None)
#                 if quiz is not None:
#                     table_data = get_table_data(quiz)
#                     if table_data is not None:
#                         df = pd.DataFrame(table_data)
#                         df.index = df.index + 1
#                         st.table(df)

#                         #Display the review in a text box
#                         st.text_area(label="Review", value= response["review"])
#                     else:
#                         st.error("Error in the table data")

#             else:
#                 st.write(response)

def main():
    """
        Main function for the streamlit app.
    """
    config_dict = fetch_config_dict()
    app_setup()
    user_does_something_flag = create_form(config_dict)
    # if user_does_something_flag:
    #     display_output_quiz()

if __name__ == "__main__": 
    main()