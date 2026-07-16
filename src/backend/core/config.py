"""Backend çekirdek yapılandırma ayarları (.env üzerinden okunur)."""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Uygulama genelinde kullanılan merkezi yapılandırma değerleri."""

    def __init__(self) -> None:
        """Çevre değişkenlerinden yapılandırma değerlerini okur."""
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql://katilim_user:katilim_password@localhost:5433/katilim_db",
        )
        # %100 çevrimdışı kuralı: model yalnızca bu yoldan yüklenir (ADR-003).
        self.local_model_path: str = os.getenv("LOCAL_MODEL_PATH", "data/models")
        self.ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_llm_model: str = os.getenv("DEFAULT_LLM_MODEL", "llama3.1:8b")


settings = Settings()
