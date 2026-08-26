from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "RAG Technical Document Assistant"

    # --- Database ---
    DATABASE_URL: str = "postgresql://rag_user:rag_pass@db:5432/rag_db"

    # --- Auth ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # --- LLM (Groq - free tier) ---
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # --- Embeddings (fastembed, ONNX-based, no torch required) ---
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # --- Vector store ---
    CHROMA_PERSIST_DIR: str = "./chroma_store"

    # --- Chunking ---
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 4

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
