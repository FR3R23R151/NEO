# NEO Design System

## Overview

NEO Design System представляет собой современную, адаптивную систему дизайна для AI-платформы NEO. Система построена на принципах минимализма, функциональности и превосходного пользовательского опыта.

## Принципы дизайна

### 1. **Clarity First** (Ясность прежде всего)
- Четкая иерархия информации
- Интуитивная навигация
- Понятные визуальные сигналы

### 2. **Performance Focused** (Ориентированность на производительность)
- Оптимизированные анимации
- Эффективное использование ресурсов
- Быстрая загрузка компонентов

### 3. **Accessibility** (Доступность)
- Поддержка клавиатурной навигации
- Высокий контраст цветов
- Семантическая разметка

### 4. **Consistency** (Последовательность)
- Единообразные паттерны взаимодействия
- Согласованная типографика
- Стандартизированные компоненты

## Цветовая палитра

### Основные цвета

```css
/* Primary Brand Colors */
--neo-primary: #6366f1;        /* Indigo 500 */
--neo-primary-dark: #4f46e5;   /* Indigo 600 */
--neo-primary-light: #818cf8;  /* Indigo 400 */
--neo-primary-50: #eef2ff;
--neo-primary-100: #e0e7ff;
--neo-primary-900: #312e81;

/* Secondary Colors */
--neo-secondary: #06b6d4;      /* Cyan 500 */
--neo-secondary-dark: #0891b2; /* Cyan 600 */
--neo-secondary-light: #22d3ee; /* Cyan 400 */

/* Accent Colors */
--neo-accent: #f59e0b;         /* Amber 500 */
--neo-accent-dark: #d97706;    /* Amber 600 */
--neo-accent-light: #fbbf24;   /* Amber 400 */
```

### Семантические цвета

```css
/* Status Colors */
--neo-success: #10b981;        /* Emerald 500 */
--neo-error: #ef4444;          /* Red 500 */
--neo-warning: #f59e0b;        /* Amber 500 */
```

### Нейтральные цвета

```css
/* Light Mode */
--neo-gray-50: #f9fafb;
--neo-gray-100: #f3f4f6;
--neo-gray-200: #e5e7eb;
--neo-gray-300: #d1d5db;
--neo-gray-400: #9ca3af;
--neo-gray-500: #6b7280;
--neo-gray-600: #4b5563;
--neo-gray-700: #374151;
--neo-gray-800: #1f2937;
--neo-gray-900: #111827;
```

## Типографика

### Шрифтовая система

```css
/* Font Families */
--font-sans: 'Geist Sans', ui-sans-serif, system-ui;
--font-mono: 'Geist Mono', ui-monospace, 'SF Mono';

/* Font Sizes */
--neo-text-xs: 0.75rem;    /* 12px */
--neo-text-sm: 0.875rem;   /* 14px */
--neo-text-base: 1rem;     /* 16px */
--neo-text-lg: 1.125rem;   /* 18px */
--neo-text-xl: 1.25rem;    /* 20px */
--neo-text-2xl: 1.5rem;    /* 24px */
--neo-text-3xl: 1.875rem;  /* 30px */
--neo-text-4xl: 2.25rem;   /* 36px */
--neo-text-5xl: 3rem;      /* 48px */
```

### Типографические классы

```css
.neo-heading-1 { /* 48px/60px, bold */ }
.neo-heading-2 { /* 36px/44px, bold */ }
.neo-heading-3 { /* 30px/36px, semibold */ }
.neo-heading-4 { /* 24px/32px, semibold */ }
.neo-body-large { /* 18px/28px, regular */ }
.neo-body { /* 16px/24px, regular */ }
.neo-body-small { /* 14px/20px, regular */ }
```

## Компоненты

### Кнопки

#### Основные стили
```css
.neo-btn-primary {
  background: linear-gradient(135deg, var(--neo-primary), var(--neo-primary-dark));
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 200ms ease;
}

.neo-btn-secondary {
  background: linear-gradient(135deg, var(--neo-secondary), var(--neo-secondary-dark));
  color: white;
}

.neo-btn-outline {
  border: 1px solid var(--neo-border-medium);
  background: transparent;
  color: var(--neo-text-primary);
}

.neo-btn-ghost {
  background: transparent;
  color: var(--neo-text-primary);
}
```

#### Состояния
- **Hover**: Увеличение тени, легкое масштабирование (scale: 1.02)
- **Active**: Уменьшение масштаба (scale: 0.98)
- **Focus**: Кольцо фокуса с цветом primary
- **Disabled**: Opacity 50%, cursor not-allowed

### Карточки

#### Glass Card
```css
.neo-glass-card {
  background: var(--neo-glass-bg);
  backdrop-filter: blur(16px);
  border: 1px solid var(--neo-glass-border);
  box-shadow: var(--neo-glass-shadow);
  border-radius: 12px;
}
```

#### Интерактивные карточки
```css
.neo-card-interactive {
  transition: all 200ms ease;
}

.neo-card-interactive:hover {
  transform: translateY(-2px);
  box-shadow: var(--neo-shadow-lg);
}
```

