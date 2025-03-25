"""
    This is a basic streamlit app for running the
    QA system.
    
    This is the entry point for the project.
    On the command line run `streamlit run app.py`
"""
import streamlit as st
from qa_system import QASystem

def main():
    st.title("Voy Weight Loss FAQ Assistant")
    
    # Initialising the QA system
    if 'qa_system' not in st.session_state:
        with st.spinner("Initializing the QA system..."):
            st.session_state.qa_system = QASystem()
    
    # User input
    user_question = st.text_input("Ask a question about Voy's weight loss services:")
    
    if st.button("Get Answer") and user_question:
        with st.spinner("Generating answer..."):
            result = st.session_state.qa_system.answer_question(user_question)
        
        # Display answer
        st.subheader("Answer:")
        st.write(result)
        
        # Simple feedback to evaluate the answer (doesn't do anything meaningful)
        st.subheader("Was this answer helpful?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes"):
                st.success("Thanks for your feedback!")
        with col2:
            if st.button("No"):
                st.error("We'll work on improving our answers!")

if __name__ == "__main__":
    main()