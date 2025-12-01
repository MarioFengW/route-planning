"""
Map loader and processor using OSMnx
Handles loading, caching, and transforming OpenStreetMap data
"""
import osmnx as ox
import networkx as nx
import pickle
import os
from typing import Tuple, List, Dict, Optional
import geopy.distance
import numpy as np


class MapLoader:
    """Loads and manages OpenStreetMap data using OSMnx"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.graph = None
        self.cache_dir = cache_dir
        self.nodes_data = {}
        self.edges_data = {}
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def load_map_from_address(self, address: str, dist: int = 10000, 
                             network_type: str = 'drive', 
                             use_cache: bool = True) -> nx.MultiDiGraph:
        """
        Load map from address using OSMnx
        
        Args:
            address: Address to center the map
            dist: Distance in meters from the address
            network_type: Type of network ('drive', 'walk', 'bike', 'all')
            use_cache: Whether to use cached graph if available
            
        Returns:
            NetworkX MultiDiGraph with the street network
        """
        cache_file = os.path.join(self.cache_dir, f"graph_{hash(address)}_{dist}.pkl")
        
        # Try to load from cache
        if use_cache and os.path.exists(cache_file):
            print(f"Loading graph from cache: {cache_file}")
            with open(cache_file, 'rb') as f:
                self.graph = pickle.load(f)
        else:
            print(f"Downloading graph from OSMnx for address: {address}")
            self.graph = ox.graph_from_address(
                address, 
                dist=dist, 
                network_type=network_type
            )
            
            # Add speed and travel time information
            try:
                self.graph = ox.add_edge_speeds(self.graph)
                self.graph = ox.add_edge_travel_times(self.graph)
            except AttributeError:
                # Older version compatibility
                try:
                    self.graph = ox.speed.add_edge_speeds(self.graph)
                    self.graph = ox.speed.add_edge_travel_times(self.graph)
                except:
                    print("Warning: Could not add speed/travel time data")
            
            # Save to cache
            with open(cache_file, 'wb') as f:
                pickle.dump(self.graph, f)
            print(f"Graph saved to cache: {cache_file}")
        
        # Extract nodes and edges data for quick access
        self._extract_nodes_data()
        self._extract_edges_data()
        
        return self.graph
    
    def load_map_from_place(self, place_name: str, network_type: str = 'drive',
                           use_cache: bool = True) -> nx.MultiDiGraph:
        """
        Load map from place name using OSMnx
        
        Args:
            place_name: Name of the place (city, neighborhood, etc.)
            network_type: Type of network ('drive', 'walk', 'bike', 'all')
            use_cache: Whether to use cached graph if available
            
        Returns:
            NetworkX MultiDiGraph with the street network
        """
        cache_file = os.path.join(self.cache_dir, f"graph_{hash(place_name)}.pkl")
        
        # Try to load from cache
        if use_cache and os.path.exists(cache_file):
            print(f"Loading graph from cache: {cache_file}")
            with open(cache_file, 'rb') as f:
                self.graph = pickle.load(f)
        else:
            print(f"Downloading graph from OSMnx for place: {place_name}")
            self.graph = ox.graph_from_place(
                place_name,
                network_type=network_type
            )
            
            # Add speed and travel time information
            try:
                self.graph = ox.add_edge_speeds(self.graph)
                self.graph = ox.add_edge_travel_times(self.graph)
            except AttributeError:
                # Older version compatibility
                try:
                    self.graph = ox.speed.add_edge_speeds(self.graph)
                    self.graph = ox.speed.add_edge_travel_times(self.graph)
                except:
                    print("Warning: Could not add speed/travel time data")
            
            # Save to cache
            with open(cache_file, 'wb') as f:
                pickle.dump(self.graph, f)
            print(f"Graph saved to cache: {cache_file}")
        
        # Extract nodes and edges data
        self._extract_nodes_data()
        self._extract_edges_data()
        
        return self.graph
    
    def _extract_nodes_data(self):
        """Extract and store nodes data for quick access"""
        self.nodes_data = {}
        for node_id, data in self.graph.nodes(data=True):
            self.nodes_data[node_id] = {
                'lat': data['y'],
                'lon': data['x'],
                'x': data['x'],
                'y': data['y']
            }
    
    def _extract_edges_data(self):
        """Extract and store edges data for quick access"""
        self.edges_data = {}
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            edge_key = (u, v, key)
            self.edges_data[edge_key] = {
                'length': data.get('length', 0),
                'speed_kph': data.get('speed_kph', 50),
                'travel_time': data.get('travel_time', 0)
            }
    
    def get_all_nodes_coords(self) -> Tuple[List[Tuple[float, float]], List[int]]:
        """
        Get all node coordinates and IDs for KD-tree construction
        
        Returns:
            Tuple of (coordinates_list, node_ids_list)
        """
        coords = []
        node_ids = []
        
        for node_id, data in self.nodes_data.items():
            coords.append((data['x'], data['y']))
            node_ids.append(node_id)
        
        return coords, node_ids
    
    def latlon_to_xy(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        Convert latitude/longitude to graph's x/y coordinate system
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Tuple of (x, y) in graph coordinate system
        """
        # In OSMnx, x corresponds to longitude and y to latitude
        return lon, lat
    
    def xy_to_latlon(self, x: float, y: float) -> Tuple[float, float]:
        """
        Convert graph's x/y coordinates to latitude/longitude
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of (lat, lon)
        """
        # In OSMnx, x corresponds to longitude and y to latitude
        return y, x
    
    def get_node_coords(self, node_id: int) -> Tuple[float, float]:
        """
        Get coordinates of a node
        
        Args:
            node_id: Node ID
            
        Returns:
            Tuple of (x, y) coordinates
        """
        if node_id in self.nodes_data:
            data = self.nodes_data[node_id]
            return data['x'], data['y']
        return None
    
    def get_node_latlon(self, node_id: int) -> Tuple[float, float]:
        """
        Get latitude/longitude of a node
        
        Args:
            node_id: Node ID
            
        Returns:
            Tuple of (lat, lon)
        """
        if node_id in self.nodes_data:
            data = self.nodes_data[node_id]
            return data['lat'], data['lon']
        return None
    
    def calculate_distance(self, node1: int, node2: int) -> float:
        """
        Calculate distance between two nodes in meters
        
        Args:
            node1: First node ID
            node2: Second node ID
            
        Returns:
            Distance in meters
        """
        coord1 = self.get_node_latlon(node1)
        coord2 = self.get_node_latlon(node2)
        
        if coord1 and coord2:
            return geopy.distance.distance(coord1, coord2).m
        return float('inf')
    
    def get_successors(self, node_id: int) -> List[int]:
        """
        Get successor nodes (nodes reachable from this node)
        
        Args:
            node_id: Node ID
            
        Returns:
            List of successor node IDs
        """
        if self.graph and node_id in self.graph:
            return list(self.graph.successors(node_id))
        return []
    
    def get_edge_data(self, node1: int, node2: int) -> Optional[Dict]:
        """
        Get edge data between two nodes
        
        Args:
            node1: Source node ID
            node2: Destination node ID
            
        Returns:
            Dictionary with edge data or None
        """
        if self.graph and self.graph.has_edge(node1, node2):
            # Get the first edge (there might be multiple)
            edges = self.graph.get_edge_data(node1, node2)
            if edges:
                # Return the first edge data
                first_key = list(edges.keys())[0]
                return edges[first_key]
        return None
    
    def get_features_near_location(self, lat: float, lon: float, 
                                   tags: Dict, dist: int = 500) -> List[Dict]:
        """
        Get features (buildings, hospitals, etc.) near a location
        
        Args:
            lat: Latitude
            lon: Longitude
            tags: Dictionary of OSM tags to search for
            dist: Distance in meters
            
        Returns:
            List of features with their data
        """
        try:
            point = (lat, lon)
            features = ox.features_from_point(point, tags=tags, dist=dist)
            
            results = []
            for idx, feature in features.iterrows():
                feature_data = {
                    'osmid': idx,
                    'geometry': feature.get('geometry'),
                    'tags': {k: v for k, v in feature.items() if k != 'geometry'}
                }
                results.append(feature_data)
            
            return results
        except Exception as e:
            print(f"Error getting features: {e}")
            return []
    
    def find_hospitals(self, dist: int = 5000) -> List[Dict]:
        """
        Find hospitals in the loaded map area
        
        Args:
            dist: Distance to search from map center
            
        Returns:
            List of hospital data
        """
        if not self.graph:
            return []
        
        # Get center of the graph
        nodes = list(self.graph.nodes())
        if not nodes:
            return []
        
        center_node = nodes[len(nodes) // 2]
        center_lat, center_lon = self.get_node_latlon(center_node)
        
        # Search for hospitals
        tags = {'amenity': 'hospital'}
        hospitals = self.get_features_near_location(center_lat, center_lon, tags, dist)
        
        return hospitals
    
    def get_graph_stats(self) -> Dict:
        """Get statistics about the loaded graph"""
        if not self.graph:
            return {}
        
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'is_directed': self.graph.is_directed(),
            'is_multigraph': self.graph.is_multigraph()
        }
