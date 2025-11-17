
from langchain_community.chat_models import ChatPerplexity
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import  PromptTemplate
template = "You are a friendly assistant. Answer concisely: {question}"
prompt = PromptTemplate(input_variables=["question"], template=template)



llm = ChatPerplexity(model="sonar", temperature=0.7)

chain = LLMChain(llm=llm, prompt=prompt)
response = chain.run("give your opinion on Stock Price of HDFC Bank")
print(response)
