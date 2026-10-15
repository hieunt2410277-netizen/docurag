from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "gemini"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemma-3-27b-it:free"

    chroma_path: str = "./chroma_db"
    collection_name: str = "documents"
    embedding_model: str = "BAAI/bge-m3"
    top_k: int = 5
    min_distance_threshold: float = 0.8

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
