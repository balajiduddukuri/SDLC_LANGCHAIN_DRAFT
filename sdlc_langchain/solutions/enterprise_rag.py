import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from providers.provider_factory import LLMProviderFactory

class EnterpriseRAG:
    """Production-grade RAG implementation."""
    
    def __init__(self, docs_path: str = None):
        self.embeddings = OpenAIEmbeddings()
        self.provider = LLMProviderFactory.create_from_config()
        self.vector_store = None
        
    def index_documents(self, texts: List[str]):
        """Create FAISS index from text chunks."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.create_documents(texts)
        self.vector_store = FAISS.from_documents(splits, self.embeddings)
        
    def get_answer(self, query: str):
        """Query the RAG system."""
        if not self.vector_store:
            return "Knowledge base not initialized."
            
        system_prompt = (
            "You are an enterprise knowledge assistant. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, say that you don't know. "
            "\n\n"
            "{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(self.provider.llm, prompt)
        retriever = self.vector_store.as_retriever()
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        response = rag_chain.invoke({"input": query})
        return response["answer"]

if __name__ == "__main__":
    rag = EnterpriseRAG()
    rag.index_documents(["Enterprise Policy: Friday is Pizza Day.", "HR: 20 days PTO for all."])
    print(rag.get_answer("What happens on Friday?"))
