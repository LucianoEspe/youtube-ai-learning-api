# YouTube AI Learning API

Una API desarrollada con FastAPI que utiliza inteligencia artificial para generar resúmenes y exámenes de autoevaluación a partir de videos de YouTube.
El proyecto originalmente fue creado para trabajar con la API de Vimeo, y los datos de transcripción eran almacenados en el backend (Odoo Framework).

## 🚀 Demo en vivo
<a href="https://youtube-ai-learning-api.onrender.com/docs#/" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/PROBAR_DEMO-AQU%C3%8D-10b981?style=for-the-badge" alt="Demo en vivo"></a>

*Nota: La demo pública utiliza mi token de OpenAI con límites de uso.*

## 🚀 Características

- **Extracción de transcripciones**: Obtiene automáticamente las transcripciones de videos de YouTube
- **Generación de resúmenes**: Crea resúmenes concisos del contenido audiovisual utilizando OpenAI
- **Exámenes de autoevaluación**: Genera preguntas y respuestas basadas en el contenido del video
- **API REST**: Endpoints documentados para integración con aplicaciones frontend
- **Interfaz interactiva**: Documentación automática con Swagger UI

## 🛠️ Tecnologías

- **FastAPI**: Framework web moderno y rápido para Python
- **OpenAI API**: Modelo GPT para generación de contenido (usando cliente asíncrono `AsyncOpenAI`)
- **YouTube Transcript3 (RapidAPI)**: Para acceso a transcripciones de videos vía <a href="https://rapidapi.com/solid-api-solid-api-default/api/youtube-transcript3" target="_blank" rel="noopener noreferrer">https://rapidapi.com/solid-api-solid-api-default/api/youtube-transcript3</a>
- **Redis**: Cache asíncrona de resultados usando `redis.asyncio`
- **httpx**: Cliente HTTP asíncrono para llamadas externas
- **uv**: Gestor de dependencias Python ultrarrápido
- **Pydantic**: Validación de datos y serialización

## 🔍 Flujo de procesamiento
```mermaid
  graph LR
      A[URL YouTube] --> B(Extraer ID)
      B --> C[Transcripción API]
      C --> D{OpenAI API (Async)}
      D --> E[Resumen del video]
      D --> F[Cuestionario de autoevaluación]
      E --> G[Formato JSON]
      F --> G
      G --> H[Respuesta API]
```

## 📋 Requisitos previos

- Python 3.11+
- Token de API de OpenAI
- Token de API de YouTube Transcript3 (RapidAPI)
- Redis instalado y corriendo localmente o en la nube
- uv instalado (<a href="https://docs.astral.sh/uv/getting-started/installation/" target="_blank" rel="noopener noreferrer">Guía de instalación</a>)

## 🔧 Instalación

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/youtube-ai-learning-api.git
   cd youtube-ai-learning-api
   ```

2. **Instala las dependencias con uv**
   ```bash
   uv sync
   ```

3. **Configura las variables de entorno**
   ```bash
   cp .env.example .env
   ```

4. **Edita el archivo .env y agrega tu token de OpenAI y RapidAPI:**
   ```env
   OPENAI_API_KEY=tu_token_openai
   RAPIDAPI_KEY=tu_token_rapidapi
   REDIS_URL=redis://localhost:6379
   ```

5. **Ejecuta la aplicación**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

La API estará disponible en <a href="http://localhost:8000" target="_blank" rel="noopener noreferrer">http://localhost:8000</a>

## 🧑‍💻 Notas técnicas

- Todo el backend es **asíncrono**: FastAPI, Redis, httpx y OpenAI usan await/async.
- El cliente de OpenAI es `AsyncOpenAI`.
- El cache usa `redis.asyncio`.
- Puedes limpiar la cache de Redis ejecutando:
  ```bash
  redis-cli FLUSHALL
  ```
  O desde Python:
  ```python
  import asyncio
  from app.services.redis_client import redis_client
  asyncio.run(redis_client.flushdb())
  ```

## 📖 Uso

Todos los endpoints son **GET** y requieren autenticación a través de la API Key en el encabezado `API-Key`.

### Ejemplo: Obtener un resumen

```http
GET /summary?youtube_url=https://www.youtube.com/watch?v=ZacjOVVgoLY&language=en
API-Key: tu_api_key_aqui
```

### Ejemplo: Obtener un cuestionario

```http
GET /quiz?youtube_url=https://www.youtube.com/watch?v=ZacjOVVgoLY&language=en&num_questions=5
API-Key: tu_api_key_aqui
```

**Documentación interactiva**  
Visita <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">http://localhost:8000/docs</a> para acceder a la documentación interactiva de Swagger UI.