### Формы

#### Поля ввода
```css
.neo-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--neo-border-light);
  border-radius: 8px;
  background: var(--neo-bg-primary);
  color: var(--neo-text-primary);
  transition: all 200ms ease;
}

.neo-input:focus {
  outline: none;
  ring: 2px solid var(--neo-primary);
  border-color: transparent;
}
```

### Навигация

#### Боковая панель
- Адаптивная ширина (280px развернуто, 80px свернуто)
- Плавные анимации переходов
- Tooltips для свернутого состояния
- Активные индикаторы с motion layout

#### Верхняя панель
- Поиск с клавиатурными сокращениями (⌘K)
- Уведомления с счетчиком
- Переключатель темы
- Профиль пользователя

## Анимации

### Принципы анимации

1. **Easing**: Используем cubic-bezier для естественных движений
2. **Duration**: 150ms для быстрых, 250ms для обычных, 350ms для медленных
3. **Staging**: Последовательные анимации с задержками

### Ключевые анимации

```css
/* Fade In */
@keyframes neo-fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Scale In */
@keyframes neo-scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

/* Slide In */
@keyframes neo-slide-in-right {
  from { opacity: 0; transform: translateX(100%); }
  to { opacity: 1; transform: translateX(0); }
}
```

### Framer Motion паттерны

```tsx
// Stagger Children
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

// Item Animation
const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}
```

## Темная тема

### Автоматическое переключение
- Определение системных предпочтений
- Сохранение выбора пользователя
- Плавные переходы между темами

### Цветовые адаптации
```css
.dark {
  --neo-bg-primary: #0f172a;
  --neo-bg-secondary: #1e293b;
  --neo-bg-tertiary: #334155;
  --neo-text-primary: #f8fafc;
  --neo-text-secondary: #cbd5e1;
  --neo-text-tertiary: #94a3b8;
}
```

## Адаптивность

### Breakpoints
```css
/* Mobile First Approach */
sm: 640px   /* Small devices */
md: 768px   /* Medium devices */
lg: 1024px  /* Large devices */
xl: 1280px  /* Extra large devices */
2xl: 1536px /* 2X Extra large devices */
```

### Адаптивные паттерны

1. **Navigation**: Hamburger menu на мобильных
2. **Grid**: Автоматическая адаптация колонок
3. **Typography**: Масштабирование размеров шрифтов
4. **Spacing**: Уменьшение отступов на мобильных

## Accessibility

### Клавиатурная навигация
- Tab order для всех интерактивных элементов
- Escape для закрытия модальных окон
- Enter/Space для активации кнопок
- Arrow keys для навигации по спискам

### ARIA атрибуты
```tsx
// Примеры использования
<button aria-label="Close dialog" aria-expanded="false">
<div role="dialog" aria-modal="true">
<input aria-describedby="error-message" aria-invalid="true">
```

### Цветовой контраст
- Минимум 4.5:1 для обычного текста
- Минимум 3:1 для крупного текста
- Дополнительные визуальные индикаторы помимо цвета

## Производительность

### Оптимизации
1. **Lazy Loading**: Компоненты загружаются по требованию
2. **Code Splitting**: Разделение бандлов по маршрутам
3. **Image Optimization**: WebP формат, responsive images
4. **CSS Optimization**: Purging неиспользуемых стилей

### Мониторинг
- Core Web Vitals
- Bundle size analysis
- Runtime performance profiling

## Использование

### Установка зависимостей
```bash
npm install @heroicons/react framer-motion tailwindcss
```

### Импорт компонентов
```tsx
import { NEOLayout } from '@/components/layouts/neo-layout'
import { NEODashboard } from '@/components/ui/neo-dashboard'
import { NEOChat } from '@/components/ui/neo-chat'
import { NEOAuth } from '@/components/ui/neo-auth'
```

### Использование утилит
```tsx
import { cn } from '@/lib/utils'

// Объединение классов
className={cn('base-class', condition && 'conditional-class')}
```

## Примеры

### Демо-страница
Доступна по адресу `/neo-demo` для тестирования всех компонентов.

### Основные компоненты
1. **NEONavigation**: Адаптивная боковая навигация
2. **NEODashboard**: Информационная панель с метриками
3. **NEOChat**: Интерфейс чата с AI агентами
4. **NEOAuth**: Страницы входа и регистрации
5. **NEOLayout**: Основной layout приложения

## Roadmap

### Ближайшие планы
- [ ] Компонент таблиц данных
- [ ] Расширенные формы
- [ ] Drag & Drop интерфейсы
- [ ] Графики и визуализации
- [ ] Мобильное приложение

### Долгосрочные цели
- [ ] Система тем (кастомизация)
- [ ] Компонентная библиотека
- [ ] Storybook документация
- [ ] Автоматизированное тестирование UI

## Поддержка

Для вопросов по дизайн-системе обращайтесь к команде разработки NEO или создавайте issues в репозитории проекта.