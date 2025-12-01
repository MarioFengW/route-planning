"""
Emergency service module with Voronoi partitioning
Finds nearest hospital using Voronoi diagram
"""
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
from typing import List, Tuple, Dict, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from .map_loader import MapLoader
from .kdtree import KDTree
from .search_algorithms import SearchAlgorithms
import json


class EmergencyService:
    """Emergency service with hospital routing using Voronoi partitioning"""
    
    def __init__(self, map_loader: MapLoader):
        """
        Initialize emergency service
        
        Args:
            map_loader: MapLoader instance with loaded graph
        """
        self.map_loader = map_loader
        self.hospitals = []
        self.hospital_nodes = []
        self.voronoi = None
        self.kdtree = None
        self.search_algorithms = SearchAlgorithms(map_loader.graph, map_loader)
    
    def find_and_register_hospitals(self, hospital_coords: List[Tuple[float, float]] = None,
                                   search_distance: int = 10000) -> List[Dict]:
        """
        Find hospitals in the map or register provided coordinates
        
        Args:
            hospital_coords: Optional list of (lat, lon) coordinates for hospitals
            search_distance: Distance to search for hospitals if not provided
            
        Returns:
            List of hospital data
        """
        if hospital_coords:
            # Use provided coordinates
            print(f"Registering {len(hospital_coords)} hospital coordinates...")
            self.hospitals = []
            
            for i, (lat, lon) in enumerate(hospital_coords):
                # Find nearest node to this coordinate
                x, y = self.map_loader.latlon_to_xy(lat, lon)
                
                # Build KD-tree if not exists
                if not self.kdtree:
                    coords, node_ids = self.map_loader.get_all_nodes_coords()
                    self.kdtree = KDTree()
                    self.kdtree.build(coords, node_ids)
                
                nearest_node, distance, _ = self.kdtree.nearest_neighbor((x, y))
                
                hospital_data = {
                    'id': i,
                    'name': f'Hospital {i+1}',
                    'lat': lat,
                    'lon': lon,
                    'nearest_node': int(nearest_node),
                    'distance_to_node': float(distance)
                }
                
                self.hospitals.append(hospital_data)
                print(f"  {hospital_data['name']}: Node {nearest_node}")
        else:
            # Search for hospitals using OSMnx
            print(f"Searching for hospitals within {search_distance}m...")
            hospitals_features = self.map_loader.find_hospitals(search_distance)
            
            self.hospitals = []
            for i, feature in enumerate(hospitals_features[:10]):  # Limit to 10
                # Get centroid of hospital geometry
                geom = feature.get('geometry')
                if geom:
                    if hasattr(geom, 'centroid'):
                        centroid = geom.centroid
                        lat, lon = centroid.y, centroid.x
                    else:
                        # If it's a point
                        lat, lon = geom.y, geom.x
                    
                    # Find nearest node
                    x, y = self.map_loader.latlon_to_xy(lat, lon)
                    
                    if not self.kdtree:
                        coords, node_ids = self.map_loader.get_all_nodes_coords()
                        self.kdtree = KDTree()
                        self.kdtree.build(coords, node_ids)
                    
                    nearest_node, distance, _ = self.kdtree.nearest_neighbor((x, y))
                    
                    hospital_data = {
                        'id': i,
                        'name': feature['tags'].get('name', f'Hospital {i+1}'),
                        'lat': lat,
                        'lon': lon,
                        'nearest_node': int(nearest_node),
                        'distance_to_node': float(distance)
                    }
                    
                    self.hospitals.append(hospital_data)
        
        # Extract hospital nodes
        self.hospital_nodes = [h['nearest_node'] for h in self.hospitals]
        
        print(f"\nRegistered {len(self.hospitals)} hospitals")
        return self.hospitals
    
    def compute_voronoi_partition(self) -> Voronoi:
        """
        Compute Voronoi partition for hospitals
        
        Returns:
            Voronoi object
        """
        if not self.hospitals:
            raise ValueError("No hospitals registered. Call find_and_register_hospitals first.")
        
        print("Computing Voronoi partition...")
        
        # Get hospital coordinates in x, y
        hospital_points = []
        for hospital in self.hospitals:
            x, y = self.map_loader.latlon_to_xy(hospital['lat'], hospital['lon'])
            hospital_points.append([x, y])
        
        # Compute Voronoi diagram
        self.voronoi = Voronoi(np.array(hospital_points))
        
        print(f"Voronoi partition computed with {len(self.voronoi.regions)} regions")
        
        return self.voronoi
    
    def find_nearest_hospital(self, lat: float, lon: float) -> Dict:
        """
        Find nearest hospital to a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with nearest hospital information
        """
        if not self.hospitals:
            raise ValueError("No hospitals registered.")
        
        # Convert to x, y
        x, y = self.map_loader.latlon_to_xy(lat, lon)
        query_point = np.array([x, y])
        
        # Find which Voronoi region the point belongs to
        # Simple approach: find closest hospital point
        min_distance = float('inf')
        nearest_hospital = None
        nearest_index = -1
        
        for i, hospital in enumerate(self.hospitals):
            h_x, h_y = self.map_loader.latlon_to_xy(hospital['lat'], hospital['lon'])
            h_point = np.array([h_x, h_y])
            distance = np.linalg.norm(query_point - h_point)
            
            if distance < min_distance:
                min_distance = distance
                nearest_hospital = hospital
                nearest_index = i
        
        return {
            'hospital': nearest_hospital,
            'hospital_index': nearest_index,
            'distance': float(min_distance)
        }
    
    def get_route_to_nearest_hospital(self, lat: float, lon: float, 
                                     algorithm: str = 'astar') -> Dict:
        """
        Get route from location to nearest hospital
        
        Args:
            lat: Latitude of starting location
            lon: Longitude of starting location
            algorithm: Algorithm to use (bfs, dfs, ucs, iddfs, astar)
            
        Returns:
            Dictionary with route information
        """
        # Find nearest hospital
        hospital_info = self.find_nearest_hospital(lat, lon)
        hospital = hospital_info['hospital']
        
        # Find nearest node to starting location
        x, y = self.map_loader.latlon_to_xy(lat, lon)
        
        if not self.kdtree:
            coords, node_ids = self.map_loader.get_all_nodes_coords()
            self.kdtree = KDTree()
            self.kdtree.build(coords, node_ids)
        
        start_node, _, _ = self.kdtree.nearest_neighbor((x, y))
        goal_node = hospital['nearest_node']
        
        # Find route using specified algorithm
        print(f"Finding route from node {start_node} to hospital at node {goal_node} using {algorithm}...")
        
        if algorithm == 'bfs':
            result = self.search_algorithms.solve_bfs(start_node, goal_node)
        elif algorithm == 'dfs':
            result = self.search_algorithms.solve_dfs(start_node, goal_node)
        elif algorithm == 'ucs':
            result = self.search_algorithms.solve_ucs(start_node, goal_node)
        elif algorithm == 'iddfs':
            result = self.search_algorithms.solve_iddfs(start_node, goal_node)
        else:  # default to A*
            result = self.search_algorithms.solve_astar(start_node, goal_node, 'haversine')
        
        # Add location and hospital information
        result['start_location'] = {'lat': lat, 'lon': lon}
        result['start_node'] = int(start_node)
        result['hospital'] = hospital
        result['voronoi_region'] = hospital_info['hospital_index']
        
        return result
    
    def visualize_voronoi(self, filename: str = 'voronoi_diagram.png', 
                         show_map: bool = True):
        """
        Visualize Voronoi partition
        
        Args:
            filename: Output filename for the plot
            show_map: Whether to show map nodes as background
        """
        if not self.voronoi:
            self.compute_voronoi_partition()
        
        print(f"Creating Voronoi visualization: {filename}")
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot Voronoi diagram
        voronoi_plot_2d(self.voronoi, ax=ax, show_vertices=False, 
                       line_colors='blue', line_width=2, point_size=10)
        
        # Plot hospital points
        hospital_points = np.array([[self.map_loader.latlon_to_xy(h['lat'], h['lon'])[0],
                                    self.map_loader.latlon_to_xy(h['lat'], h['lon'])[1]] 
                                   for h in self.hospitals])
        
        ax.plot(hospital_points[:, 0], hospital_points[:, 1], 'r+', 
               markersize=20, markeredgewidth=3, label='Hospitals')
        
        # Add hospital labels
        for i, hospital in enumerate(self.hospitals):
            x, y = self.map_loader.latlon_to_xy(hospital['lat'], hospital['lon'])
            ax.annotate(hospital['name'], (x, y), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # Optionally show map nodes
        if show_map:
            coords, _ = self.map_loader.get_all_nodes_coords()
            coords_array = np.array(coords)
            ax.plot(coords_array[:, 0], coords_array[:, 1], 'k.', 
                   markersize=0.5, alpha=0.3, label='Map nodes')
        
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('Voronoi Partition - Hospital Service Areas')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Voronoi diagram saved to {filename}")
    
    def get_service_area_info(self) -> Dict:
        """
        Get information about hospital service areas
        
        Returns:
            Dictionary with service area statistics
        """
        if not self.voronoi:
            self.compute_voronoi_partition()
        
        info = {
            'num_hospitals': len(self.hospitals),
            'hospitals': self.hospitals,
            'num_regions': len(self.voronoi.regions),
            'num_vertices': len(self.voronoi.vertices)
        }
        
        return info
    
    def save_configuration(self, filename: str = 'emergency_config.json'):
        """
        Save emergency service configuration
        
        Args:
            filename: Output filename
        """
        config = {
            'hospitals': self.hospitals,
            'hospital_nodes': [int(n) for n in self.hospital_nodes]
        }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Emergency service configuration saved to {filename}")
    
    def load_configuration(self, filename: str = 'emergency_config.json'):
        """
        Load emergency service configuration
        
        Args:
            filename: Input filename
        """
        with open(filename, 'r') as f:
            config = json.load(f)
        
        self.hospitals = config['hospitals']
        self.hospital_nodes = config['hospital_nodes']
        
        print(f"Loaded {len(self.hospitals)} hospitals from {filename}")
        
        # Recompute Voronoi
        self.compute_voronoi_partition()
