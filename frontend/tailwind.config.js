/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // NOTE: 纯净森系主色板 —— 青柠绿（品牌主色）+ 天际蓝（点缀色）+ 大量留白
        lime: {
          50: '#f7fee7',
          100: '#ecfccb',
          200: '#d9f99d',
          300: '#bef264',
          400: '#a3e635',
          500: '#84cc16', // 主 - 青柠绿
          600: '#65a30d',
          700: '#4d7c0f',
        },
        sky: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          400: '#38bdf8',
          500: '#0ea5e9', // 点缀 - 天际蓝
          600: '#0284c7',
        },
        // 品牌语义 alias，方便在组件中调用
        brand: '#84cc16', // lime-500
        brandHover: '#65a30d', // lime-600
        accent: '#0ea5e9', // sky-500
        accentHover: '#0284c7', // sky-600
        surface: '#ffffff',
        surfaceAlt: '#f8fafc', // 极浅灰
        border: '#e2e8f0', // slate-200
        borderActive: '#84cc16',
        textMain: '#0f172a',  // slate-950
        textSub: '#475569',  // slate-600
        textMuted: '#94a3b8', // slate-400
        danger: '#ef4444',
        warning: '#f59e0b',
        success: '#22c55e',
      },
      fontFamily: {
        sans: ['Inter', 'PingFang SC', 'Noto Sans SC', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        // 克制的微阴影系统，营造"卡片浮起"的呼吸感
        card: '0 1px 3px 0 rgba(0,0,0,0.06), 0 1px 2px -1px rgba(0,0,0,0.04)',
        cardHover: '0 4px 16px 0 rgba(0,0,0,0.08), 0 2px 4px -2px rgba(0,0,0,0.06)',
        nav: '0 1px 0 0 rgba(0,0,0,0.06)',
        tag: '0 1px 2px 0 rgba(0,0,0,0.05)',
        btn: '0 1px 3px 0 rgba(132,204,22,0.25), 0 1px 2px -1px rgba(132,204,22,0.15)',
        btnHover: '0 4px 12px 0 rgba(132,204,22,0.3)',
        inputFocus: '0 0 0 3px rgba(132,204,22,0.15)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.25rem',
        card: '0.875rem',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-120%)' },
          '100%': { transform: 'translateX(120%)' },
        },
        spinSlow: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        fadeUp: 'fadeUp 0.25s ease-out',
        shimmer: 'shimmer 1.4s ease-in-out infinite',
        spin: 'spinSlow 0.8s linear infinite',
      },
    },
  },
  plugins: [],
}
