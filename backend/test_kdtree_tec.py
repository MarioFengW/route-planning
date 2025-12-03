"""
Test script to verify KD-tree is working correctly in the Tec de Monterrey area
"""
import sys
import os

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.map_loader import MapLoader
from app.kdtree import KDTree

def test_tec_area():
    print("=" * 60)
    print("Testing KD-Tree in Tec de Monterrey Area")
    print("=" * 60)
    
    # Load map
    print("\n1. Loading map...")
    map_loader = MapLoader()
    address = "Tec de Monterrey campus Guadalajara, Zapopan, Jalisco, Mexico"
    graph = map_loader.load_map_from_address(address, dist=2000, network_type='drive')
    
    stats = map_loader.get_graph_stats()
    print(f"   Map loaded: {stats['num_nodes']} nodes, {stats['num_edges']} edges")
    
    # Build KD-tree
    print("\n2. Building KD-Tree...")
    coords, node_ids = map_loader.get_all_nodes_coords()
    kdtree = KDTree()
    build_time = kdtree.build(coords, node_ids)
    print(f"   KD-Tree built in {build_time:.4f} seconds")
    
    # Test several points in the Tec area
    test_points = [
        (20.7339, -103.4587, "Tec de Monterrey Campus Center"),
        (20.7350, -103.4600, "Near Tec"),
        (20.7320, -103.4570, "South of Tec"),
        (20.7360, -103.4610, "North of Tec"),
    ]
    
    print("\n3. Testing nearest neighbor search...")
    print("-" * 60)
    
    for lat, lon, description in test_points:
        print(f"\nTest Point: {description}")
        print(f"  Coordinates: ({lat}, {lon})")
        
        # Convert to x, y
        x, y = map_loader.latlon_to_xy(lat, lon)
        print(f"  Converted to: ({x}, {y})")
        
        # Find nearest node
        node_id, distance, search_time = kdtree.nearest_neighbor((x, y))
        node_lat, node_lon = map_loader.get_node_latlon(node_id)
        
        print(f"  Nearest Node: {node_id}")
        print(f"  Node Location: ({node_lat}, {node_lon})")
        print(f"  Distance: {distance:.2f} meters")
        print(f"  Search Time: {search_time:.6f} seconds")
        
        if distance > 500:
            print(f"  ⚠️  WARNING: Distance is quite large!")
        else:
            print(f"  ✓ Node found successfully")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == '__main__':
    test_tec_area()
