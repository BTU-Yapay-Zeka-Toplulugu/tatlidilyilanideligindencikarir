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
        self.local_model_path: str = os.getenv("LOCAL_MODEL_PATH", "model")
        # Görev bazlı model yolları: her modül kendi model dizinine işaret eder.
        # Bir dizin verilirse içindeki ilk .gguf otomatik yüklenir; ileride
        # her alt dizine ayrı model koymak kolaylaşır.
        self.main_responser_model_path: str = os.getenv(
            "MAIN_RESPONSER_MODEL_PATH", "model/main_responser"
        )
        self.data_cleaner_model_path: str = os.getenv(
            "DATA_CLEANER_MODEL_PATH", "model/data_cleaner"
        )
        self.extractor_model_path: str = os.getenv(
            "EXTRACTOR_MODEL_PATH", "model/extractor"
        )
        self.classifier_model_path: str = os.getenv(
            "CLASSIFIER_MODEL_PATH", "model/classifier"
        )
        self.embedder_model_path: str = os.getenv(
            "EMBEDDER_MODEL_PATH", "model/embedder"
        )
        self.comparison_model_path: str = os.getenv(
            "COMPARISON_MODEL_PATH", "model/comparison"
        )
        self.ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_llm_model: str = os.getenv("DEFAULT_LLM_MODEL", "llama3.1:8b")
        # LLM backend seçimi: auto | gguf | ollama (auto -> .gguf varsa gguf)
        self.llm_backend: str = os.getenv("LLM_BACKEND", "auto")


settings = Settings()
