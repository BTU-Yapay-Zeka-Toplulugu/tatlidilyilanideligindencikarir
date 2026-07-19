// src/chatbot/components/ChatMessage.jsx
// Bölüm 5 / Örnek 5.1: Mesaj balonu, Markdown render, Citation Badge — Chat balonları tasarımı
// ADR-007: dangerouslySetInnerHTML YASAK — ReactMarkdown ile güvenli render
// Özellikler: Kullanıcı sağa (flex-row-reverse), bot sola (flex-row) hizalı, modern rounded balonlar

import PropTypes from 'prop-types';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';
import { CodeBlock } from './CodeBlock';
import { cn } from '../../utils/styleUtils';
import { formatTarih } from '../../utils/formatters';
import { MESAJ_ROLU } from '../../constants/chatSabitleri';
import { useI18n } from '../../context/I18nContext';

const kodRenderer = ({ inline, className, children }) => {
  if (inline) {
    return (
      <code className="mx-0.5 rounded bg-black/5 px-1 py-0.5 font-mono text-xs text-black dark:bg-white/10 dark:text-white">
        {children}
      </code>
    );
  }
  const dil = /language-(\w+)/.exec(className || '')?.[1] ?? '';
  return <CodeBlock kod={String(children).replace(/\n$/, '')} dil={dil} />;
};

kodRenderer.propTypes = {
  inline:    PropTypes.bool,
  className: PropTypes.string,
  children:  PropTypes.node,
};

export const ChatMessage = ({ mesaj }) => {
  const { t } = useI18n();
  const botMu = mesaj.rol === MESAJ_ROLU.ASISTAN;

  return (
    <div
      className={cn(
        'animate-fade-in flex w-full gap-3 px-4 py-3 bg-transparent border-0 transition-colors duration-200',
        botMu ? 'flex-row' : 'flex-row-reverse'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex h-8 w-8 shrink-0 items-center justify-center rounded-full shadow-sm',
          botMu
            ? 'bg-black/10 text-black dark:bg-white/10 dark:text-white'
            : 'bg-emerald-600 text-white'
        )}
        aria-hidden="true"
      >
        {botMu ? <Bot size={16} /> : <User size={16} />}
      </div>

      {/* Mesaj Gövdesi ve Başlığı */}
      <div className={cn(
        'flex flex-col max-w-[75%] min-w-0',
        botMu ? 'items-start' : 'items-end'
      )}>
        {/* Gönderen Etiketi */}
        <span className="mb-1 text-[10px] font-semibold tracking-wider uppercase text-black/40 dark:text-white/40">
          {botMu ? t('chatbot.assistant') : t('chatbot.you')}
        </span>

        {/* Mesaj Balonu */}
        <div className={cn(
          'p-4 text-sm break-words shadow-sm',
          botMu
            ? 'bg-black/5 border border-black/5 rounded-2xl rounded-tl-none text-black dark:bg-white/5 dark:border-white/5 dark:text-white'
            : 'bg-black/10 rounded-2xl rounded-tr-none text-black dark:bg-white/10 dark:text-white'
        )}>
          <div className="prose prose-sm max-w-none break-words prose-neutral dark:prose-invert text-black dark:text-white">
            <ReactMarkdown components={{ code: kodRenderer }}>
              {mesaj.icerik}
            </ReactMarkdown>

            {/* Streaming imleci */}
            {mesaj.akisDevam && (
              <span
                className="animate-blink ml-0.5 inline-block h-4 w-0.5 rounded-sm bg-black dark:bg-white"
                aria-hidden="true"
              />
            )}
          </div>

          {/* Citation Badge */}
          {botMu && mesaj.atiflar && mesaj.atiflar.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5" aria-label={t('chatbot.sources')}>
              {mesaj.atiflar.map((atif, index) => (
                <a
                  key={index}
                  href={atif.url || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center rounded-md border px-2 py-0.5 text-[10px] font-medium shadow-sm border-black/10 bg-white/80 text-black/70 dark:border-white/10 dark:bg-black/80 dark:text-white/70 hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
                  title={`Kaynak: ${atif.bankaAdi} — ${atif.urunAdi} (Tıklayarak kaynağa gidin)`}
                >
                  [{atif.bankaAdi} — {atif.urunAdi}]
                </a>
              ))}
            </div>
          )}
        </div>

        {/* Zaman Damgası */}
        {mesaj.zaman && !mesaj.akisDevam && (
          <span className="mt-1 text-[10px] text-black/35 dark:text-white/35">
            {formatTarih(mesaj.zaman)}
          </span>
        )}
      </div>
    </div>
  );
};

ChatMessage.propTypes = {
  mesaj: PropTypes.shape({
    id:        PropTypes.string,
    rol:       PropTypes.string.isRequired,
    icerik:    PropTypes.string.isRequired,
    atiflar:   PropTypes.arrayOf(
      PropTypes.shape({
        bankaAdi: PropTypes.string.isRequired,
        urunAdi:  PropTypes.string.isRequired,
        url:      PropTypes.string,
      })
    ),
    zaman:     PropTypes.string,
    akisDevam: PropTypes.bool,
  }).isRequired,
};
