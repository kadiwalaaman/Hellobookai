"""
RAG Engine for Hellobooks
Handles document loading, embedding, FAISS indexing, and LLM querying via Ollama.
"""

import os
import pickle
from pathlib import Path
from typing import List, Tuple

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge_base"
FAISS_INDEX_PATH = Path(__file__).parent / "faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2"  # Change to your available Ollama model
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


PROMPT_TEMPLATE = """You are Hellobooks AI, a helpful accounting and bookkeeping assistant. 
Use the following context from the Hellobooks knowledge base to answer the user's question accurately and clearly.
If the answer is not in the context, say you don't have enough information but offer general guidance.

Context:
{context}

Question: {question}

Answer in a clear, professional, and friendly tone:"""


class RAGEngine:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self._initialize()

    def _initialize(self):
        """Load or build the FAISS index and set up the QA chain."""
        print("Initializing RAG Engine...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        if FAISS_INDEX_PATH.exists():
            print("Loading existing FAISS index...")
            self.vectorstore = FAISS.load_local(
                str(FAISS_INDEX_PATH),
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
        else:
            print("Building new FAISS index from knowledge base...")
            self.vectorstore = self._build_index()

        self._setup_qa_chain()
        print("RAG Engine ready.")

    def _load_documents(self):
        """Load all markdown files from the knowledge base directory."""
        loader = DirectoryLoader(
            str(KNOWLEDGE_BASE_DIR),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=80,
            separators=["\n## ", "\n### ", "\n\n", "\n", " "],
        )
        return splitter.split_documents(docs)

    def _build_index(self) -> FAISS:
        """Build and save FAISS index."""
        chunks = self._load_documents()
        print(f"Loaded {len(chunks)} document chunks.")
        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        vectorstore.save_local(str(FAISS_INDEX_PATH))
        print(f"FAISS index saved to {FAISS_INDEX_PATH}")
        return vectorstore

    def rebuild_index(self):
        """Force rebuild the FAISS index."""
        import shutil
        if FAISS_INDEX_PATH.exists():
            shutil.rmtree(FAISS_INDEX_PATH)
        self.vectorstore = self._build_index()
        self._setup_qa_chain()

    def _setup_qa_chain(self):
        """Set up the LangChain RetrievalQA chain with Ollama."""
        llm = OllamaLLM(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.2,
        )

        prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["context", "question"],
        )

        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

    def query(self, question: str) -> dict:
        """Run a question through the RAG pipeline."""
        if not self.qa_chain:
            raise RuntimeError("QA chain not initialized.")

        result = self.qa_chain.invoke({"query": question})

        sources = []
        for doc in result.get("source_documents", []):
            source_path = doc.metadata.get("source", "")
            source_name = Path(source_path).stem.replace("_", " ").title()
            if source_name not in sources:
                sources.append(source_name)

        return {
            "answer": result["result"],
            "sources": sources,
        }


# Singleton instance
_engine = None

def get_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine
