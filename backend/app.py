from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import sys

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.map_loader import MapLoader
from app.kdtree import KDTree
from app.search_algorithms import SearchAlgorithms
from app.emergency_service import EmergencyService
from app.evaluation_kdtree import KDTreeEvaluator
from app.evaluation_search import SearchAlgorithmsEvaluator

app = Flask(__name__)
CORS(app)

# Global instances
map_loader = None
kdtree = None
search_algorithms = None
emergency_service = None

# ============================================================================
# INITIALIZATION ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok", 
        "message": "Route Planning API is running",
        "map_loaded": map_loader is not None
    })

@app.route('/api/map/load', methods=['POST'])
def load_map():
    """
    Load map from address or place name
    Body: {
        "address": "Tec de Monterrey campus Guadalajara...",
        "dist": 10000,
        "network_type": "drive"
    }
    OR
    Body: {
        "place": "Guadalajara, Jalisco, Mexico",
        "network_type": "drive"
    }
    """
    global map_loader, kdtree, search_algorithms, emergency_service
    
    try:
        data = request.get_json()
        
        map_loader = MapLoader()
        
        if 'address' in data:
            address = data['address']
            dist = data.get('dist', 10000)
            network_type = data.get('network_type', 'drive')
            
            graph = map_loader.load_map_from_address(address, dist, network_type)
        elif 'place' in data:
            place = data['place']
            network_type = data.get('network_type', 'drive')
            
            graph = map_loader.load_map_from_place(place, network_type)
        else:
            return jsonify({"error": "Must provide 'address' or 'place'"}), 400
        
        # Initialize other components
        search_algorithms = SearchAlgorithms(graph, map_loader)
        emergency_service = EmergencyService(map_loader)
        
        stats = map_loader.get_graph_stats()
        
        return jsonify({
            "success": True,
            "message": "Map loaded successfully",
            "stats": stats
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/map/stats', methods=['GET'])
def get_map_stats():
    """Get map statistics"""
    if not map_loader:
        return jsonify({"error": "Map not loaded"}), 400
    
    return jsonify(map_loader.get_graph_stats())

# ============================================================================
# COMPONENT 1: KD-TREE ENDPOINTS
# ============================================================================

@app.route('/api/kdtree/build', methods=['POST'])
def build_kdtree():
    """Build KD-Tree from loaded map"""
    global kdtree
    
    if not map_loader:
        return jsonify({"error": "Map not loaded"}), 400
    
    try:
        coords, node_ids = map_loader.get_all_nodes_coords()
        kdtree = KDTree()
        construction_time = kdtree.build(coords, node_ids)
        
        return jsonify({
            "success": True,
            "construction_time": construction_time,
            "stats": kdtree.get_stats()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/kdtree/search', methods=['POST'])
def search_kdtree():
    """
    Search for nearest node using KD-Tree
    Body: {
        "lat": 20.xxx,
        "lon": -103.xxx
    }
    """
    if not map_loader or not kdtree:
        return jsonify({"error": "Map or KD-Tree not initialized"}), 400
    
    try:
        data = request.get_json()
        lat = data['lat']
        lon = data['lon']
        
        x, y = map_loader.latlon_to_xy(lat, lon)
        node_id, distance, search_time = kdtree.nearest_neighbor((x, y))
        
        node_latlon = map_loader.get_node_latlon(node_id)
        
        return jsonify({
            "success": True,
            "nearest_node": int(node_id),
            "node_lat": node_latlon[0],
            "node_lon": node_latlon[1],
            "distance": float(distance),
            "search_time": float(search_time)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/kdtree/evaluate', methods=['POST'])
def evaluate_kdtree():
    """
    Run full KD-Tree evaluation
    Body: {
        "num_locations": 20,
        "use_real_locations": true
    }
    """
    if not map_loader:
        return jsonify({"error": "Map not loaded"}), 400
    
    try:
        data = request.get_json() or {}
        num_locations = data.get('num_locations', 20)
        use_real = data.get('use_real_locations', True)
        
        evaluator = KDTreeEvaluator(map_loader)
        results = evaluator.run_full_evaluation(num_locations, use_real)
        
        # Save results
        evaluator.save_results(results, 'kdtree_evaluation.json')
        
        return jsonify({
            "success": True,
            "results": results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# COMPONENT 2: ROUTE PLANNING ENDPOINTS
# ============================================================================

@app.route('/api/route/plan', methods=['POST'])
def plan_route():
    """
    Plan route between two locations
    Body: {
        "start_lat": 20.xxx,
        "start_lon": -103.xxx,
        "goal_lat": 20.yyy,
        "goal_lon": -103.yyy,
        "algorithm": "astar"  // bfs, dfs, ucs, iddfs, astar
    }
    """
    if not map_loader or not search_algorithms:
        return jsonify({"error": "Map not initialized"}), 400
    
    try:
        data = request.get_json()
        
        # Get start and goal nodes
        if not kdtree:
            coords, node_ids = map_loader.get_all_nodes_coords()
            temp_kdtree = KDTree()
            temp_kdtree.build(coords, node_ids)
        else:
            temp_kdtree = kdtree
        
        start_x, start_y = map_loader.latlon_to_xy(data['start_lat'], data['start_lon'])
        goal_x, goal_y = map_loader.latlon_to_xy(data['goal_lat'], data['goal_lon'])
        
        start_node, _, _ = temp_kdtree.nearest_neighbor((start_x, start_y))
        goal_node, _, _ = temp_kdtree.nearest_neighbor((goal_x, goal_y))
        
        algorithm = data.get('algorithm', 'astar')
        
        # Run algorithm
        if algorithm == 'bfs':
            result = search_algorithms.solve_bfs(start_node, goal_node)
        elif algorithm == 'dfs':
            result = search_algorithms.solve_dfs(start_node, goal_node)
        elif algorithm == 'ucs':
            result = search_algorithms.solve_ucs(start_node, goal_node)
        elif algorithm == 'iddfs':
            result = search_algorithms.solve_iddfs(start_node, goal_node)
        else:
            result = search_algorithms.solve_astar(start_node, goal_node)
        
        # Add coordinates for path visualization
        if result.get('success') and 'path' in result:
            path_coords = []
            for node in result['path']:
                lat, lon = map_loader.get_node_latlon(node)
                path_coords.append({'lat': lat, 'lon': lon, 'node': int(node)})
            result['path_coords'] = path_coords
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/route/evaluate', methods=['POST'])
def evaluate_search_algorithms():
    """
    Run full search algorithms evaluation
    Body: {
        "num_pairs_per_range": 5
    }
    """
    if not map_loader:
        return jsonify({"error": "Map not loaded"}), 400
    
    try:
        data = request.get_json() or {}
        num_pairs = data.get('num_pairs_per_range', 5)
        
        evaluator = SearchAlgorithmsEvaluator(map_loader)
        results = evaluator.run_full_evaluation(num_pairs)
        
        # Save results
        evaluator.save_results(results, 'search_evaluation.json')
        
        return jsonify({
            "success": True,
            "results": results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# COMPONENT 3: EMERGENCY SERVICE ENDPOINTS
# ============================================================================

@app.route('/api/emergency/register-hospitals', methods=['POST'])
def register_hospitals():
    """
    Register hospital locations
    Body: {
        "hospitals": [
            {"lat": 20.xxx, "lon": -103.xxx},
            {"lat": 20.yyy, "lon": -103.yyy}
        ]
    }
    OR to search automatically:
    Body: {
        "search_distance": 10000
    }
    """
    if not map_loader or not emergency_service:
        return jsonify({"error": "Map not initialized"}), 400
    
    try:
        data = request.get_json() or {}
        
        if 'hospitals' in data:
            coords = [(h['lat'], h['lon']) for h in data['hospitals']]
            hospitals = emergency_service.find_and_register_hospitals(coords)
        else:
            search_dist = data.get('search_distance', 10000)
            hospitals = emergency_service.find_and_register_hospitals(
                search_distance=search_dist
            )
        
        # Compute Voronoi
        emergency_service.compute_voronoi_partition()
        
        return jsonify({
            "success": True,
            "num_hospitals": len(hospitals),
            "hospitals": hospitals
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency/nearest-hospital', methods=['POST'])
def find_nearest_hospital():
    """
    Find nearest hospital to location
    Body: {
        "lat": 20.xxx,
        "lon": -103.xxx
    }
    """
    if not emergency_service or not emergency_service.hospitals:
        return jsonify({"error": "Emergency service not initialized"}), 400
    
    try:
        data = request.get_json()
        lat = data['lat']
        lon = data['lon']
        
        result = emergency_service.find_nearest_hospital(lat, lon)
        
        return jsonify({
            "success": True,
            "hospital": result['hospital'],
            "distance": result['distance']
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency/route', methods=['POST'])
def emergency_route():
    """
    Get route to nearest hospital
    Body: {
        "lat": 20.xxx,
        "lon": -103.xxx,
        "algorithm": "astar"
    }
    """
    if not emergency_service or not emergency_service.hospitals:
        return jsonify({"error": "Emergency service not initialized"}), 400
    
    try:
        data = request.get_json()
        lat = data['lat']
        lon = data['lon']
        algorithm = data.get('algorithm', 'astar')
        
        result = emergency_service.get_route_to_nearest_hospital(lat, lon, algorithm)
        
        # Add coordinates for path visualization
        if result.get('success') and 'path' in result:
            path_coords = []
            for node in result['path']:
                node_lat, node_lon = map_loader.get_node_latlon(node)
                path_coords.append({'lat': node_lat, 'lon': node_lon, 'node': int(node)})
            result['path_coords'] = path_coords
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency/voronoi', methods=['GET'])
def get_voronoi_diagram():
    """Get Voronoi diagram visualization"""
    if not emergency_service or not emergency_service.voronoi:
        return jsonify({"error": "Voronoi not computed"}), 400
    
    try:
        # Generate visualization
        filename = 'voronoi_diagram.png'
        emergency_service.visualize_voronoi(filename)
        
        return send_file(filename, mimetype='image/png')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency/service-areas', methods=['GET'])
def get_service_areas():
    """Get hospital service areas information"""
    if not emergency_service or not emergency_service.hospitals:
        return jsonify({"error": "Emergency service not initialized"}), 400
    
    try:
        info = emergency_service.get_service_area_info()
        return jsonify(info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/api/node/info/<int:node_id>', methods=['GET'])
def get_node_info(node_id):
    """Get information about a specific node"""
    if not map_loader:
        return jsonify({"error": "Map not loaded"}), 400
    
    try:
        lat, lon = map_loader.get_node_latlon(node_id)
        x, y = map_loader.get_node_coords(node_id)
        successors = map_loader.get_successors(node_id)
        
        return jsonify({
            "node_id": node_id,
            "lat": lat,
            "lon": lon,
            "x": x,
            "y": y,
            "num_successors": len(successors),
            "successors": successors[:10]  # Limit to first 10
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("ROUTE PLANNING API SERVER")
    print("=" * 60)
    print("Starting Flask server on http://localhost:5000")
    print("API Documentation:")
    print("  - GET  /api/health - Health check")
    print("  - POST /api/map/load - Load map")
    print("  - POST /api/kdtree/build - Build KD-Tree")
    print("  - POST /api/kdtree/evaluate - Evaluate KD-Tree")
    print("  - POST /api/route/plan - Plan route")
    print("  - POST /api/route/evaluate - Evaluate algorithms")
    print("  - POST /api/emergency/register-hospitals - Register hospitals")
    print("  - POST /api/emergency/route - Emergency route")
    print("=" * 60)
    app.run(debug=True, port=5000)
