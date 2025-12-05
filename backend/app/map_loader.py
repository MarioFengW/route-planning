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
from shapely.geometry import Point


class MapLoader:
    """Loads and manages OpenStreetMap data using OSMnx"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.graph = None
        self.cache_dir = cache_dir
        self.nodes_data = {}
        self.edges_data = {}
        self.network_type = 'all'  # Track current network type
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def load_map_from_address(self, address: str, dist: int = 10000, 
                             network_type: str = 'all', 
                             use_cache: bool = True) -> nx.MultiDiGraph:
        """
        Load map from address using OSMnx
        
        Args:
            address: Address to center the map
            dist: Distance in meters from the address
            network_type: Type of network ('drive', 'walk', 'bike', 'all')
                         Default 'all' includes all types of roads including pedestrian paths
            use_cache: Whether to use cached graph if available
            
        Returns:
            NetworkX MultiDiGraph with the street network
        """
        cache_file = os.path.join(self.cache_dir, f"graph_{hash(address)}_{dist}_{network_type}.pkl")
        
        # Store network type
        self.network_type = network_type
        
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
    
    def load_map_from_place(self, place_name: str, network_type: str = 'all',
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
        cache_file = os.path.join(self.cache_dir, f"graph_{hash(place_name)}_{network_type}.pkl")
        
        # Store network type
        self.network_type = network_type
        
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
            )            # Add speed and travel time information
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
        Calculate distance between two nodes in meters using geopy with Haversine formula
        
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
            # Add timeout to prevent hanging
            import socket
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(10)  # 10 second timeout
            
            try:
                features = ox.features_from_point(point, tags=tags, dist=dist)
            finally:
                socket.setdefaulttimeout(old_timeout)
            
            if features.empty:
                return []
            
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
            # Silently fail - this is expected when no features are found
            return []
    
    def find_hospitals(self, dist: int = 5000) -> List[Dict]:
        """
        Find hospitals within the loaded map area only
        
        Args:
            dist: Maximum distance from center (will be capped to map bounds)
            
        Returns:
            List of hospital data within the loaded map area
        """
        if not self.graph:
            return []
        
        # Get all nodes to determine the actual map bounds
        nodes = list(self.graph.nodes())
        if not nodes:
            return []
        
        # Calculate the actual bounds of the loaded map
        all_lats = [self.nodes_data[node]['lat'] for node in nodes if node in self.nodes_data]
        all_lons = [self.nodes_data[node]['lon'] for node in nodes if node in self.nodes_data]
        
        if not all_lats or not all_lons:
            return []
        
        min_lat, max_lat = min(all_lats), max(all_lats)
        min_lon, max_lon = min(all_lons), max(all_lons)
        
        # Calculate the center and actual radius of the loaded map
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        
        # Calculate the maximum distance from center to corners of the bounding box
        import geopy.distance
        corner_distances = [
            geopy.distance.distance((center_lat, center_lon), (min_lat, min_lon)).m,
            geopy.distance.distance((center_lat, center_lon), (min_lat, max_lon)).m,
            geopy.distance.distance((center_lat, center_lon), (max_lat, min_lon)).m,
            geopy.distance.distance((center_lat, center_lon), (max_lat, max_lon)).m
        ]
        max_radius = max(corner_distances)
        
        # Use the smaller of the provided distance or the actual map radius
        search_dist = min(dist, max_radius)
        
        print(f"Map bounds: lat [{min_lat:.6f}, {max_lat:.6f}], lon [{min_lon:.6f}, {max_lon:.6f}]")
        print(f"Map center: ({center_lat:.6f}, {center_lon:.6f})")
        print(f"Map radius: {max_radius:.0f}m, requested: {dist}m, using: {search_dist:.0f}m")
        
        # Search for hospitals with multiple tag combinations
        hospitals = []
        
        # Try different tag combinations (limit attempts to avoid hanging)
        tag_combinations = [
            {'amenity': 'hospital'},
            {'amenity': 'clinic'},
            {'healthcare': 'hospital'},
        ]
        
        for tags in tag_combinations:
            try:
                print(f"  Trying tags: {tags}")
                features = self.get_features_near_location(center_lat, center_lon, tags, search_dist)
                if features:
                    print(f"  Found {len(features)} features with tags {tags}")
                    hospitals.extend(features)
                    # If we found hospitals, we can stop searching
                    if len(hospitals) >= 3:
                        break
            except Exception as e:
                print(f"  No data for tags {tags}: {str(e)[:100]}")
                continue
        
        # Filter hospitals to only include those within the actual loaded map bounds
        filtered_hospitals = []
        for hospital in hospitals:
            geom = hospital.get('geometry')
            if geom:
                if hasattr(geom, 'centroid'):
                    h_lat, h_lon = geom.centroid.y, geom.centroid.x
                else:
                    h_lat, h_lon = geom.y, geom.x
                
                # Check if hospital is within map bounds
                if min_lat <= h_lat <= max_lat and min_lon <= h_lon <= max_lon:
                    filtered_hospitals.append(hospital)
                else:
                    tags = hospital.get('tags', {})
                    name = tags.get('name', 'Unknown')
                    print(f"  Filtered out hospital '{name}' at ({h_lat:.6f}, {h_lon:.6f}) - outside map bounds")
        
        # Remove duplicates based on location
        unique_hospitals = []
        seen_locations = set()
        for hospital in filtered_hospitals:
            geom = hospital.get('geometry')
            if geom:
                if hasattr(geom, 'centroid'):
                    loc = (round(geom.centroid.y, 6), round(geom.centroid.x, 6))
                else:
                    loc = (round(geom.y, 6), round(geom.x, 6))
                if loc not in seen_locations:
                    seen_locations.add(loc)
                    unique_hospitals.append(hospital)
        
        if not unique_hospitals:
            print("⚠️  No hospitals found in OpenStreetMap data within the loaded map area")
        else:
            print(f"✓ Found {len(unique_hospitals)} unique hospitals within map bounds")
        
        return unique_hospitals
    
    def get_graph_stats(self) -> Dict:
        """Get statistics about the loaded graph"""
        if not self.graph:
            return {}
        
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'is_directed': self.graph.is_directed(),
            'is_multigraph': self.graph.is_multigraph(),
            'network_type': self.network_type
        }
