import os
import shutil
import uuid

from fastembed import TextEmbedding
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings

from app.core.config import settings


class FastEmbedEmbeddings(Embeddings):
    """Thin LangChain-compatible wrapper around fastembed.

    Avoids pulling in sentence-transformers/torch (2GB+), which is overkill
    for this project and slow to install/deploy. fastembed uses ONNX runtime
    under the hood and is CPU-friendly and lightweight.
    """

    def __init__(self, model_name: str):
        self._model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vec.tolist() for vec in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._model.embed([text]))).tolist()


_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = FastEmbedEmbeddings(settings.EMBEDDING_MODEL)
    return _embeddings


def get_vectorstore(user_id: str) -> Chroma:
    """Each user gets an isolated Chroma collection so docs don't leak across accounts."""
    persist_dir = os.path.join(settings.CHROMA_PERSIST_DIR, user_id)
    os.makedirs(persist_dir, exist_ok=True)
    return Chroma(
        collection_name=f"user_{user_id}",
        embedding_function=get_embeddings(),
        persist_directory=persist_dir,
    )


def load_document(file_path: str, filename: str):
    if filename.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif filename.lower().endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")
    return loader.load()


def ingest_document(user_id: str, tmp_file_path: str, filename: str) -> int:
    """Load -> chunk -> embed -> persist. Returns number of chunks created."""
    docs = load_document(tmp_file_path, filename)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)

    # Attach metadata used later for citations
    for i, chunk in enumerate(chunks):
        chunk.metadata["filename"] = filename
        chunk.metadata["chunk_index"] = i
        chunk.metadata["doc_id"] = str(uuid.uuid4())

    if not chunks:
        raise ValueError(
            "No extractable text found in this document. It may be scanned, "
            "image-only, or empty — try a text-based PDF/DOCX."
        )

    vectorstore = get_vectorstore(user_id)
    # Note: since Chroma 0.4.x, documents are auto-persisted on add — no
    # explicit .persist() call needed (it's deprecated/a no-op now).
    vectorstore.add_documents(chunks)

    return len(chunks)


def delete_user_store(user_id: str):
    persist_dir = os.path.join(settings.CHROMA_PERSIST_DIR, user_id)
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
