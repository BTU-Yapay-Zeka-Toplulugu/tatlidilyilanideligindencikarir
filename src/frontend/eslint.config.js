// eslint.config.js
// ESLint 9 Flat Config — kurumsal kural seti
import js from '@eslint/js';
import reactPlugin from 'eslint-plugin-react';
import reactHooksPlugin from 'eslint-plugin-react-hooks';

export default [
  js.configs.recommended,
  {
    files: ['src/**/*.{js,jsx}'],
    plugins: {
      react: reactPlugin,
      'react-hooks': reactHooksPlugin,
    },
    languageOptions: {
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        console: 'readonly',
        CustomEvent: 'readonly',
        Event: 'readonly',
        Number: 'readonly',
        Promise: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        AbortController: 'readonly',
        WebSocket: 'readonly',
        fetch: 'readonly',
        Date: 'readonly',
        JSON: 'readonly',
        String: 'readonly',
        Array: 'readonly',
        Object: 'readonly',
        Math: 'readonly',
        parseInt: 'readonly',
        parseFloat: 'readonly',
        Intl: 'readonly',
        Blob: 'readonly',
        URL:  'readonly',
        Set:  'readonly',
        navigator:            'readonly',
        requestAnimationFrame:'readonly',
        clearInterval:        'readonly',
        setInterval:          'readonly',
      },
    },
    settings: {
      react: { version: 'detect' },
    },
    rules: {
      // Kurumsal kural: Named Export zorunluluğu — default export yasak (ADR-001)
      'no-restricted-syntax': [
        'error',
        {
          selector: 'ExportDefaultDeclaration',
          message:
            'export default YASAKTIR. Named export kullanın: export const MyComponent = () => {}',
        },
      ],
      // React best practices
      ...reactPlugin.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',
      'react/prop-types': 'warn',
      // React Hooks kuralları
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      // Genel kalite
      'no-console': 'warn',
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'prefer-const': 'error',
      'no-var': 'error',
    },
  },
  {
    // Test ve config dosyaları için gevşek kurallar
    files: ['*.config.js', '*.config.cjs'],
    rules: {
      'no-restricted-syntax': 'off',
    },
  },
];
