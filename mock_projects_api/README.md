# Mock API de Proyectos JIC

API pequena en FastAPI para probar la integracion de `JIC_PROJECTS_API_URL`.

## Endpoints

- `GET /health`
- `GET /api/proyectos-jic`

El endpoint principal responde este esquema:

```json
{
  "total": 10,
  "ganadores_historicos": [
    {
      "id": 1,
      "titulo": "...",
      "ano": "2023",
      "universidad": "...",
      "siglas": "UTP",
      "resumen": "...",
      "categoria": "...",
      "premio": "Primer Lugar",
      "asesor": "...",
      "email": "...",
      "institucion": "...",
      "activo": 1
    }
  ]
}
```

## Ejecucion local

Desde la raiz del repo:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r .\mock_projects_api\requirements.txt
uvicorn mock_projects_api.app:app --host 0.0.0.0 --port 8001 --reload
```

Probar respuesta:

```powershell
curl http://127.0.0.1:8001/api/proyectos-jic
```

## Conectar con Django

Configura la variable de entorno antes de levantar tu app Django:

```powershell
$env:JIC_PROJECTS_API_URL="http://127.0.0.1:8001/api/proyectos-jic"
$env:JIC_PROJECTS_API_TIMEOUT="3"
$env:JIC_PROJECTS_CACHE_TTL="30"
```

Con eso, las partes del proyecto que consumen proyectos historicos usaran el mock.

## Contenedor Docker (base de jicweb_app)

El servicio `jic_projects_mock_api` reutiliza el mismo `Dockerfile` de `jicweb_app` para mantener una base consistente.

Levantar solo el mock:

```powershell
docker compose up -d jic_projects_mock_api
```

Ver logs:

```powershell
docker compose logs -f jic_projects_mock_api
```

Probar endpoint desde host:

```powershell
curl http://127.0.0.1:8001/api/proyectos-jic
```

Para que `jicweb_app` use el mock dentro de la red de Docker, define:

```powershell
$env:JIC_PROJECTS_API_URL="http://jic_projects_mock_api:8001/api/proyectos-jic"
```
