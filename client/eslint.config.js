// ESM flat config для ESLint v9
import js from '@eslint/js'
import globals from 'globals'
import vue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'

export default [
  // игнор теперь тут
  { ignores: ['dist', 'node_modules', '.vite', 'coverage'] },

  // базовые рекомендации
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...vue.configs['flat/recommended'], // ← был корень ошибки: нужен spread

  // общие language options
  {
    files: ['**/*.{js,jsx,ts,tsx,vue}'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      globals: { ...globals.browser, ...globals.node },
    },
  },

  // Vue + TS внутри <script> у .vue
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
        ecmaVersion: 2023,
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
      },
    },
    rules: {
      'vue/multi-word-component-names': 'off',
    },
  },
]
