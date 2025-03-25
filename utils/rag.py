"""
    This file contains all the utility functions,
    to process documents and create a vectorstore
    for RAG, during the QA run.
"""
from selenium import webdriver
from bs4 import BeautifulSoup
import json, os

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

def get_html_page(url):
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
        return soup
    except Exception as e:
        print(f"Error reading page {url}: {e}")
        driver.close()
    
def load_process_docs():
    urls = []
    all_faqs = []
    with open("./outputs/parsed_urls.txt", "r") as f:
        str_urls = f.readlines()
    
    for url in str_urls:
        title = url.split("/")[-1]
        urls.append({"url": url, "title": title})
        
    # Get the article content
    # call the get_html_page function for each url and extract content
    for url in urls:
        article_soup = get_html_page(url["url"])
        article_body = article_soup.find("div", class_="article-body")
        if article_body:
            article_content = article_body.text.strip()
            all_faqs.append({
                "title": url["title"],
                "url": url["url"],
                "content": article_content
            })

    # Save FAQs to a JSON file. We need it for evals
    with open("./outputs/all_faqs.json", "w") as f:
        json.dump(all_faqs, f, indent=2)
        
    return all_faqs

def convert_lc_docs(all_faqs):
    # Converting the faqs into langchain Document type
    documents = []
    for faq in all_faqs:
        documents.append(Document(page_content=faq["content"], metadata={"title": faq["title"], "url": faq["url"]}))
    return documents
        
def create_embeddings():
    all_faqs = load_process_docs()
    
    # Create embeddings using HuggingFace model
    model_name = "sentence-transformers/all-mpnet-base-v2" 
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # Using InMemoryVectorStore because Chroma was throwing errors locally
    vectorstore = InMemoryVectorStore(embeddings)
    
    # First create langchain Documents, split into chunks and then add them to the vectorstore
    documents = convert_lc_docs(all_faqs)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    vectorstore.add_documents(documents=chunks)
    
    # Save the vectorstore in a file locally
    if not os.path.exists("./inmemory_langchain_db"):
        vectorstore.dump("./inmemory_langchain_db")
            
    return vectorstore