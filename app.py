import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.utils import *
from src.generator.question_generator import QuestionGenerator
load_dotenv()


def main():
    st.set_page_config(page_title="Study Buddy AI" , page_icon="🎧")

    if 'quiz_manager'not in st.session_state:
        st.session_state.quiz_manager = QuizManager()

    if 'quiz_generated'not in st.session_state:
        st.session_state.quiz_generated = False

    if 'quiz_submitted'not in st.session_state:
        st.session_state.quiz_submitted = False

    if 'saved_file'not in st.session_state:
        st.session_state.saved_file = None


    st.title("Study Buddy AI")

    st.sidebar.header("Quiz Settings")

    question_type = st.sidebar.selectbox(
        "Select Question Type" ,
        ["Multiple Choice" , "Fill in the Blank"],
        index=0
    )

    topic = st.sidebar.text_input("Enter Topic")

    difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        ["Easy" , "Medium" , "Hard"],
        index=1
    )

    num_questions=st.sidebar.number_input(
        "Number of Questions",
        min_value=1,  max_value=10 , value=5
    )

    

    
    if st.sidebar.button("Generate Quiz"):
        st.session_state.quiz_submitted = False
        st.session_state.saved_file = None

        # building the generator can fail on missing/invalid config, and that
        # happens outside generate_questions' own error handling
        try:
            generator = QuestionGenerator()
        except Exception as e:
            st.error(f"⚠️ {e}")
            st.stop()

        succces = st.session_state.quiz_manager.generate_questions(
            generator,
            topic,question_type,difficulty,num_questions
        )

        st.session_state.quiz_generated= succces
        rerun()

    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header("Quiz")
        st.session_state.quiz_manager.attempt_quiz()

        if st.button("Submit Quiz"):
            if "" in st.session_state.quiz_manager.user_answers:
                st.warning("⚠️ Please answer all questions before submitting!")
            else:
                st.session_state.quiz_manager.evaluate_quiz()
                st.session_state.quiz_submitted = True
                rerun()


    if st.session_state.quiz_submitted:
        st.header("Quiz Results")
        results_df = st.session_state.quiz_manager.generate_result_dataframe()

        if not results_df.empty:
            correct_count = results_df["is_correct"].sum()
            total_questions = len(results_df)
            score_percentage = (correct_count/total_questions)*100
            st.write(f"Score : {score_percentage:.1f}% ({correct_count}/{total_questions})")

            for _, result in results_df.iterrows():
                question_num = result['question_number']
                if result['is_correct']:
                    st.success(f"✅ Question {question_num} : {result['question']}")
                else:
                    st.error(f"❌ Question {question_num} : {result['question']}")
                    st.write(f"Your answer : {result['user_answer']}")
                    st.write(f"Correct answer : {result['correct_answer']}")
                
                st.markdown("-------")

            
            if st.button("Save Results"):
                st.session_state.saved_file = st.session_state.quiz_manager.save_to_csv()

            saved_file = st.session_state.saved_file
            if saved_file and os.path.exists(saved_file):
                with open(saved_file,'rb') as f:
                    st.download_button(
                        label="Download Results",
                        data=f.read(),
                        file_name=os.path.basename(saved_file),
                        mime='text/csv'
                    )

if __name__=="__main__":
    main()

        
