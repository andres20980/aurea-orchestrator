# 🎯 TU PLAN DE ACCIÓN - Gemini + OpenAI

## ✅ Lo que YA está configurado

1. ✅ Proyecto adaptado para usar **Google Gemini** (en lugar de Anthropic/Claude)
2. ✅ Soporte para **OpenAI GPT-4** como alternativa
3. ✅ Model router inteligente que selecciona el mejor modelo según complejidad
4. ✅ Dependencies actualizadas (langchain-google-genai)
5. ✅ Scripts de setup automatizados
6. ✅ Documentación completa en inglés

## 🔑 PASO 1: Conseguir API Keys (5 minutos)

### Gemini API (RECOMENDADO - Gratis y potente)
```bash
1. Ve a: https://makersuite.google.com/app/apikey
2. Inicia sesión con tu cuenta Google
3. Click en "Create API Key"
4. Copia la key (formato: AIzaSy...)
```

**Límites FREE:**
- ✅ 60 requests/minuto
- ✅ 1,500 requests/día
- ✅ Gemini 1.5 Flash - Súper rápido
- ✅ Gemini 1.5 Pro - Muy capaz

### OpenAI API (Opcional - De pago)
```bash
1. Ve a: https://platform.openai.com/api-keys
2. Inicia sesión
3. Click en "Create new secret key"
4. Copia la key (formato: sk-proj-...)
5. Añade créditos en: https://platform.openai.com/account/billing
```

**Costos:**
- GPT-4 Turbo: $10 input / $30 output por 1M tokens
- GPT-3.5 Turbo: $0.50 input / $1.50 output por 1M tokens

### Office 365 / Azure OpenAI (Si tienes cuenta empresa)
```bash
Si tu empresa tiene Azure OpenAI:
1. Ve a Azure Portal
2. Busca "Azure OpenAI Service"
3. Obtén tu endpoint y key
4. Configurarlo es diferente (ver SETUP_GEMINI.md)
```

## 🚀 PASO 2: Setup Rápido (3 comandos)

```bash
cd /home/asanchez/Code/github-andres20980/aurea-orchestrator

# Ejecuta el setup interactivo
./setup_gemini.sh

# Te pedirá las API keys y configurará todo automáticamente
# Opción: edita .env manualmente si prefieres
vi .env
```

## ⚙️ PASO 3: Configuración del .env

Tu archivo `.env` debe quedar así:

```bash
# API Keys
GOOGLE_API_KEY=AIzaSy...tu_key_de_gemini
OPENAI_API_KEY=sk-proj-...tu_key_de_openai  # Opcional

# Database (ya está bien configurado)
DATABASE_URL=postgresql://aurea:aurea_pass@localhost:5432/aurea_orchestrator

# Redis (ya está bien configurado)
REDIS_URL=redis://localhost:6379/0

# Model Configuration
GEMINI_MODEL=gemini-1.5-flash      # O gemini-1.5-pro
OPENAI_MODEL=gpt-4                  # Solo si tienes OpenAI
COMPLEXITY_THRESHOLD=0.5            # 0-1, cuándo usar modelo complejo
DEFAULT_MODEL_PROVIDER=gemini       # gemini u openai

# App
DEBUG=true
LOG_LEVEL=INFO
```

## 🎮 PASO 4: Probar que funciona

```bash
# 1. Levantar servicios
docker-compose up

# En otra terminal:

# 2. Test básico
curl http://localhost:8000/health

# 3. Crear una tarea
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a Python function that calculates fibonacci numbers",
    "metadata": {"priority": "high"}
  }'

# Respuesta esperada:
# {"task_id": "abc-123-xyz", "status": "queued"}

# 4. Ver estado de la tarea
curl http://localhost:8000/tasks/abc-123-xyz

# 5. Ver API docs interactiva
# Abre: http://localhost:8000/docs
```

## 💰 RECOMENDACIÓN: Solo Gemini

Para empezar, te recomiendo **SOLO GEMINI**:

