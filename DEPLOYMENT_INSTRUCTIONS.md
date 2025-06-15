# NEO Enhanced Deployment Instructions

## 🚀 Complete Transformation Summary

Выполнена полная трансформация платформы Suna в NEO - современную, автономную и стабильную AI-агентскую платформу с локальной архитектурой.

## 📦 Что было создано

### 🏗️ Архитектурные изменения
- ✅ Миграция с Supabase на локальный PostgreSQL стек
- ✅ Замена Daytona на кастомный NEO Isolator
- ✅ Новая система аутентификации на JWT
- ✅ Локальные сервисы: PostgreSQL, Redis, MinIO, RabbitMQ
- ✅ Docker Compose оркестрация

### 🤖 Улучшения агента
- ✅ Интеллектуальная обработка ошибок с автовосстановлением
- ✅ Circuit breaker паттерн для внешних сервисов
- ✅ Адаптивное поведение и контекстная осведомленность
- ✅ Мониторинг производительности и оптимизация
- ✅ Самодиагностика и самовосстановление

### 🎨 Редизайн UI/UX
- ✅ Современная дизайн-система с NEO брендингом
- ✅ Responsive компоненты с Framer Motion анимациями
- ✅ Поддержка темной/светлой темы
- ✅ Улучшенный чат интерфейс с поддержкой файлов
- ✅ Комплексная панель управления с метриками в реальном времени

### 🛠️ Инструменты разработки
- ✅ Улучшенный менеджер сервисов (neo_manager.py)
- ✅ Кроссплатформенные установщики (PowerShell/Bash)
- ✅ Система мониторинга производительности
- ✅ Продвинутый фреймворк обработки ошибок
- ✅ Комплексное логирование и диагностика

## 🔧 Развертывание

### Вариант 1: Автоматическая установка

#### Windows
```powershell
# Скачать и запустить установщик
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/FR3R23R151/NEO/main/deploy/windows/install.ps1'))
```

#### Linux/macOS
```bash
# Скачать и запустить установщик
curl -sSL https://raw.githubusercontent.com/FR3R23R151/NEO/main/deploy/linux/install.sh | bash
```

### Вариант 2: Ручная установка

1. **Клонировать репозиторий**:
```bash
git clone https://github.com/FR3R23R151/NEO.git
cd NEO
```

2. **Настроить окружение**:
```bash
python neo_manager.py setup
```

3. **Запустить сервисы**:
```bash
python neo_manager.py start
```

### Вариант 3: Из архива (если репозиторий недоступен)

1. **Распаковать архив**:
```bash
tar -xzf NEO-enhanced-transformation.tar.gz
cd suna
```

2. **Настроить и запустить**:
```bash
python neo_manager.py setup
python neo_manager.py start
```

## 📋 Требования

### Системные требования
- **OS**: Windows 10+, Linux (Ubuntu 18.04+, CentOS 7+), macOS 10.15+
- **RAM**: Минимум 4GB, рекомендуется 8GB+
- **Диск**: Минимум 10GB свободного места
- **CPU**: 2+ ядра

### Программные зависимости
Установщики автоматически установят:
- Docker Desktop (Windows/macOS) или Docker Engine (Linux)
- Python 3.8+ с Poetry
- Node.js 18+ с npm
- Git

## 🚀 Запуск

### После установки

1. **Запуск всех сервисов**:
```bash
# Windows
.\scripts\windows\start.bat

# Linux/macOS
./scripts/unix/start.sh

# Или через менеджер
python neo_manager.py start
```

2. **Доступ к интерфейсам**:
- 🌐 **NEO Web Interface**: http://localhost:3000
- 📚 **API Documentation**: http://localhost:8000/docs
- 🔧 **Backend API**: http://localhost:8000
- ⚙️ **Isolator Service**: http://localhost:8001
- 📦 **MinIO Console**: http://localhost:9001
- 🐰 **RabbitMQ Management**: http://localhost:15672

### Мониторинг

```bash
# Статус сервисов
python neo_manager.py status --detailed

# Мониторинг в реальном времени
python neo_manager.py monitor

# Проверка здоровья
python neo_manager.py health --fix
```

## 🔧 Конфигурация

### Основные файлы конфигурации

