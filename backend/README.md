# Route Planning Backend

Backend del proyecto de planificación de rutas utilizando OSMnx, SimpleAI y estructuras de datos avanzadas.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── map_loader.py          # Carga y procesamiento de mapas OSM
│   ├── kdtree.py              # Implementación de KD-Tree
│   ├── search_algorithms.py   # Algoritmos de búsqueda (BFS, DFS, UCS, IDDFS, A*)
│   ├── emergency_service.py   # Servicio de emergencias con Voronoi
│   ├── evaluation_kdtree.py   # Evaluación de KD-Tree
│   └── evaluation_search.py   # Evaluación de algoritmos de búsqueda
├── app.py                      # API Flask
├── run_evaluation.py           # Script para ejecutar evaluaciones
├── requirements.txt            # Dependencias
└── cache/                      # Cache de grafos descargados

## Componentes Implementados

### Componente 1: KD-Tree
- Construcción eficiente de árbol KD para búsqueda espacial
- Búsqueda del vecino más cercano optimizada
- Comparación con búsqueda exhaustiva
- Evaluación de tiempos de construcción y búsqueda

### Componente 2: Planificador de Rutas
Algoritmos implementados usando **SimpleAI**:
- **BFS** (Breadth-First Search)
- **DFS** (Depth-First Search)
- **UCS** (Uniform Cost Search)
- **IDDFS** (Iterative Deepening DFS)
- **A*** (A-Star con heurísticas: Haversine, Euclidiana, Manhattan)

Evaluación en 3 rangos de distancia:
- Corta distancia: < 1000 metros
- Media distancia: 1000-5000 metros
- Larga distancia: > 5000 metros

### Componente 3: Sistema de Emergencias
- Registro de hospitales en el mapa
- Partición de Voronoi para áreas de servicio
- Enrutamiento automático al hospital más cercano
- Visualización de regiones de influencia

## Instalación

1. Crear y activar entorno virtual:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# o
source venv/bin/activate      # Linux/Mac
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar API Flask

```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`

### Ejecutar Evaluaciones Completas

```bash
python run_evaluation.py
```

Este script ejecutará:
1. Carga del mapa desde OpenStreetMap
2. Evaluación completa del KD-Tree (20 ubicaciones)
3. Evaluación de algoritmos de búsqueda (5 pares por rango)
4. Configuración del sistema de emergencias con Voronoi

**Nota:** Edita `run_evaluation.py` para cambiar:
- La dirección o lugar del mapa
- Las coordenadas de los hospitales
- El número de evaluaciones

### Resultados Generados

Después de ejecutar `run_evaluation.py`, se generan:
- `kdtree_evaluation.json` - Resultados de evaluación del KD-Tree
- `search_evaluation.json` - Comparación de algoritmos de búsqueda
- `voronoi_diagram.png` - Visualización de partición de Voronoi
- `emergency_config.json` - Configuración del servicio de emergencias

## API Endpoints

### Inicialización

**POST** `/api/map/load`
```json
{
  "address": "Tec de Monterrey campus Guadalajara, Zapopan, Jalisco, México",
  "dist": 10000,
  "network_type": "drive"
}
```

**GET** `/api/health` - Estado del servidor

**GET** `/api/map/stats` - Estadísticas del mapa cargado

### KD-Tree (Componente 1)

**POST** `/api/kdtree/build` - Construir KD-Tree

**POST** `/api/kdtree/search`
```json
{
  "lat": 20.6597,
  "lon": -103.3494
}
```

**POST** `/api/kdtree/evaluate`
```json
{
  "num_locations": 20,
  "use_real_locations": true
}
```

### Planificación de Rutas (Componente 2)

**POST** `/api/route/plan`
```json
{
  "start_lat": 20.6597,
  "start_lon": -103.3494,
  "goal_lat": 20.7000,
  "goal_lon": -103.3800,
  "algorithm": "astar"
}
```

**POST** `/api/route/evaluate`
```json
{
  "num_pairs_per_range": 5
}
```

### Sistema de Emergencias (Componente 3)

**POST** `/api/emergency/register-hospitals`
```json
{
  "hospitals": [
    {"lat": 20.6597, "lon": -103.3494},
    {"lat": 20.7000, "lon": -103.3800}
  ]
}
```

**POST** `/api/emergency/route`
```json
{
  "lat": 20.6700,
  "lon": -103.3500,
  "algorithm": "astar"
}
```

**POST** `/api/emergency/nearest-hospital`
```json
{
  "lat": 20.6700,
  "lon": -103.3500
}
```

**GET** `/api/emergency/voronoi` - Obtener diagrama de Voronoi (imagen)

**GET** `/api/emergency/service-areas` - Información de áreas de servicio

## Tecnologías Utilizadas

- **OSMnx** - Acceso a datos de OpenStreetMap
- **SimpleAI** - Implementación de algoritmos de búsqueda
- **NetworkX** - Manejo de grafos
- **SciPy** - Cálculo de Voronoi
- **GeoPy** - Cálculos geoespaciales
- **NumPy** - Operaciones numéricas
- **Matplotlib** - Visualizaciones
- **Flask** - API REST

## Notas Importantes

1. **Cache de Mapas**: Los mapas descargados se cachean en la carpeta `cache/` para evitar descargas repetidas.

2. **Coordenadas de Hospitales**: Para mejores resultados, proporciona coordenadas reales de hospitales en tu área de interés en lugar de usar búsqueda automática.

3. **Tamaño del Mapa**: Mapas muy grandes pueden tomar tiempo en cargar y procesar. Ajusta el parámetro `dist` según tus necesidades.

4. **Algoritmos**: A* con heurística Haversine generalmente ofrece el mejor balance entre velocidad y optimalidad.

## Troubleshooting

### Error al cargar mapa
- Verifica la conexión a internet
- Asegúrate de que la dirección o lugar existe en OpenStreetMap
- Reduce el parámetro `dist` si el área es muy grande

### Error con SimpleAI
- Verifica que SimpleAI esté instalado correctamente: `pip install simpleai`

### Error con Voronoi
- Asegúrate de tener al menos 4 hospitales registrados
- Verifica que las coordenadas estén dentro del área del mapa

## Autor

Proyecto desarrollado para el curso de Algoritmos - Tec de Monterrey
