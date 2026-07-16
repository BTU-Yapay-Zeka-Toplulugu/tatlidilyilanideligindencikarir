"""Katılım Bankası kampanya dashboard + chatbot Streamlit ön yüzü."""

from typing import Any

import streamlit as st

from src.frontend.api_client import ApiClient


def render_dashboard(client: ApiClient) -> None:
    """Karşılaştırma tablosu ve filtrelerle dashboard sekmesini çizer."""
    st.header("Kampanya Karşılaştırma Paneli")
    banks = client.get_banks()
    bank_options = {b["name"]: b["id"] for b in banks}
    selected_bank = st.selectbox("Banka seçin", ["Tümü"] + list(bank_options.keys()))

    col1, col2 = st.columns(2)
    term = col1.number_input("Vade (ay)", min_value=0, value=0, step=1)
    amount = col2.number_input("Tutar (TL)", min_value=0, value=0, step=1000)

    bank_id = bank_options.get(selected_bank) if selected_bank != "Tümü" else None
    results = client.compare(
        term_months=term or None,
        amount=amount or None,
    )
    if bank_id is not None:
        results = [r for r in results if r.get("bank_name") == selected_bank]

    if results:
        st.dataframe(results)
    else:
        st.info("Filtrelere uyan kampanya bulunamadı.")


def render_chatbot(client: ApiClient) -> None:
    """RAG tabanlı chatbot sekmesini çizer."""
    st.header("Kampanya Asistanı (RAG Chatbot)")
    question = st.text_input("Sorunuzu yazın")
    if st.button("Gönder") and question:
        try:
            answer = client.chat(question)
        except Exception as exc:  # kullanıcıya hata göster, sessiz geçme
            st.error(f"Chatbot hatası: {exc}")
            return
        st.markdown(f"**Yanıt:** {answer.get('answer', '')}")
        if answer.get("sources"):
            st.subheader("Kaynaklar")
            for src in answer["sources"]:
                st.write(f"- {src.get('id')} ({src.get('source_url')})")


def main() -> None:
    """Streamlit uygulamasını başlatır ve sekmeleri oluşturur."""
    st.set_page_config(page_title="Katılım Bankası Kampanya Analizi", layout="wide")
    st.title("Katılım Bankası Kampanya Analizi")
    client = ApiClient()
    tab1, tab2 = st.tabs(["Dashboard", "Chatbot"])
    with tab1:
        render_dashboard(client)
    with tab2:
        render_chatbot(client)


if __name__ == "__main__":
    main()
