
from langchain_openai import OpenAI
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import  PromptTemplate
template = "You are a friendly assistant. Answer concisely: {question}"
prompt = PromptTemplate(input_variables=["question"], template=template)
llm = OpenAI(temperature=0.7)

chain = LLMChain(llm=llm, prompt=prompt)
response = chain.run("What is Agentic AI?")
print(response)
