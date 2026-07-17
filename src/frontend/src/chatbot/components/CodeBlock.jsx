// src/chatbot/components/CodeBlock.jsx
// Bölüm 5 / Acceptance Criteria: Kod bloklarında syntax highlighter + "Kopyala" butonu
// ADR-007: dangerouslySetInnerHTML YASAK — react-syntax-highlighter güvenli render yapar
// Bölüm 7 Performans: PrismLight ile sadece gerekli diller yüklenir (küçük bundle)
// Named Export — export default YASAKTIR

import { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import { PrismLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';
import { useI18n } from '../../context/I18nContext';

// Sadece ihtiyaç duyulan diller — tree-shaking dostu (Bölüm 7 Performans)
import python     from 'react-syntax-highlighter/dist/esm/languages/prism/python';
import javascript from 'react-syntax-highlighter/dist/esm/languages/prism/javascript';
import json       from 'react-syntax-highlighter/dist/esm/languages/prism/json';
import bash       from 'react-syntax-highlighter/dist/esm/languages/prism/bash';
import sql        from 'react-syntax-highlighter/dist/esm/languages/prism/sql';

SyntaxHighlighter.registerLanguage('python',     python);
SyntaxHighlighter.registerLanguage('javascript', javascript);
SyntaxHighlighter.registerLanguage('js',         javascript);
SyntaxHighlighter.registerLanguage('json',       json);
SyntaxHighlighter.registerLanguage('bash',       bash);
SyntaxHighlighter.registerLanguage('shell',      bash);
SyntaxHighlighter.registerLanguage('sql',        sql);

const KOPYALAMA_GERI_BILDIRIM_MS = 2000;

/**
 * Syntax highlighted kod bloğu — sağ üstte "Kopyala" butonu ile.
 * @param {object} props
 * @param {string} props.kod      - Kod içeriği
 * @param {string} [props.dil]    - Programlama dili (ör: 'python', 'javascript')
 */
export const CodeBlock = ({ kod, dil = '' }) => {
  const { t } = useI18n();
  const [kopyalandi, setKopyalandi] = useState(false);

  const kopyala = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(kod);
      setKopyalandi(true);
      setTimeout(() => setKopyalandi(false), KOPYALAMA_GERI_BILDIRIM_MS);
    } catch {
      // Clipboard API desteklenmiyorsa sessizce geç
    }
  }, [kod]);

  return (
    <div className="group relative my-3 overflow-hidden rounded-md border border-black/10 dark:border-white/10 bg-black">
      {/* Dil etiketi + Kopyala butonu — sağ üst köşe (Acceptance Criteria) */}
      <div className="flex items-center justify-between border-b border-black/10 dark:border-white/10 px-4 py-2 bg-neutral-900/50">
        <span className="text-xs font-medium text-white/50">
          {dil || 'kod'}
        </span>
        <button
          onClick={kopyala}
          aria-label={t('chatbot.copyCode')}
          className="flex items-center gap-1.5 rounded px-2 py-1 text-xs text-white/50 transition-colors hover:bg-white/10 hover:text-white focus:outline-none focus:ring-0 outline-none"
        >
          {kopyalandi ? (
            <>
              <Check size={12} aria-hidden="true" />
              {t('chatbot.copied')}
            </>
          ) : (
            <>
              <Copy size={12} aria-hidden="true" />
              {t('chatbot.copyCode')}
            </>
          )}
        </button>
      </div>

      {/* Syntax Highlighter — ADR-007: güvenli render, XSS yok */}
      <SyntaxHighlighter
        language={dil}
        style={vscDarkPlus}
        customStyle={{
          margin: 0,
          padding: '1rem',
          background: 'transparent',
          fontSize: '0.8125rem',
          lineHeight: '1.6',
        }}
        showLineNumbers={kod.split('\n').length > 5}
        wrapLongLines
      >
        {kod}
      </SyntaxHighlighter>
    </div>
  );
};

CodeBlock.propTypes = {
  kod: PropTypes.string.isRequired,
  dil: PropTypes.string,
};
