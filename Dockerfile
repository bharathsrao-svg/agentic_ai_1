FROM python:3.10-slim



WORKDIR /app


RUN pip install --upgrade pip
RUN pip install langchain_classic langchain-google-genai

#RUN python -c "import langchain; print(langchain.__version__); print(dir(langchain))"

COPY agent_1.py .


CMD [ "python","agent_1.py" ]