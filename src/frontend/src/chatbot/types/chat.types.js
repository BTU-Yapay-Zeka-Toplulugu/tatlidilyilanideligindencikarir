// src/chatbot/types/chat.types.js
// JSDoc tip tanımları — TypeScript olmadan tip güvenliği
// Named Export — export default YASAKTIR

/**
 * @typedef {'user'|'assistant'} MesajRolu
 */

/**
 * @typedef {object} Atif
 * @property {string} bankaAdi   - Örn: "Kuveyt Türk"
 * @property {string} urunAdi    - Örn: "Araç Finansmanı"
 * @property {string} [url]      - Opsiyonel belge linki
 */

/**
 * @typedef {object} Mesaj
 * @property {string}      id         - Benzersiz mesaj kimliği
 * @property {MesajRolu}   rol        - 'user' veya 'assistant'
 * @property {string}      icerik     - Markdown içerik (react-markdown ile render edilir)
 * @property {Atif[]}      [atiflar]  - RAG kaynakçaları (yalnızca assistant mesajlarında)
 * @property {string}      zaman      - ISO 8601 formatı (formatTarih ile gösterilir)
 * @property {boolean}     [akisDevam] - true ise streaming henüz bitmedi
 */

/**
 * @typedef {object} ChatYanitiResponse
 * @property {string}  oturumId
 * @property {Mesaj}   mesaj
 */

/**
 * @typedef {Mesaj[]} MesajListesiResponse
 */

export {};
