
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import  PromptTemplate
template = "You are a friendly assistant. Answer concisely: {question}"
prompt = PromptTemplate(input_variables=["question"], template=template)

# A simple wrapper class to integrate Gemini model with LangChain style LLM interface
#class GeminiLLM(Runnable):
 #   def __init__(self, model_name: str = "gemini-1"):
  #      self.model_name = model_name

   # def invoke(self, prompt_text: str) -> str:
    #    response = client.chat.completions.create(
     #       model=self.model_name,
      #      messages=[{"role": "user", "content": prompt_text}]
       # )
       # return response.choices[0].message.content

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

chain = LLMChain(llm=llm, prompt=prompt)
response = chain.run("give your opinion on Stock Price of HDFC Bank")
print(response)
