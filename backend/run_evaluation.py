"""
Example script to run all evaluations
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.map_loader import MapLoader
from app.evaluation_kdtree import KDTreeEvaluator
from app.evaluation_search import SearchAlgorithmsEvaluator
from app.emergency_service import EmergencyService


def main():
    print("=" * 70)
    print("ROUTE PLANNING PROJECT - FULL EVALUATION")
    print("=" * 70)
    
    # ========================================================================
    # STEP 1: Load Map
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 1: LOADING MAP")
    print("=" * 70)
    
    map_loader = MapLoader()
    
    # Choose one of the following:
    # Option 1: Load by address
    address = 'Tec de Monterrey campus Guadalajara, Zapopan, Jalisco, 45201, México'
    graph = map_loader.load_map_from_address(address, dist=10000, network_type='drive')
    
    # Option 2: Load by place name
    # graph = map_loader.load_map_from_place('Guadalajara, Jalisco, Mexico', network_type='drive')
    
    stats = map_loader.get_graph_stats()
    print(f"\nMap loaded:")
    print(f"  Nodes: {stats['num_nodes']}")
    print(f"  Edges: {stats['num_edges']}")
    
    # ========================================================================
    # STEP 2: Evaluate KD-Tree (Component 1)
    # ========================================================================
    print("\n" + "=" * 70)
    print("COMPONENT 1: KD-TREE EVALUATION")
    print("=" * 70)
    
    kdtree_evaluator = KDTreeEvaluator(map_loader)
    kdtree_results = kdtree_evaluator.run_full_evaluation(num_locations=20, use_real_locations=True)
    
    print(f"\n✓ KD-Tree evaluation completed")
    print(f"  Results saved to: kdtree_evaluation.json")
    
    # ========================================================================
    # STEP 3: Evaluate Search Algorithms (Component 2)
    # ========================================================================
    print("\n" + "=" * 70)
    print("COMPONENT 2: SEARCH ALGORITHMS EVALUATION")
    print("=" * 70)
    
    search_evaluator = SearchAlgorithmsEvaluator(map_loader)
    search_results = search_evaluator.run_full_evaluation(num_pairs_per_range=5)
    
    print(f"\n✓ Search algorithms evaluation completed")
    print(f"  Results saved to: search_evaluation.json")
    
    # ========================================================================
    # STEP 4: Emergency Service with Voronoi (Component 3)
    # ========================================================================
    print("\n" + "=" * 70)
    print("COMPONENT 3: EMERGENCY SERVICE EVALUATION")
    print("=" * 70)
    
    emergency_service = EmergencyService(map_loader)
    
    # Option 1: Manually specify hospital locations (recommended)
    # Get some coordinates from your map area
    print("\nRegistering hospitals...")
    hospital_coords = [
        (20.6597, -103.3494),  # Example coordinates - replace with real ones
        (20.7000, -103.3800),
        (20.6800, -103.3200),
        (20.6400, -103.3600),
        (20.7200, -103.3400)
    ]
    
    # Option 2: Auto-search for hospitals (may not find any in small areas)
    # hospitals = emergency_service.find_and_register_hospitals(search_distance=10000)
    
    hospitals = emergency_service.find_and_register_hospitals(hospital_coords)
    
    print(f"\nRegistered {len(hospitals)} hospitals")
    for h in hospitals:
        print(f"  - {h['name']}: Node {h['nearest_node']}")
    
    # Compute Voronoi partition
    print("\nComputing Voronoi partition...")
    emergency_service.compute_voronoi_partition()
    
    # Visualize Voronoi
    print("Creating Voronoi visualization...")
    emergency_service.visualize_voronoi('voronoi_diagram.png', show_map=False)
    
    # Get service area info
    service_info = emergency_service.get_service_area_info()
    print(f"\nService area information:")
    print(f"  Number of hospitals: {service_info['num_hospitals']}")
    print(f"  Number of Voronoi regions: {service_info['num_regions']}")
    
    # Test emergency routing
    print("\nTesting emergency routing...")
    test_location = (20.6700, -103.3500)  # Replace with a location in your map
    
    try:
        emergency_result = emergency_service.get_route_to_nearest_hospital(
            test_location[0], test_location[1], algorithm='astar'
        )
        
        if emergency_result.get('success'):
            print(f"✓ Emergency route found")
            print(f"  Hospital: {emergency_result['hospital']['name']}")
            print(f"  Path length: {emergency_result['path_length']} nodes")
            print(f"  Distance: {emergency_result['cost']:.2f} meters")
            print(f"  Search time: {emergency_result['search_time']*1000:.3f} ms")
        else:
            print(f"✗ No route found")
    except Exception as e:
        print(f"✗ Error finding emergency route: {e}")
    
    # Save configuration
    emergency_service.save_configuration('emergency_config.json')
    print(f"\n✓ Emergency service configuration saved to: emergency_config.json")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("EVALUATION COMPLETED")
    print("=" * 70)
    print("\nGenerated files:")
    print("  1. kdtree_evaluation.json - KD-Tree performance results")
    print("  2. search_evaluation.json - Search algorithms comparison")
    print("  3. voronoi_diagram.png - Voronoi partition visualization")
    print("  4. emergency_config.json - Emergency service configuration")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
