# Route Planning Project

Proyecto de planificación de rutas con análisis de algoritmos de búsqueda, estructuras de datos espaciales (KD-Tree), y sistema de emergencias con partición de Voronoi.

## 📋 Descripción

Este proyecto implementa tres componentes principales para análisis y planificación de rutas sobre datos reales de OpenStreetMap:

### 🎯 Componente 1: Optimización con KD-Tree
- Construcción de árbol KD para búsqueda espacial eficiente
- Comparación de rendimiento: KD-Tree vs búsqueda exhaustiva
- Evaluación con 20 ubicaciones de prueba
- Reporte de tiempos de construcción y búsqueda

### 🚗 Componente 2: Planificador de Rutas
Evaluación de 5 algoritmos de búsqueda usando **SimpleAI**:
- BFS (Breadth-First Search)
- DFS (Depth-First Search)
- UCS (Uniform Cost Search)
- IDDFS (Iterative Deepening DFS)
- A* (A-Star con múltiples heurísticas)

**Evaluación en 3 rangos de distancia:**
- Corta: < 1000 metros (5 pares de nodos)
- Media: 1000-5000 metros (5 pares de nodos)
- Larga: > 5000 metros (5 pares de nodos)

### 🏥 Componente 3: Sistema de Emergencias
- Registro y localización de hospitales en el mapa
- Partición de Voronoi para determinar áreas de servicio
- Enrutamiento automático al hospital más cercano
- Visualización de regiones de influencia

## 🛠️ Tecnologías

### Backend
- **Python 3.8+**
- **Flask** - API REST
- **OSMnx** - Acceso a OpenStreetMap
- **SimpleAI** - Algoritmos de búsqueda
- **NetworkX** - Manejo de grafos
- **SciPy** - Cálculo de Voronoi
- **NumPy** - Operaciones numéricas
- **Matplotlib** - Visualizaciones

### Frontend
- **Vue 3** - Framework JavaScript
- **Vite** - Build tool
- **Tailwind CSS** - Estilos
- **Pinia** - State management
- **Vue Router** - Routing

## 📁 Estructura del Proyecto

```
route-planning/
├── backend/
│   ├── app/
│   │   ├── kdtree.py              # Implementación KD-Tree
│   │   ├── map_loader.py          # Carga de mapas OSM
│   │   ├── search_algorithms.py   # Algoritmos de búsqueda
│   │   ├── emergency_service.py   # Servicio de emergencias
│   │   ├── evaluation_kdtree.py   # Evaluación KD-Tree
│   │   └── evaluation_search.py   # Evaluación algoritmos
│   ├── app.py                      # API Flask
│   ├── run_evaluation.py           # Script de evaluaciones
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── router/
│   │   └── ...
│   ├── package.json
│   └── ...
└── README.md
```

## 🚀 Instalación y Uso

### Backend

1. **Crear entorno virtual:**
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Ejecutar evaluaciones completas:**
```bash
python run_evaluation.py
```

**⚠️ Importante:** Edita `run_evaluation.py` antes de ejecutar para:
- Cambiar la dirección o ciudad del mapa
- Especificar coordenadas de hospitales en tu área
- Ajustar número de evaluaciones

4. **Ejecutar servidor API (opcional):**
```bash
python app.py
```
API disponible en: `http://localhost:5000`

### Frontend

1. **Instalar dependencias:**
```bash
cd frontend
npm install
```

2. **Ejecutar servidor de desarrollo:**
```bash
npm run dev
```
Aplicación disponible en: `http://localhost:5173`

## 📊 Resultados de Evaluación

Después de ejecutar `run_evaluation.py`, se generan:

1. **`kdtree_evaluation.json`** - Resultados de evaluación del KD-Tree
2. **`search_evaluation.json`** - Comparación de algoritmos de búsqueda
3. **`voronoi_diagram.png`** - Visualización de partición de Voronoi
4. **`emergency_config.json`** - Configuración del servicio de emergencias

## 📖 Documentación Completa

- Ver `backend/README.md` para documentación detallada de la API
- Ver ejemplos de uso en `run_evaluation.py`

## 📝 Requisitos del Proyecto

- [x] Uso de OSMnx para acceso a OpenStreetMap
- [x] Implementación de algoritmos de búsqueda con SimpleAI
- [x] Evaluación completa del árbol KD
- [x] Evaluación completa de algoritmos de búsqueda
- [x] Sistema de emergencias con Voronoi

---

**Desarrollado para el curso de Análisis y Diseño de Algoritmos**  
Tecnológico de Monterrey