1. **Backend** (`backend/.env`):
```bash
# Database
DATABASE_URL=postgresql://neo_user:neo_password@localhost:5432/neo_db

# Redis
REDIS_URL=redis://localhost:6379

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=neo_minio
MINIO_SECRET_KEY=neo_minio_password

# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

2. **Frontend** (`frontend/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ISOLATOR_URL=http://localhost:8001
NEXT_PUBLIC_MINIO_URL=http://localhost:9000
```

## 📊 Ключевые файлы

### Новые компоненты
- `backend/agent/enhanced_agent.py` - Улучшенный агент с автовосстановлением
- `backend/utils/error_handler.py` - Система обработки ошибок
- `backend/utils/performance_monitor.py` - Мониторинг производительности
- `backend/isolator/` - Кастомный изолятор сервис
- `backend/services/database.py` - Новый сервис базы данных
- `backend/services/auth.py` - JWT аутентификация
- `backend/services/storage.py` - MinIO интеграция
- `neo_manager.py` - Улучшенный менеджер сервисов

### UI/UX компоненты
- `frontend/src/components/ui/neo-*.tsx` - Новые UI компоненты
- `frontend/src/components/layouts/neo-layout.tsx` - Основной layout
- `frontend/src/styles/neo-theme.css` - Тема NEO
- `frontend/tailwind.config.js` - Конфигурация Tailwind

### Установщики
- `deploy/windows/install.ps1` - Windows установщик
- `deploy/linux/install.sh` - Linux/macOS установщик

## 📚 Документация

### Основные документы
- `README_ENHANCED.md` - Полное руководство пользователя
- `MIGRATION_REPORT.md` - Отчет о миграции с Supabase
- `AGENT_ENHANCEMENT_REPORT.md` - Улучшения агента
- `UI_UX_REDESIGN_REPORT.md` - Редизайн интерфейса
- `docs/ARCHITECTURE.md` - Архитектура системы
- `frontend/NEO_DESIGN_SYSTEM.md` - Дизайн-система

## 🔍 Диагностика

### Проверка установки
```bash
# Проверка всех компонентов
python neo_manager.py health

# Детальный статус
python neo_manager.py status --detailed

# Просмотр логов
python neo_manager.py logs --follow
```

### Решение проблем

1. **Сервисы не запускаются**:
```bash
# Проверить Docker
docker info

# Перезапустить сервисы
python neo_manager.py stop
python neo_manager.py start
```

2. **Проблемы с производительностью**:
```bash
# Мониторинг ресурсов
python neo_manager.py monitor

# Автоисправление
python neo_manager.py health --fix
```

3. **Ошибки базы данных**:
```bash
# Сброс базы данных
docker-compose down
docker volume rm suna_postgres_data
python neo_manager.py start
```

## 🎯 Следующие шаги

1. **Тестирование**: Запустить полное тестирование системы
2. **Настройка**: Добавить API ключи для LLM моделей
3. **Кастомизация**: Настроить под специфические требования
4. **Мониторинг**: Настроить алерты и мониторинг
5. **Бэкапы**: Настроить регулярные бэкапы данных

## 🆘 Поддержка

### Получение помощи
1. Проверить логи: `python neo_manager.py logs`
2. Запустить диагностику: `python neo_manager.py health`
3. Изучить документацию в папке `docs/`
4. Создать issue в GitHub репозитории

### Контакты
- **GitHub**: https://github.com/FR3R23R151/NEO
- **Issues**: https://github.com/FR3R23R151/NEO/issues

## ✅ Чеклист развертывания

- [ ] Установлены все зависимости (Docker, Python, Node.js)
- [ ] Клонирован/распакован репозиторий
- [ ] Запущена команда `python neo_manager.py setup`
- [ ] Настроены файлы конфигурации (.env)
- [ ] Добавлены API ключи для LLM моделей
- [ ] Запущены сервисы `python neo_manager.py start`
- [ ] Проверен статус `python neo_manager.py status`
- [ ] Доступен веб-интерфейс http://localhost:3000
- [ ] Протестирована работа агента
- [ ] Настроен мониторинг и алерты

---

**🎉 Поздравляем! NEO готов к использованию!**

Теперь у вас есть полнофункциональная AI-агентская платформа с улучшенной стабильностью, автономностью и современным интерфейсом.