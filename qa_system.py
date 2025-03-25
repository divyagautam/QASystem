"""
    This file defines the main QA System class.
    The QA system can be run by calling the answer_question() function
    with a question
"""
import os
from getpass import getpass

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI

from utils.rag import create_embeddings
from utils.logging import LoggingCallback
        
class QASystem:
    def __init__(self):
        # check if vectorstore "inmemory_langchain_db" is saved locally and load it if it exists, if not then create it
        if os.path.exists("./inmemory_langchain_db"):
            model_name = "sentence-transformers/all-mpnet-base-v2" 
            embeddings = HuggingFaceEmbeddings(model_name=model_name)
            self.vectorstore = InMemoryVectorStore.load(path="./inmemory_langchain_db", embedding=embeddings)
        else:
            self.vectorstore = create_embeddings()
        
        self.llm = GoogleGenerativeAI(model="gemini-2.0-pro-exp-02-05", temperature=0.2, callbacks=[LoggingCallback()]) # using Google's chat model

        print("System ready!")
        
    def _format_docs(self,docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
    def answer_question(self, question: str):
        
        self.prompt = PromptTemplate.from_template("""You are a helpful assistant for Voy, a telehealth service exclusively for weight loss. 
            Answer the following question based ONLY on the provided context.
            If the question cannot be answered from the context, 
            say "I don't have enough information to answer that question."
            Do not make up any medical information or recommendations that aren't explicitly stated in the context.

            Context:
            {context}

            Question: {question}

            Answer:""")
            
        self.qa_chain = (
            {
                "context": self.vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 5}) | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        try:
            result = self.qa_chain.invoke(question)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"result": "An error occurred. Please try again."}