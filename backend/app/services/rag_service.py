from langchain_groq import ChatGroq

from app.core.config import settings
from app.services.document_service import get_vectorstore

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.2,
        )
    return _llm


SYSTEM_PROMPT = """You are a technical assistant answering questions strictly using \
the provided document excerpts. If the excerpts don't contain the answer, say so \
clearly instead of guessing. Always be precise and concise."""


def answer_query(user_id: str, query: str) -> dict:
    vectorstore = get_vectorstore(user_id)
    retriever = vectorstore.as_retriever(search_kwargs={"k": settings.TOP_K})
    relevant_docs = retriever.invoke(query)

    if not relevant_docs:
        return {
            "answer": "I couldn't find any relevant content in your uploaded documents. "
            "Please upload a document first.",
            "sources": [],
        }

    context = "\n\n".join(
        f"[Source: {d.metadata.get('filename')}, chunk {d.metadata.get('chunk_index')}]\n{d.page_content}"
        for d in relevant_docs
    )

    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question: {query}

Answer:"""

    llm = get_llm()
    response = llm.invoke(prompt)

    sources = [
        {
            "filename": d.metadata.get("filename", "unknown"),
            "chunk_index": d.metadata.get("chunk_index", -1),
            "snippet": d.page_content[:200],
        }
        for d in relevant_docs
    ]

    return {"answer": response.content, "sources": sources}
