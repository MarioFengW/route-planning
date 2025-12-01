# Route Planning Frontend

Frontend del proyecto de planificación de rutas construido con Vue 3, Vite y Tailwind CSS.

## 🚀 Características

- **Dashboard Interactivo** - Interfaz principal para acceder a los 3 componentes
- **Carga de Mapas** - Integración con API para cargar mapas de OpenStreetMap
- **KD-Tree Evaluation** - Visualización de resultados de búsqueda espacial
- **Route Planning** - Comparación de algoritmos de búsqueda
- **Emergency Service** - Sistema de enrutamiento a hospitales

## 🛠️ Tecnologías

- **Vue 3** - Framework JavaScript progresivo
- **Vite** - Build tool ultrarrápido
- **Tailwind CSS** - Framework de CSS utility-first
- **Pinia** - State management
- **Vue Router** - Routing de aplicación

## 📦 Instalación

```bash
npm install
```

## 🏃 Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## 🏗️ Build para Producción

```bash
npm run build
```

Los archivos optimizados se generarán en la carpeta `dist/`

## 📂 Estructura del Proyecto

```
frontend/
├── public/               # Archivos estáticos
├── src/
│   ├── assets/          # Imágenes, estilos globales
│   ├── components/      # Componentes Vue
│   │   ├── Dashboard.vue    # Componente principal
│   │   └── Home.vue         # Vista home
│   ├── composables/     # Composables de Vue
│   │   └── useApi.js        # API client
│   ├── router/          # Configuración de rutas
│   │   └── index.js
│   ├── App.vue          # Componente raíz
│   ├── main.js          # Punto de entrada
│   └── style.css        # Estilos Tailwind
├── index.html
├── package.json
├── tailwind.config.js   # Configuración Tailwind
├── vite.config.js       # Configuración Vite
└── postcss.config.js    # Configuración PostCSS
```

## 🎨 Componentes

### Dashboard.vue

Componente principal que incluye:
- **Estado de la API** - Indicador de conexión con el backend
- **Carga de Mapas** - Formulario para cargar mapas desde OSM
- **Tarjetas de Componentes** - Acceso a los 3 componentes principales
- **Estadísticas del Mapa** - Información sobre nodos y aristas cargadas

### useApi.js (Composable)

Proporciona métodos para comunicarse con la API:

```javascript
const api = useApi()

// Cargar mapa
await api.loadMap({
  address: "Guadalajara, Jalisco",
  dist: 10000,
  network_type: "drive"
})

// Evaluar KD-Tree
await api.evaluateKdTree(20, true)

// Planificar ruta
await api.planRoute(lat1, lon1, lat2, lon2, 'astar')

// Ruta de emergencia
await api.getEmergencyRoute(lat, lon, 'astar')
```

## 🔌 Conexión con Backend

La aplicación se conecta al backend Flask en `http://localhost:5000`

Asegúrate de que el backend esté corriendo antes de usar la aplicación:

```bash
cd ../backend
python app.py
```

## 🎯 Uso

1. **Iniciar Backend:**
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1  # Windows
   python app.py
   ```

2. **Iniciar Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Abrir en Navegador:**
   - Visita `http://localhost:5173`
   - Verifica que el indicador de API esté en verde (online)

4. **Cargar un Mapa:**
   - Ingresa una dirección o lugar
   - Ajusta la distancia y tipo de red
   - Click en "Load Map"

5. **Explorar Componentes:**
   - Click en las tarjetas de componentes para explorar cada funcionalidad
   - KD-Tree: Evaluación de búsqueda espacial
   - Route Planner: Comparación de algoritmos
   - Emergency: Rutas a hospitales

## 🔧 Configuración

### Cambiar URL del Backend

Edita `src/composables/useApi.js`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api'
```

### Personalizar Estilos

Edita `tailwind.config.js` para personalizar colores, fuentes, etc:

```javascript
export default {
  theme: {
    extend: {
      colors: {
        // Tus colores personalizados
      }
    }
  }
}
```

## 📝 Notas

- La aplicación requiere que el backend esté corriendo para funcionar
- El indicador de estado de la API se actualiza cada 30 segundos
- Los mapas se cachean en el backend para mejorar el rendimiento

## 🐛 Troubleshooting

### Error: API Offline

- Verifica que el backend esté corriendo en `http://localhost:5000`
- Revisa la consola del backend para errores
- Verifica que las dependencias de Python estén instaladas

### Error al cargar mapa

- Asegúrate de que la dirección sea válida
- Verifica tu conexión a internet (OSMnx descarga datos)
- Reduce el parámetro de distancia si es muy grande

### Estilos no se aplican

- Ejecuta `npm install` para instalar todas las dependencias
- Verifica que Tailwind esté configurado correctamente
- Limpia la caché con `npm run build`

## 📚 Recursos

- [Vue 3 Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)

## 👨‍💻 Desarrollo

Para agregar nuevas funcionalidades:

1. Crea nuevos componentes en `src/components/`
2. Agrega endpoints en `src/composables/useApi.js`
3. Actualiza el router si es necesario
4. Usa Tailwind CSS para estilos consistentes

---

**Proyecto de Algoritmos - Tec de Monterrey**
