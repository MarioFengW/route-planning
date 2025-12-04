from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import sys
import numpy as np
from flask.json.provider import DefaultJSONProvider

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.map_loader import MapLoader
from app.kdtree import KDTree
from app.search_algorithms import SearchAlgorithms
from app.emergency_service import EmergencyService
from app.evaluation_kdtree import KDTreeEvaluator
from app.evaluation_search import SearchAlgorithmsEvaluator

# Custom JSON provider to handle numpy types
class NumpyJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

app = Flask(__name__)
app.json = NumpyJSONProvider(app)
CORS(app)

# Global instances
map_loader = None
kdtree = None
search_algorithms = None
emergency_service = None

# Helper function to convert numpy types
def convert_numpy_types(obj):
    """Recursively convert numpy types to native Python types"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

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
        dist = 10000  # Default search distance
        
        if 'address' in data:
            address = data['address']
            dist = data.get('dist', 10000)
            network_type = data.get('network_type', 'all')  # Changed default to 'all'
            
            graph = map_loader.load_map_from_address(address, dist, network_type)
        elif 'place' in data:
            place = data['place']
            dist = data.get('dist', 10000)
            network_type = data.get('network_type', 'all')  # Changed default to 'all'
            
            graph = map_loader.load_map_from_place(place, network_type)
        else:
            return jsonify({"error": "Must provide 'address' or 'place'"}), 400
        
        # Initialize other components
        search_algorithms = SearchAlgorithms(graph, map_loader)
        emergency_service = EmergencyService(map_loader)
        
        # Use the same distance as the map to ensure hospitals are within bounds
        # The find_and_register_hospitals method will further restrict to actual map bounds
        hospital_search_dist = dist
        
        # Automatically search and register hospitals within the loaded map area only
        print(f"\n{'='*60}")
        print(f"🏥 Searching for hospitals in loaded map...")
        print(f"Network Type: {network_type.upper()}")
        print(f"Search Distance: {hospital_search_dist} meters")
        print(f"{'='*60}\n")
        hospitals_found = 0
        try:
            hospitals = emergency_service.find_and_register_hospitals(search_distance=hospital_search_dist)
            if hospitals and len(hospitals) > 0:
                emergency_service.compute_voronoi_partition()
                hospitals_found = len(hospitals)
                print(f"Successfully registered {hospitals_found} hospitals within map bounds")
            else:
                print("⚠️  No hospitals found in the loaded map area")
                print(f"   You can manually register hospitals or increase the map distance")
        except Exception as e:
            print(f"⚠️  Warning: Could not auto-register hospitals: {str(e)}")
            print(f"   Emergency service will be available but without auto-detected hospitals")
            hospitals_found = 0
        
        stats = map_loader.get_graph_stats()
        stats['hospitals_registered'] = hospitals_found
        
        print(f"\n{'='*60}")
        print(f"✅ MAP LOADED SUCCESSFULLY")
        print(f"Network Type: {network_type.upper()}")
        print(f"Nodes: {stats['num_nodes']}")
        print(f"Edges: {stats['num_edges']}")
        print(f"Hospitals: {hospitals_found}")
        print(f"{'='*60}\n")
        
        return jsonify({
            "success": True,
            "message": f"Map loaded successfully with {hospitals_found} hospitals",
            "stats": stats,
            "hospitals_found": hospitals_found,
            "network_type": network_type
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/map/stats', methods=['GET'])
def get_map_stats():
    """Get map statistics"""
    if not map_loader:
        return jsonify({"error": "Map not loaded"}), 400
    
    return jsonify(map_loader.get_graph_stats())

@app.route('/api/map/graph', methods=['GET'])
def get_graph_data():
    """
    Get graph data for visualization
    Returns nodes and edges in a format suitable for frontend rendering
    """
    if not map_loader:
        return jsonify({"error": "Map not loaded"}), 400
    
    try:
        graph = map_loader.graph
        
        # Get bounding box for normalization
        nodes_data = []
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for node_id, data in graph.nodes(data=True):
            x, y = data['x'], data['y']
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            nodes_data.append({
                'id': str(node_id),
                'x': x,
                'y': y,
                'lat': data['y'],
                'lon': data['x']
            })
        
        # Sample edges if too many (for performance)
        edges_data = []
        max_edges = 2000
        edge_list = list(graph.edges(data=True))
        
        if len(edge_list) > max_edges:
            import random
            edge_list = random.sample(edge_list, max_edges)
        
        for source, target, data in edge_list:
            edges_data.append({
                'source': str(source),
                'target': str(target)
            })
        
        return jsonify({
            "nodes": nodes_data,
            "edges": edges_data,
            "bounds": {
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y
            },
            "total_nodes": len(nodes_data),
            "total_edges": len(edges_data),
            "sampled": len(edge_list) < graph.number_of_edges()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
            "build_time": construction_time,  # Changed from construction_time
            "construction_time": construction_time,  # Keep for backwards compatibility
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
        
        if node_id is None:
            return jsonify({
                "success": False,
                "error": "No nodes found in the map area. The location may be outside the loaded map bounds.",
                "search_time": float(search_time)
            }), 404
        
        node_latlon = map_loader.get_node_latlon(node_id)
        
        # Warn if distance is very large (> 500m)
        warning = None
        if distance > 500:
            warning = f"Nearest node is {distance:.0f}m away. Consider loading a map with more detail or checking if the location is within the map area."
        
        return jsonify({
            "success": True,
            "nearest_node": int(node_id),
            "node_lat": node_latlon[0],
            "node_lon": node_latlon[1],
            "distance": float(distance),
            "search_time": float(search_time),
            "warning": warning
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
        
        # Transform results to match frontend expectations
        comparison = results.get('comparison', {})
        kdtree_stats = comparison.get('kdtree', {})
        exhaustive_stats = comparison.get('exhaustive', {})
        
        # Combine detailed results
        detailed_results = []
        kdtree_results = kdtree_stats.get('results', [])
        exhaustive_results = exhaustive_stats.get('results', [])
        
        for i in range(len(kdtree_results)):
            if i < len(exhaustive_results):
                kd = kdtree_results[i]
                ex = exhaustive_results[i]
                detailed_results.append({
                    'query_location': [kd.get('query_lat'), kd.get('query_lon')],
                    'nearest_node': kd.get('nearest_node'),
                    'distance': kd.get('distance'),
                    'kdtree_time': kd.get('search_time'),
                    'exhaustive_time': ex.get('search_time'),
                    'speedup': ex.get('search_time', 0) / kd.get('search_time', 1) if kd.get('search_time', 0) > 0 else 0
                })
        
        transformed_results = {
            'build_time': results.get('kdtree_construction', {}).get('build_time', 0),
            'num_nodes': results.get('kdtree_construction', {}).get('num_nodes', 0),
            'kdtree_avg_time': kdtree_stats.get('avg_time', 0),
            'kdtree_min_time': kdtree_stats.get('min_time', 0),
            'kdtree_max_time': kdtree_stats.get('max_time', 0),
            'kdtree_total_time': kdtree_stats.get('total_time', 0),
            'exhaustive_avg_time': exhaustive_stats.get('avg_time', 0),
            'exhaustive_min_time': exhaustive_stats.get('min_time', 0),
            'exhaustive_max_time': exhaustive_stats.get('max_time', 0),
            'exhaustive_total_time': exhaustive_stats.get('total_time', 0),
            'speedup_factor': comparison.get('speedup', 0),
            'speedup_percentage': comparison.get('speedup_percentage', 0),
            'num_locations': comparison.get('num_locations', 0),
            'detailed_results': detailed_results
        }
        
        # Convert numpy types to native Python types
        transformed_results = convert_numpy_types(transformed_results)
        
        return jsonify(transformed_results)
    
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
                path_coords.append({'lat': float(lat), 'lon': float(lon), 'node': int(node)})
            result['path_coords'] = path_coords
        
        # Convert all numpy types to native Python types
        result = convert_numpy_types(result)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error in plan_route: {str(e)}")
        import traceback
        traceback.print_exc()
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
        raw_results = evaluator.run_full_evaluation(num_pairs)
        
        # Save raw results
        evaluator.save_results(raw_results, 'search_evaluation.json')
        
        # Transform results to match frontend expectations
        by_range = {}
        detailed_results = []
        
        # Map range labels to keys
        range_mapping = {
            "Short distance (< 1000m)": "short",
            "Medium distance (1000m - 5000m)": "medium",
            "Long distance (> 5000m)": "long"
        }
        
        for label, range_data in raw_results.get('evaluation_ranges', {}).items():
            range_key = range_mapping.get(label, label.lower().split()[0])
            
            # Transform statistics to frontend format
            if 'statistics' in range_data:
                by_range[range_key] = {}
                for algo, stats in range_data['statistics'].items():
                    by_range[range_key][algo.lower()] = {
                        'avg_time': stats.get('avg_time', 0),
                        'avg_path_length': stats.get('avg_path_length', 0),
                        'avg_distance': stats.get('avg_cost', 0),  # cost -> distance
                        'success_rate': stats.get('success_rate', 0)
                    }
            
            # Transform detailed results
            if 'results' in range_data:
                for algo, algo_results in range_data['results'].items():
                    for result in algo_results:
                        if result.get('success'):
                            detailed_results.append({
                                'distance_range': range_key,
                                'start_node': result.get('start_node'),
                                'goal_node': result.get('goal_node'),
                                'algorithm': algo.lower(),
                                'time': result.get('search_time', 0),
                                'path_length': result.get('path_length', 0),
                                'total_distance': result.get('cost', 0)
                            })
        
        # Determine best overall algorithm (lowest average time across all ranges)
        best_overall = None
        best_avg_time = float('inf')
        
        for algo in ['bfs', 'dfs', 'ucs', 'iddfs', 'astar']:
            total_time = 0
            count = 0
            for range_key in ['short', 'medium', 'long']:
                if range_key in by_range and algo in by_range[range_key]:
                    total_time += by_range[range_key][algo]['avg_time']
                    count += 1
            
            if count > 0:
                avg_time = total_time / count
                if avg_time < best_avg_time:
                    best_avg_time = avg_time
                    best_overall = algo
        
        transformed_results = {
            'by_range': by_range,
            'detailed_results': detailed_results,
            'best_overall_algorithm': best_overall or 'astar'
        }
        
        return jsonify(transformed_results)
    
    except Exception as e:
        print(f"Error in evaluate_search_algorithms: {str(e)}")
        import traceback
        traceback.print_exc()
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
    if not emergency_service:
        return jsonify({
            "success": False,
            "error": "Emergency service not initialized. Please load a map first."
        }), 400
    
    if not emergency_service.hospitals or len(emergency_service.hospitals) == 0:
        return jsonify({
            "success": False,
            "error": "No hospitals registered in the loaded map area. Try loading a larger map area or manually register hospitals."
        }), 400
    
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
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/emergency/voronoi', methods=['GET'])
def get_voronoi_diagram():
    """Get Voronoi diagram visualization"""
    if not emergency_service or not emergency_service.hospitals:
        return jsonify("No hospitals registered in the map area"), 400
    
    try:
        # Generate visualization (handles both voronoi and single hospital case)
        filename = 'voronoi_diagram.png'
        emergency_service.visualize_voronoi(filename)
        
        return send_file(filename, mimetype='image/png')
    
    except Exception as e:
        print(f"Error generating Voronoi diagram: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency/status', methods=['GET'])
def emergency_status():
    """Check if emergency service is available with hospitals"""
    if not emergency_service:
        return jsonify({
            "available": False,
            "hospitals_count": 0,
            "message": "Emergency service not initialized. Please load a map first."
        })
    
    hospitals_count = len(emergency_service.hospitals) if emergency_service.hospitals else 0
    
    return jsonify({
        "available": hospitals_count > 0,
        "hospitals_count": hospitals_count,
        "message": f"{hospitals_count} hospitals registered" if hospitals_count > 0 else "No hospitals in map area"
    })

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
    app.run(debug=True, port=5000, use_reloader=False)
