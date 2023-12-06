from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import os
import sys
import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
import constants
from fpdf import FPDF


app = Flask(__name__)
CORS(app)

@app.route('/process_strings', methods=['POST'])
def process_strings():
    data = request.json 
    responses = []

    if isinstance(data, dict):
        for key, value in data.items():
            processed_data = your_openai_function(value)
            responses.append(processed_data)

    return jsonify({"responses": responses})

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)


def clean_text(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_from_responses(responses):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    titles = ['Wissensfragen', 'Objektorientierte Programmierung', 'Verkettete Liste', 'Bäume', 'Fehleranalyse']

    for i, response in enumerate(responses):
        cleaned_response = clean_text(response)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, titles[i], ln=True)

        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 10, cleaned_response)
        pdf.cell(0, 10, '', ln=True)

    pdf_file_path = "antworten.pdf"
    pdf.output(pdf_file_path)
    print(f"PDF wurde unter {pdf_file_path} gespeichert.")

def your_openai_function(data):
    os.environ["OPENAI_API_KEY"] = constants.APIKEY
    PERSIST = False
    if PERSIST and os.path.exists("persist"):
        print("Reusing index...\n")
        vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings(model="code-search-ada-code-001"))
        index = VectorStoreIndexWrapper(vectorstore=vectorstore)
    else:
        loader = DirectoryLoader("data/", show_progress=True)
        if PERSIST:
            index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
        else:
            index = VectorstoreIndexCreator().from_loaders([loader])

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model=constants.Modell, temperature=1.2),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    )

    query = data
    if query in ['quit', 'q', 'exit']:
        sys.exit()

    result = chain({"question": query, "chat_history": []})

    print(result['answer'])

    return result['answer']







def feedback_openai_function(data, task):
    os.environ["OPENAI_API_KEY"] = constants.APIKEY
    # Enable to save to disk & reuse the model (for repeated queries on the same data)
    PERSIST = False
    query = None
    if len(sys.argv) > 1:
        query = sys.argv[1]

    if PERSIST and os.path.exists("persist"):
        print("Reusing index...\n")
        vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
        index = VectorStoreIndexWrapper(vectorstore=vectorstore)
    else:
    #loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
        loader = DirectoryLoader("data/")
    if PERSIST:
        index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
    else:
        index = VectorstoreIndexCreator().from_loaders([loader])

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-4"),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
    )

    chat_history = []
    while True:
        if not query:
            query = data
        if query in ['quit', 'q', 'exit']:
            sys.exit()
        result = chain({"question": query, "chat_history": task})
        print(result['answer'])

        chat_history.append((query, result['answer']))
        query = None
        return result['answer']

if __name__ == '__main__':
    app.run(port=8080)


