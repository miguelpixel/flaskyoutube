import os
from flask import Flask, jsonify, request, url_for , make_response, redirect, render_template
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import YoutubeLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.llms import OpenAI

app = Flask(__name__)

def getId(videourl):
    vidid=videourl.find('watch?v=')
    VId = videourl[vidid+8:vidid+19]
    if vidid==-1:
        vidid=videourl.find('be/')
        VId=videourl[vidid+3:]
    return VId

@app.route('/', methods=('GET','POST'))
def index():
    if request.method == 'POST':
        videoComplete = request.form['url']
        loader = YoutubeLoader.from_youtube_url(("https://www.youtube.com/watch?v=" + getId(videoComplete)), add_video_info=True, language = 'es')
        result = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=0)
        texts = text_splitter.split_documents(result)
        texts_trim = texts[:5]
        llm = OpenAI(temperature=0.2)
        prompt_template = """Eres un experto en Copywriting, Creame 5 titulos de máximo 50 caracteres con el siguiente texto:

        text: ```{text}```

        """
        PROMPT = PromptTemplate(template=prompt_template,input_variables=["text"])
        chain = load_summarize_chain(llm, chain_type="stuff", prompt=PROMPT)
        chain.run(texts_trim)

        return render_template('index.html',result = chain.run(texts_trim))
        
    result = request.args.get('url')
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