```bash
# .env
GOOGLE_API_KEY=tu_key_aqui
# OPENAI_API_KEY=  # <-- Déjalo comentado o vacío

GEMINI_MODEL=gemini-1.5-flash
DEFAULT_MODEL_PROVIDER=gemini
```

**¿Por qué?**
- ✅ **GRATIS** hasta 1,500 requests/día
- ✅ **MUY RÁPIDO** (1-2 segundos)
- ✅ **EXCELENTE CALIDAD** para tareas de código
- ✅ **50x MÁS BARATO** que GPT-4 (si pagas)

## 🔧 Si tienes Office 365 con Azure

Si tu empresa tiene **Azure OpenAI**:

1. Pregunta a tu admin por:
   - Azure OpenAI Endpoint
   - Azure OpenAI API Key
   - Deployment Name (ej: gpt-4)

2. Añade a `.env`:
```bash
AZURE_OPENAI_ENDPOINT=https://tu-empresa.openai.azure.com/
AZURE_OPENAI_KEY=tu_azure_key
AZURE_OPENAI_DEPLOYMENT=gpt-4
USE_AZURE_OPENAI=true
```

**Ventajas:**
- ✅ Ya pagado por tu empresa
- ✅ Sin límites (según tu suscripción)
- ✅ Cumplimiento GDPR/enterprise

## 📊 Comparación de modelos

| Modelo | Velocidad | Calidad Código | Costo | Recomendación |
|--------|-----------|----------------|-------|---------------|
| **Gemini 1.5 Flash** | ⚡⚡⚡ | ⭐⭐⭐⭐ | 💰 GRATIS | ✅ EMPIEZA AQUÍ |
| Gemini 1.5 Pro | ⚡⚡ | ⭐⭐⭐⭐⭐ | 💰💰 | Para tasks complejas |
| GPT-4 Turbo | ⚡ | ⭐⭐⭐⭐⭐ | 💰💰💰 | Solo si Gemini no vale |
| GPT-3.5 Turbo | ⚡⚡⚡ | ⭐⭐⭐ | 💰 | No recomendado |

## ✅ CHECKLIST Antes de Empezar

- [ ] Obtener Gemini API key de https://makersuite.google.com/app/apikey
- [ ] (Opcional) Obtener OpenAI API key de https://platform.openai.com/api-keys
- [ ] Ejecutar `./setup_gemini.sh`
- [ ] Verificar `.env` tiene las keys correctas
- [ ] Ejecutar `docker-compose up`
- [ ] Probar http://localhost:8000/health
- [ ] Crear una tarea de prueba
- [ ] Ver docs en http://localhost:8000/docs

## 🆘 Troubleshooting

### "API key not found"
```bash
# Verifica que tu .env tenga:
cat .env | grep GOOGLE_API_KEY
# Debe mostrar: GOOGLE_API_KEY=AIzaSy...
```

### "Docker not running"
```bash
sudo systemctl start docker
# O abre Docker Desktop
```

### "Connection refused"
```bash
# Espera 30 segundos después de docker-compose up
# Los servicios tardan en iniciar
```

### Quiero ver logs
```bash
docker-compose logs -f api
docker-compose logs -f celery_worker
```

## 🎯 Próximos Pasos (después de que funcione)

1. **Optimiza costos**: Usa Gemini Flash para el 90% de tareas
2. **Tests**: Ejecuta `pytest tests/` para verificar todo
3. **Dashboard**: Levanta el dashboard Next.js en `/dashboard`
4. **Deploy**: Usa los manifests de Kubernetes en `/k8s`
5. **CI/CD**: Los GitHub Actions ya están configurados

## 📚 Documentación

- **Este archivo**: TODO.md
- **Setup Gemini**: SETUP_GEMINI.md (detalles técnicos)
- **Quick Start**: QUICKSTART_REAL.md
- **MVP Status**: MVP_STATUS.md
- **Architecture**: ARCHITECTURE.md

---

**🚀 ACCIÓN INMEDIATA:**
```bash
./setup_gemini.sh
```

¡Y ya está! 🎉
