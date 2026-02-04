from transformers import pipeline
#Load Api key
import os
from dotenv import load_dotenv
load_dotenv()

GEP_API_KEY= os.getenv("GEP_API_KEY")
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Recommended model for RAG
    #base_url="https://openai.generative.engine.capgemini.com/v1",
    api_key=GEP_API_KEY,
    #default_headers={"x-api-key": GEP_API_KEY},
    temperature=0.5,
   
) 
"""
llm = pipeline(
    "text-generation",
    model="google/flan-t5-small",
    max_new_tokens=80
)
"""

def explain(testcase, functions):
    prompt = (
        "You are a QA engineer \n"
        "Explain why the testcase is retrieved & how it is relevant to code in short in 1 line."
        f"Testcase description: {testcase['description']}\n"
        f"Impacted functions: {functions}\n"
        "Explanation:"
    )
 
    
    response = llm.invoke(prompt)
    return response.content

    #response = llm(prompt)[0]["generated_text"]
    #return response.strip()