"""
Emergency service module with Voronoi partitioning
Finds nearest hospital using Voronoi diagram
"""
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
from typing import List, Tuple, Dict, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import contextily as ctx
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
        coords, node_ids = self.map_loader.get_all_nodes_coords()
        self.kdtree = KDTree()
        self.kdtree.build(coords, node_ids)
        print(f"Built KD-tree with {len(node_ids)} nodes from current graph")
        print(f"Graph has {self.map_loader.graph.number_of_nodes()} nodes")
        print(f"Sample node IDs from graph: {list(self.map_loader.graph.nodes())[:5]}")
        
        assigned_nodes = set()
        
        if hospital_coords:
            print(f"Registering {len(hospital_coords)} hospital coordinates...")
            self.hospitals = []
            
            for i, (lat, lon) in enumerate(hospital_coords):
                x, y = self.map_loader.latlon_to_xy(lat, lon)
                
                nearest_node = None
                distance = 0
                
                k = 20
                neighbors = self.kdtree.k_nearest_neighbors((x, y), k)
                
                for node, dist in neighbors:
                    if node not in assigned_nodes and node in self.map_loader.graph:
                        nearest_node = node
                        distance = dist
                        break
                
                if nearest_node is None or nearest_node not in self.map_loader.graph:
                    print(f"  Warning: No available node found for Hospital {i+1}, skipping...")
                    continue
                
                assigned_nodes.add(nearest_node)
                
                hospital_data = {
                    'id': int(i),
                    'name': f'Hospital {i+1}',
                    'lat': float(lat) if not np.isnan(lat) else 0.0,
                    'lon': float(lon) if not np.isnan(lon) else 0.0,
                    'nearest_node': int(nearest_node),
                    'distance_to_node': float(distance) if not np.isnan(distance) else 0.0
                }
                
                self.hospitals.append(hospital_data)
                print(f"  {hospital_data['name']}: Node {nearest_node} (distance: {distance:.1f}m)")
        else:
            print(f"Searching for hospitals within {search_distance}m...")
            hospitals_features = self.map_loader.find_hospitals(search_distance)
            
            self.hospitals = []
            temp_hospital_data = []
            
            for i, feature in enumerate(hospitals_features[:10]):
                geom = feature.get('geometry')
                if geom:
                    if hasattr(geom, 'centroid'):
                        centroid = geom.centroid
                        lat, lon = centroid.y, centroid.x
                    else:
                        lat, lon = geom.y, geom.x
                    
                    tags = feature.get('tags', {})
                    name = None
                    
                    if 'name' in tags:
                        name = tags.get('name')
                    elif 'official_name' in tags:
                        name = tags.get('official_name')
                    elif 'alt_name' in tags:
                        name = tags.get('alt_name')
                    
                    if not name or (isinstance(name, float) and np.isnan(name)):
                        name = f'Hospital en ({lat:.4f}, {lon:.4f})'
                    
                    temp_hospital_data.append({
                        'index': i,
                        'name': str(name),
                        'lat': float(lat),
                        'lon': float(lon)
                    })
            
            for hospital_data in temp_hospital_data:
                x, y = self.map_loader.latlon_to_xy(hospital_data['lat'], hospital_data['lon'])
                
                print(f"\n  Processing: {hospital_data['name']}")
                print(f"    Location: ({hospital_data['lat']:.6f}, {hospital_data['lon']:.6f})")
                
                # Try to find an available node (not already assigned)
                nearest_node = None
                distance = 0
                
                # Get k nearest neighbors to find an available one
                k = 20  # Check up to 20 nearest nodes
                neighbors = self.kdtree.k_nearest_neighbors((x, y), k)
                
                found_available = False
                for idx, (node, dist) in enumerate(neighbors):
                    # Check if node is available (not assigned) and exists in graph
                    if node not in assigned_nodes and node in self.map_loader.graph:
                        nearest_node = node
                        distance = dist
                        if idx > 0:
                            print(f"    ⚠️  Nearest node was occupied, using alternative #{idx+1}")
                        print(f"    ✓ Assigned to node {nearest_node} (distance: {distance:.1f}m)")
                        found_available = True
                        break
                
                # CRITICAL: Verify node exists in current graph and is available
                if not found_available or nearest_node is None or nearest_node not in self.map_loader.graph:
                    print(f"    ❌ SKIPPING - No available node found in {self.map_loader.network_type} network!")
                    print(f"       All nearby nodes may be occupied or inaccessible")
                    continue
                
                # Assign this node (mark as used)
                assigned_nodes.add(nearest_node)
                
                # Convert numpy types to Python native types and handle NaN
                final_hospital_data = {
                    'id': int(hospital_data['index']),
                    'name': str(hospital_data['name']),
                    'lat': float(hospital_data['lat']) if not np.isnan(hospital_data['lat']) else 0.0,
                    'lon': float(hospital_data['lon']) if not np.isnan(hospital_data['lon']) else 0.0,
                    'nearest_node': int(nearest_node),
                    'distance_to_node': float(distance) if not np.isnan(distance) else 0.0
                }
                
                self.hospitals.append(final_hospital_data)
                print(f"    ✅ REGISTERED: {final_hospital_data['name']} → Node {nearest_node}")
        
        # No more shared nodes - each node has exactly one hospital
        print(f"\n{'='*60}")
        print(f"  ✓ All hospitals assigned to unique nodes")
        print(f"  Total nodes used: {len(assigned_nodes)}")
        print(f"{'='*60}\n")
        
        # Extract hospital nodes
        self.hospital_nodes = [h['nearest_node'] for h in self.hospitals]
        
        print(f"\n{'='*60}")
        if not self.hospitals:
            print(f"⚠️  WARNING: No hospitals could be registered in {self.map_loader.network_type} network")
            print(f"   This may be because:")
            print(f"   1. No hospitals found in the search area")
            print(f"   2. Hospitals are not accessible via {self.map_loader.network_type} network")
            print(f"   Try using 'all' network type or increase search distance")
            raise ValueError(f"No hospitals found within {search_distance}m that are accessible via {self.map_loader.network_type} network. Try 'all' network type or increase search distance.")
        
        print(f"✅ Successfully registered {len(self.hospitals)} hospitals in {self.map_loader.network_type} network")
        print(f"   Hospital nodes: {self.hospital_nodes}")
        print(f"{'='*60}\n")
        return self.hospitals
    
    def compute_voronoi_partition(self) -> Voronoi:
        """
        Compute Voronoi partition for hospitals
        
        Returns:
            Voronoi object (or None if less than 2 hospitals)
        """
        if not self.hospitals:
            raise ValueError("No hospitals registered. Call find_and_register_hospitals first.")
        
        if len(self.hospitals) < 2:
            print(f"Warning: Only {len(self.hospitals)} hospital(s) registered. Voronoi partitioning requires at least 2 hospitals.")
            print("Nearest hospital will be determined by direct distance calculation.")
            self.voronoi = None
            return None
        
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
        Find nearest hospital to a location using Voronoi diagram (regions of influence)
        
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
        
        # If we have a Voronoi diagram (2+ hospitals), use it to find the region
        if self.voronoi is not None:
            # Find which Voronoi region the point belongs to
            # This is done by finding the closest hospital point (Voronoi region generator)
            # This is O(n) but uses the concept of Voronoi regions of influence
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
            
            print(f"✓ Using Voronoi regions: Point ({lat:.6f}, {lon:.6f}) belongs to region {nearest_index} (Hospital: {nearest_hospital['name']})")
            
            return {
                'hospital': nearest_hospital,
                'hospital_index': nearest_index,
                'distance': float(min_distance),
                'method': 'voronoi'
            }
        else:
            # Single hospital case - no Voronoi diagram needed
            hospital = self.hospitals[0]
            h_x, h_y = self.map_loader.latlon_to_xy(hospital['lat'], hospital['lon'])
            h_point = np.array([h_x, h_y])
            distance = np.linalg.norm(query_point - h_point)
            
            print(f"✓ Single hospital mode: Using {hospital['name']}")
            
            return {
                'hospital': hospital,
                'hospital_index': 0,
                'distance': float(distance),
                'method': 'single'
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
        import networkx as nx
        
        # Find nearest hospital
        hospital_info = self.find_nearest_hospital(lat, lon)
        hospital = hospital_info['hospital']
        
        # Find nearest node to starting location IN THE CURRENT GRAPH
        x, y = self.map_loader.latlon_to_xy(lat, lon)
        
        # Ensure KD-tree is built with current graph nodes
        if not self.kdtree:
            coords, node_ids = self.map_loader.get_all_nodes_coords()
            self.kdtree = KDTree()
            self.kdtree.build(coords, node_ids)
            print(f"Built KD-tree with {len(node_ids)} nodes from current graph for emergency location")
        
        start_node, _, _ = self.kdtree.nearest_neighbor((x, y))
        
        # Verify start node is in graph
        if start_node not in self.map_loader.graph:
            print(f"Error: Start node {start_node} not in current graph")
            return {
                'algorithm': algorithm,
                'success': False,
                'error': f'Start location node {start_node} not found in current graph (network_type mismatch?)',
                'start_node': int(start_node),
                'nearest_hospital_id': 0,
                'distance_to_hospital': 0.0,
                'search_time': 0.0,
                'time': 0.0
            }
        
        goal_node = hospital['nearest_node']
        
        # Verify goal node is in graph
        if goal_node not in self.map_loader.graph:
            print(f"Error: Hospital node {goal_node} not in current graph")
            return {
                'algorithm': algorithm,
                'success': False,
                'error': f'Hospital node {goal_node} not found in current graph (network_type mismatch?)',
                'start_node': int(start_node),
                'nearest_hospital_id': int(goal_node),
                'distance_to_hospital': 0.0,
                'search_time': 0.0,
                'time': 0.0
            }
        
        # Check if nodes are in the same connected component
        # Convert to undirected for connectivity check
        G_undirected = self.map_loader.graph.to_undirected()
        
        # Check if path exists
        if not nx.has_path(G_undirected, start_node, goal_node):
            print(f"Warning: No path exists between node {start_node} and node {goal_node}")
            print(f"Graph may be disconnected. Attempting to find nodes in largest component...")
            
            # Get largest connected component
            largest_cc = max(nx.connected_components(G_undirected), key=len)
            print(f"Largest connected component has {len(largest_cc)} nodes")
            
            # Check if both nodes are in largest component
            start_in_cc = start_node in largest_cc
            goal_in_cc = goal_node in largest_cc
            
            if not start_in_cc or not goal_in_cc:
                # Try to find alternative nodes in the largest component
                if not start_in_cc:
                    print(f"Start node {start_node} not in largest component, finding alternative...")
                    # Find closest node in largest component
                    min_dist = float('inf')
                    alt_start = None
                    for node in largest_cc:
                        if node in self.map_loader.nodes_data:
                            node_lat, node_lon = self.map_loader.get_node_latlon(node)
                            dist = ((lat - node_lat)**2 + (lon - node_lon)**2)**0.5
                            if dist < min_dist:
                                min_dist = dist
                                alt_start = node
                    if alt_start:
                        print(f"Using alternative start node: {alt_start}")
                        start_node = alt_start
                
                if not goal_in_cc:
                    print(f"Hospital node {goal_node} not in largest component, finding alternative hospital...")
                    # Find alternative hospital in largest component
                    min_dist = float('inf')
                    alt_hospital = None
                    alt_hospital_data = None
                    
                    for h in self.hospitals:
                        h_node = h['nearest_node']
                        if h_node in largest_cc:
                            h_lat, h_lon = h['lat'], h['lon']
                            dist = ((lat - h_lat)**2 + (lon - h_lon)**2)**0.5
                            if dist < min_dist:
                                min_dist = dist
                                alt_hospital = h_node
                                alt_hospital_data = h
                    
                    if alt_hospital:
                        print(f"Using alternative hospital at node: {alt_hospital}")
                        goal_node = alt_hospital
                        hospital = alt_hospital_data
                    else:
                        return {
                            'algorithm': algorithm,
                            'success': False,
                            'error': 'No hospitals found in the connected component containing the start location',
                            'start_node': int(start_node),
                            'nearest_hospital_id': int(goal_node),
                            'distance_to_hospital': 0.0,
                            'search_time': 0.0,
                            'time': 0.0
                        }
                
                # Verify path exists now
                if not nx.has_path(G_undirected, start_node, goal_node):
                    return {
                        'algorithm': algorithm,
                        'success': False,
                        'error': 'No path found even after attempting to use largest connected component',
                        'start_node': int(start_node),
                        'nearest_hospital_id': int(goal_node),
                        'distance_to_hospital': 0.0,
                        'search_time': 0.0,
                        'time': 0.0
                    }
        
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
            result = self.search_algorithms.solve_astar(start_node, goal_node)
        
        # Check if route was found
        if not result.get('success'):
            print(f"Algorithm {algorithm} failed to find a route")
            return {
                'algorithm': algorithm,
                'success': False,
                'error': result.get('error', 'No route found by search algorithm'),
                'start_node': int(start_node),
                'nearest_hospital_id': int(goal_node),
                'distance_to_hospital': 0.0,
                'search_time': result.get('search_time', 0.0),
                'time': result.get('search_time', 0.0),
                'hospital': hospital,
                'start_location': {'lat': float(lat), 'lon': float(lon)}
            }
        
        # Add location and hospital information
        result['start_location'] = {'lat': float(lat), 'lon': float(lon)}
        result['start_node'] = int(start_node)
        result['hospital'] = hospital
        result['voronoi_region'] = hospital_info['hospital_index']
        result['selection_method'] = hospital_info.get('method', 'voronoi')
        
        # Add all hospitals information for Voronoi visualization
        result['all_hospitals'] = [
            {
                'id': h['id'],
                'name': h['name'],
                'lat': float(h['lat']),
                'lon': float(h['lon']),
                'nearest_node': int(h['nearest_node']),
                'is_selected': h['id'] == hospital['id']
            }
            for h in self.hospitals
        ]
        
        # Add Voronoi data if available
        if self.voronoi is not None:
            result['voronoi_available'] = True
            result['voronoi_points'] = [
                {'lat': float(h['lat']), 'lon': float(h['lon'])}
                for h in self.hospitals
            ]
        else:
            result['voronoi_available'] = False
        
        # Add frontend-expected fields
        result['nearest_hospital_id'] = int(goal_node)
        result['distance_to_hospital'] = float(result.get('cost', 0)) if result.get('success') else 0.0
        
        # Calculate travel time (assuming 50 km/h average speed in urban areas)
        if result.get('success') and result.get('cost'):
            # cost is in meters, convert to km and then to minutes
            distance_km = result['cost'] / 1000
            speed_kmh = 50
            travel_time_minutes = (distance_km / speed_kmh) * 60
            result['travel_time'] = float(travel_time_minutes)
        else:
            result['travel_time'] = 0.0
        
        # Rename 'search_time' to 'time' if needed for consistency
        if 'search_time' in result and 'time' not in result:
            result['time'] = result['search_time']
        
        return result
    
    def visualize_voronoi(self, filename: str = 'voronoi_diagram.png', 
                         show_map: bool = True):
        """
        Visualize Voronoi partition with satellite imagery background
        
        Args:
            filename: Output filename for the plot
            show_map: Whether to show map nodes as background
        """
        if not self.hospitals:
            raise ValueError("No hospitals registered. Cannot visualize Voronoi diagram.")
        
        if len(self.hospitals) < 2:
            # Special handling for single hospital - just show the hospital location
            print(f"Only {len(self.hospitals)} hospital. Creating simple visualization...")
            fig, ax = plt.subplots(figsize=(16, 14))
            
            # Get map bounds
            coords, _ = self.map_loader.get_all_nodes_coords()
            coords_array = np.array(coords)
            min_lon, max_lon = coords_array[:, 0].min(), coords_array[:, 0].max()
            min_lat, max_lat = coords_array[:, 1].min(), coords_array[:, 1].max()
            
            ax.set_xlim(min_lon, max_lon)
            ax.set_ylim(min_lat, max_lat)
            
            # Add satellite basemap
            try:
                print("Adding satellite imagery basemap...")
                ctx.add_basemap(
                    ax,
                    crs='EPSG:4326',
                    source=ctx.providers.Esri.WorldImagery,
                    attribution=False,
                    alpha=0.7,
                    zoom='auto'
                )
            except Exception as e:
                print(f"Warning: Could not add basemap: {e}")
            
            # Plot hospital
            h = self.hospitals[0]
            ax.plot(h['lon'], h['lat'], 'r*', 
                   markersize=40, markeredgewidth=3, markeredgecolor='white',
                   label='Hospital', zorder=1000)
            
            ax.annotate(h['name'], (h['lon'], h['lat']), 
                       xytext=(8, 8), textcoords='offset points',
                       fontsize=10, fontweight='bold',
                       color='white',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='red', 
                                edgecolor='white', linewidth=2, alpha=0.9),
                       zorder=1001)
            
            ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
            ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
            ax.set_title('Hospital Location\n(Voronoi requires at least 2 hospitals)', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.legend(loc='upper right', fontsize=11, framealpha=0.95)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"Hospital visualization saved to {filename}")
            return
        
        if not self.voronoi:
            self.compute_voronoi_partition()
        
        if not self.voronoi:
            raise ValueError("Failed to compute Voronoi partition.")
        
        print(f"Creating Voronoi visualization: {filename}")
        
        # Get coordinates in lat/lon (not converted)
        hospital_lons = [h['lon'] for h in self.hospitals]
        hospital_lats = [h['lat'] for h in self.hospitals]
        
        # Create figure with larger size for better detail
        fig, ax = plt.subplots(figsize=(16, 14))
        
        # Plot Voronoi diagram FIRST (in converted coordinates)
        voronoi_plot_2d(self.voronoi, ax=ax, show_vertices=False, 
                       line_colors='cyan', line_width=3, point_size=0)
        
        # Get the axis limits BEFORE adding basemap
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Convert axis limits back to lat/lon for basemap
        # The voronoi uses converted coordinates, we need original lat/lon bounds
        coords, _ = self.map_loader.get_all_nodes_coords()
        coords_array = np.array(coords)
        min_lon, max_lon = coords_array[:, 0].min(), coords_array[:, 0].max()
        min_lat, max_lat = coords_array[:, 1].min(), coords_array[:, 1].max()
        
        # Add satellite basemap using contextily
        # ESRI World Imagery (same as your frontend)
        try:
            print("Adding satellite imagery basemap...")
            ctx.add_basemap(
                ax,
                crs='EPSG:4326',  # WGS84 coordinate system (lat/lon)
                source=ctx.providers.Esri.WorldImagery,
                attribution=False,
                alpha=0.7,
                zoom='auto'
            )
        except Exception as e:
            print(f"Warning: Could not add basemap: {e}")
            print("Continuing without satellite background...")
        
        # Restore axis limits
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
        # Plot hospital points ON TOP with proper coordinates
        hospital_points = np.array([[self.map_loader.latlon_to_xy(h['lat'], h['lon'])[0],
                                    self.map_loader.latlon_to_xy(h['lat'], h['lon'])[1]] 
                                   for h in self.hospitals])
        
        ax.plot(hospital_points[:, 0], hospital_points[:, 1], 'r*', 
               markersize=30, markeredgewidth=2, markeredgecolor='white',
               label='Hospitals', zorder=1000)
        
        # Add hospital labels with high contrast
        for i, hospital in enumerate(self.hospitals):
            x, y = self.map_loader.latlon_to_xy(hospital['lat'], hospital['lon'])
            ax.annotate(hospital['name'], (x, y), 
                       xytext=(8, 8), textcoords='offset points',
                       fontsize=7, fontweight='bold',
                       color='white',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='red', 
                                edgecolor='white', linewidth=1.5, alpha=0.9),
                       zorder=1001,
                       arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
        
        ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
        ax.set_title('Voronoi Partition - Hospital Service Areas\n(Satellite Imagery Background)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', fontsize=11, framealpha=0.95, 
                 edgecolor='black', fancybox=True)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
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
        
        # Calculate region sizes and total area
        try:
            from scipy.spatial import ConvexHull
            import numpy as np
            
            region_sizes = []
            total_area = 0.0
            
            for region in self.voronoi.regions:
                if not region or -1 in region:
                    # Skip infinite or empty regions
                    continue
                
                # Get vertices of this region
                vertices = self.voronoi.vertices[region]
                
                if len(vertices) >= 3:
                    # Calculate area using the shoelace formula
                    try:
                        hull = ConvexHull(vertices)
                        area = hull.volume  # In 2D, volume is area
                        region_sizes.append(area)
                        total_area += area
                    except Exception:
                        # Skip regions that can't form a convex hull
                        continue
            
            if region_sizes:
                info['avg_region_size'] = sum(region_sizes) / len(region_sizes)
                info['total_area'] = total_area
                info['min_region_size'] = min(region_sizes)
                info['max_region_size'] = max(region_sizes)
            else:
                info['avg_region_size'] = None
                info['total_area'] = None
                
        except Exception as e:
            print(f"Warning: Could not calculate region areas: {e}")
            info['avg_region_size'] = None
            info['total_area'] = None
        
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
