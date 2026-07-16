"""Katılım Bankası kampanya dashboard + chatbot Streamlit ön yüzü."""

import sys
from pathlib import Path

# Streamlit betiği doğrudan çalıştırıldığında repo kökünü sys.path'e ekler
# (böylece `src` paketi bulunur).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from typing import Any

import streamlit as st

from src.frontend.api_client import ApiClient
from src.frontend.ui_helpers import filter_by_bank


def _filter_by_bank(results: list[dict], selected_bank: str) -> list[dict]:
    """Sonuçları seçili bankaya göre süzer (ui_helpers sarmalayıcısı)."""
    return filter_by_bank(results, selected_bank)


def render_dashboard(client: ApiClient) -> None:
    """Filtreler, grafik ve tabloyla tam işlevsel dashboard sekmesini çizer."""
    st.header("Kampanya Karşılaştırma Paneli")
    banks = client.get_banks()
    bank_options = [b["name"] for b in banks]
    selected_bank = st.selectbox("Banka seçin", ["Tümü"] + bank_options)

    col1, col2 = st.columns(2)
    term = col1.number_input("Vade (ay)", min_value=0, value=0, step=1)
    amount = col2.number_input("Tutar (TL)", min_value=0, value=0, step=1000)

    col3, col4 = st.columns(2)
    campaign_type = col3.text_input("Kampanya türü (opsiyonel)", "")
    top_n = col4.slider("Gösterilecek kayıt", 1, 50, 10)

    try:
        results = client.compare(
            term_months=term or None,
            amount=amount or None,
            campaign_type=campaign_type or None,
        )
    except Exception as exc:  # hata kullanıcıya gösterilir, sessiz geçilmez
        st.error(f"Karşılaştırma hatası: {exc}")
        return

    results = _filter_by_bank(results, selected_bank)[:top_n]

    if not results:
        st.info("Filtrelere uyan kampanya bulunamadı.")
        return

    st.subheader("Kâr Payı Oranı Karşılaştırması")
    chart_data = {
        "Banka": [r["bank_name"] for r in results],
        "Kâr Payı Oranı (%)": [r["profit_share_rate"] or 0 for r in results],
    }
    st.bar_chart(chart_data, x="Banka", y="Kâr Payı Oranı (%)")

    st.subheader("Detaylı Tablo")
    st.dataframe(results)


def render_chatbot(client: ApiClient) -> None:
    """Sohbet geçmişi ve kaynaklarla RAG chatbot sekmesini çizer."""
    st.header("Kampanya Asistanı (RAG Chatbot)")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Sorunuzu yazın")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            try:
                answer = client.chat(question)
            except Exception as exc:  # hata kullanıcıya gösterilir
                st.error(f"Chatbot hatası: {exc}")
                return
            st.markdown(answer.get("answer", ""))
            st.session_state.messages.append(
                {"role": "assistant", "content": answer.get("answer", "")}
            )
            if answer.get("sources"):
                st.caption("Kaynaklar: " + ", ".join(
                    str(s.get("id")) for s in answer["sources"]
                ))


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
