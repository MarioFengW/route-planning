"""
Evaluation module for KD-Tree performance
Compares KD-Tree search vs exhaustive search
"""
import time
import random
from typing import List, Tuple, Dict
from .kdtree import KDTree, exhaustive_search
from .map_loader import MapLoader
import json


class KDTreeEvaluator:
    """Evaluates KD-Tree performance against exhaustive search"""
    
    def __init__(self, map_loader: MapLoader):
        """
        Initialize evaluator
        
        Args:
            map_loader: MapLoader instance with loaded graph
        """
        self.map_loader = map_loader
        self.kdtree = None
        self.points = []
        self.node_ids = []
        
    def build_kdtree(self) -> Dict:
        """
        Build KD-Tree from map nodes
        
        Returns:
            Dictionary with construction statistics
        """
        print("Building KD-Tree...")
        
        # Get all node coordinates
        self.points, self.node_ids = self.map_loader.get_all_nodes_coords()
        
        # Build KD-Tree
        self.kdtree = KDTree()
        construction_time = self.kdtree.build(self.points, self.node_ids)
        
        stats = self.kdtree.get_stats()
        stats['construction_time'] = construction_time
        
        print(f"KD-Tree built with {stats['nodes_count']} nodes in {construction_time:.6f} seconds")
        
        return stats
    
    def generate_test_locations(self, num_locations: int = 20) -> List[Tuple[float, float]]:
        """
        Generate random test locations within the map bounds
        
        Args:
            num_locations: Number of locations to generate
            
        Returns:
            List of (lat, lon) tuples
        """
        if not self.points:
            self.points, self.node_ids = self.map_loader.get_all_nodes_coords()
        
        # Get bounds of the map
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # Generate random locations
        locations = []
        for _ in range(num_locations):
            x = random.uniform(min_x, max_x)
            y = random.uniform(min_y, max_y)
            # Convert to lat/lon
            lat, lon = self.map_loader.xy_to_latlon(x, y)
            locations.append((lat, lon))
        
        return locations
    
    def select_real_locations(self, num_locations: int = 20) -> List[Tuple[float, float]]:
        """
        Select random real node locations from the map
        
        Args:
            num_locations: Number of locations to select
            
        Returns:
            List of (lat, lon) tuples
        """
        if not self.node_ids:
            self.points, self.node_ids = self.map_loader.get_all_nodes_coords()
        
        # Sample random nodes
        num_to_sample = min(num_locations, len(self.node_ids))
        sampled_ids = random.sample(self.node_ids, num_to_sample)
        
        locations = []
        for node_id in sampled_ids:
            lat, lon = self.map_loader.get_node_latlon(node_id)
            locations.append((lat, lon))
        
        return locations
    
    def evaluate_kdtree_search(self, locations: List[Tuple[float, float]]) -> List[Dict]:
        """
        Evaluate KD-Tree search performance
        
        Args:
            locations: List of (lat, lon) tuples to search
            
        Returns:
            List of search results
        """
        if not self.kdtree:
            print("KD-Tree not built. Building now...")
            self.build_kdtree()
        
        results = []
        
        for i, (lat, lon) in enumerate(locations):
            # Convert to x, y coordinates
            x, y = self.map_loader.latlon_to_xy(lat, lon)
            
            # Search using KD-Tree
            node_id, distance, search_time = self.kdtree.nearest_neighbor((x, y))
            
            results.append({
                'location_index': i,
                'query_lat': lat,
                'query_lon': lon,
                'nearest_node': int(node_id),
                'distance': float(distance),
                'search_time': float(search_time)
            })
        
        return results
    
    def evaluate_exhaustive_search(self, locations: List[Tuple[float, float]]) -> List[Dict]:
        """
        Evaluate exhaustive search performance
        
        Args:
            locations: List of (lat, lon) tuples to search
            
        Returns:
            List of search results
        """
        if not self.points:
            self.points, self.node_ids = self.map_loader.get_all_nodes_coords()
        
        results = []
        
        for i, (lat, lon) in enumerate(locations):
            # Convert to x, y coordinates
            x, y = self.map_loader.latlon_to_xy(lat, lon)
            
            # Search using exhaustive search
            node_id, distance, search_time = exhaustive_search(
                self.points, 
                self.node_ids, 
                (x, y)
            )
            
            results.append({
                'location_index': i,
                'query_lat': lat,
                'query_lon': lon,
                'nearest_node': int(node_id),
                'distance': float(distance),
                'search_time': float(search_time)
            })
        
        return results
    
    def compare_methods(self, locations: List[Tuple[float, float]]) -> Dict:
        """
        Compare KD-Tree vs exhaustive search
        
        Args:
            locations: List of (lat, lon) tuples to search
            
        Returns:
            Dictionary with comparison results
        """
        print(f"\nEvaluating {len(locations)} locations...")
        
        # Evaluate KD-Tree
        print("Running KD-Tree searches...")
        kdtree_results = self.evaluate_kdtree_search(locations)
        
        # Evaluate exhaustive search
        print("Running exhaustive searches...")
        exhaustive_results = self.evaluate_exhaustive_search(locations)
        
        # Calculate statistics
        kdtree_times = [r['search_time'] for r in kdtree_results]
        exhaustive_times = [r['search_time'] for r in exhaustive_results]
        
        kdtree_avg = sum(kdtree_times) / len(kdtree_times)
        exhaustive_avg = sum(exhaustive_times) / len(exhaustive_times)
        
        speedup = exhaustive_avg / kdtree_avg if kdtree_avg > 0 else 0
        
        comparison = {
            'num_locations': len(locations),
            'kdtree': {
                'results': kdtree_results,
                'avg_time': kdtree_avg,
                'min_time': min(kdtree_times),
                'max_time': max(kdtree_times),
                'total_time': sum(kdtree_times)
            },
            'exhaustive': {
                'results': exhaustive_results,
                'avg_time': exhaustive_avg,
                'min_time': min(exhaustive_times),
                'max_time': max(exhaustive_times),
                'total_time': sum(exhaustive_times)
            },
            'speedup': speedup,
            'speedup_percentage': (speedup - 1) * 100
        }
        
        print(f"\nResults:")
        print(f"  KD-Tree average time: {kdtree_avg*1000:.6f} ms")
        print(f"  Exhaustive average time: {exhaustive_avg*1000:.6f} ms")
        print(f"  Speedup: {speedup:.2f}x ({comparison['speedup_percentage']:.2f}% faster)")
        
        return comparison
    
    def run_full_evaluation(self, num_locations: int = 20, use_real_locations: bool = True) -> Dict:
        """
        Run complete evaluation of KD-Tree
        
        Args:
            num_locations: Number of test locations
            use_real_locations: Whether to use real node locations or random
            
        Returns:
            Dictionary with all evaluation results
        """
        print("=" * 60)
        print("KD-TREE EVALUATION")
        print("=" * 60)
        
        # Build KD-Tree
        build_stats = self.build_kdtree()
        
        # Generate test locations
        if use_real_locations:
            print(f"\nSelecting {num_locations} real node locations...")
            locations = self.select_real_locations(num_locations)
        else:
            print(f"\nGenerating {num_locations} random locations...")
            locations = self.generate_test_locations(num_locations)
        
        # Compare methods
        comparison = self.compare_methods(locations)
        
        # Combine results
        full_results = {
            'kdtree_construction': build_stats,
            'test_locations': [{'lat': lat, 'lon': lon} for lat, lon in locations],
            'comparison': comparison
        }
        
        return full_results
    
    def save_results(self, results: Dict, filename: str = 'kdtree_evaluation.json'):
        """
        Save evaluation results to JSON file
        
        Args:
            results: Results dictionary
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filename}")
