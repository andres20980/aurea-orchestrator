# 🚀 Aurea Orchestrator - Quick Start

## ⚡ Inicio Rápido (5 minutos)

### 1. Setup Automático

```bash
chmod +x setup_quick.sh
./setup_quick.sh
```

### 2. Configura tus API Keys

Edita `.env` y agrega tus claves:

```bash
ANTHROPIC_API_KEY=sk-ant-xxx-TU-CLAVE-AQUI
OPENAI_API_KEY=sk-xxx-TU-CLAVE-AQUI
```

### 3. Inicia los servicios

**Terminal 1 - API Server:**
```bash
source venv/bin/activate
uvicorn aurea_orchestrator.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
source venv/bin/activate
celery -A aurea_orchestrator.celery_app worker --loglevel=info
```

### 4. Prueba el sistema

```bash
# Ver la documentación interactiva
open http://localhost:8000/docs

# O hacer una petición de prueba
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Create a Python function to calculate fibonacci numbers",
    "metadata": {"priority": "high"}
  }'
```

## 🧪 Ejecutar Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

## 📊 Monitoreo

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics (si tienes Prometheus)

## 🐳 Usar Docker (Todo incluido)

```bash
docker-compose up
```

Esto inicia:
- API (puerto 8000)
- Celery Worker
- Redis
- PostgreSQL

## 🛑 Detener servicios

```bash
# Detener Docker
docker-compose down

# O si usas services individuales
docker stop $(docker ps -q --filter "name=aurea")
```

## 🔧 Troubleshooting

### "No module named 'aurea_orchestrator'"
```bash
source venv/bin/activate
pip install -e .
```

### "Connection refused" a Redis/PostgreSQL
```bash
docker-compose ps  # Ver si están corriendo
docker-compose logs redis postgres  # Ver logs
```

### "Missing API keys"
```bash
# Verifica que .env tiene las keys
cat .env | grep API_KEY
```

## 📚 Arquitectura

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────┐
│  FastAPI    │────▶│  Celery  │
│   Server    │     │  Worker  │
└──────┬──────┘     └────┬─────┘
       │                 │
       ▼                 ▼
┌─────────────┐    ┌──────────┐
│ PostgreSQL  │    │  Redis   │
└─────────────┘    └──────────┘
```

### Flujo de Ejecución

1. **Submit Task** → API recibe task
2. **Queue** → Celery encola en Redis
3. **Process** → Worker ejecuta con LangGraph
4. **Agents** → 5 agentes trabajan secuencialmente
5. **Store** → Resultado en PostgreSQL
6. **Return** → Cliente recibe respuesta

## 🎯 Ejemplos de Uso

### Python Client

```python
import requests

response = requests.post(
    "http://localhost:8000/tasks/",
    json={
        "task_description": "Create a REST API for user management",
        "metadata": {
            "language": "python",
            "framework": "fastapi"
        }
    }
)

task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")

# Check status
status = requests.get(f"http://localhost:8000/tasks/{task_id}")
print(status.json())
```

### CLI Tool

```bash
# Instalar CLI
pip install -e .

# Usar aurea CLI
aurea request "Deploy a microservice to Kubernetes" --priority high
aurea status --all
```

## 🎓 Próximos Pasos

1. **Personalizar Agentes**: Edita `aurea_orchestrator/agents.py`
2. **Añadir Features**: Revisa los módulos en `src/`
3. **Deploy a K8s**: Usa los manifests en `k8s/`
4. **Monitoreo**: Configura Grafana con `prometheus.yml`

## 🐛 Reportar Issues

https://github.com/andres20980/aurea-orchestrator/issues
