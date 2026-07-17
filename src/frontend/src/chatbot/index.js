// src/chatbot/index.js
// Barrel export — Chatbot modülünün Public API noktası
// İç yapı değişse bile import yolları kırılmaz (Bölüm 2 Best Practices)

// Sayfalar
export { ChatbotPage } from './pages/ChatbotPage';

// Bileşenler
export { ChatMessage }     from './components/ChatMessage';
export { ChatInput }       from './components/ChatInput';
export { SuggestionChips } from './components/SuggestionChips';
export { TypingIndicator } from './components/TypingIndicator';
export { CodeBlock }       from './components/CodeBlock';

// Servisler
export {
  mesajGonder,
  sohbetGecmisiniGetir,
  oturumuTemizle,
  streamingBaglantiOlustur,
} from './services/chatApi';

// Hook'lar
export { useStreamingResponse } from './hooks/useStreamingResponse';
export { useChat }              from './hooks/useChat';
