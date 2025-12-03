"""
KD-Tree implementation for efficient nearest neighbor search
Based on the spatial partitioning algorithm for k-dimensional points
"""
import numpy as np
from typing import List, Tuple, Optional
import time
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees) using Haversine formula
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in meters
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r


class KDNode:
    """Node in a KD-Tree"""
    def __init__(self, point, node_id, left=None, right=None, axis=0):
        self.point = np.array(point)  # [x, y] coordinates
        self.node_id = node_id  # OpenStreetMap node ID
        self.left = left
        self.right = right
        self.axis = axis  # splitting axis (0 for x, 1 for y)


class KDTree:
    """
    KD-Tree for 2D spatial indexing
    Optimizes nearest neighbor queries for geographic coordinates
    """
    
    def __init__(self):
        self.root = None
        self.k = 2  # 2D points (x, y)
        self.nodes_count = 0
        self.construction_time = 0
        
    def build(self, points: List[Tuple[float, float]], node_ids: List[int]) -> float:
        """
        Build KD-Tree from list of points
        
        Args:
            points: List of (x, y) coordinates
            node_ids: List of corresponding node IDs
            
        Returns:
            Construction time in seconds
        """
        start_time = time.time()
        
        # Convert to numpy array for efficient operations
        points_array = np.array(points)
        node_ids_array = np.array(node_ids)
        
        # Build tree recursively
        self.root = self._build_recursive(points_array, node_ids_array, depth=0)
        self.nodes_count = len(points)
        
        self.construction_time = time.time() - start_time
        return self.construction_time
    
    def _build_recursive(self, points: np.ndarray, node_ids: np.ndarray, depth: int) -> Optional[KDNode]:
        """
        Recursively build KD-Tree
        
        Args:
            points: Array of points to partition
            node_ids: Array of corresponding node IDs
            depth: Current depth in the tree
            
        Returns:
            Root node of subtree
        """
        if len(points) == 0:
            return None
        
        # Select axis based on depth (alternating between x and y)
        axis = depth % self.k
        
        # Sort points by the current axis and find median
        sorted_indices = np.argsort(points[:, axis])
        median_idx = len(points) // 2
        
        # Create node with median point
        median_point_idx = sorted_indices[median_idx]
        node = KDNode(
            point=points[median_point_idx],
            node_id=node_ids[median_point_idx],
            axis=axis
        )
        
        # Recursively build left and right subtrees
        left_indices = sorted_indices[:median_idx]
        right_indices = sorted_indices[median_idx + 1:]
        
        node.left = self._build_recursive(
            points[left_indices],
            node_ids[left_indices],
            depth + 1
        )
        node.right = self._build_recursive(
            points[right_indices],
            node_ids[right_indices],
            depth + 1
        )
        
        return node
    
    def nearest_neighbor(self, query_point: Tuple[float, float], max_distance: float = None) -> Tuple[int, float, float]:
        """
        Find nearest neighbor to query point
        
        Args:
            query_point: (lon, lat) coordinates to search from
            max_distance: Optional maximum distance in meters to search within
            
        Returns:
            Tuple of (node_id, distance_in_meters, search_time)
        """
        start_time = time.time()
        
        query = np.array(query_point)
        best_node, best_distance = self._nearest_recursive(
            self.root,
            query,
            best_node=None,
            best_distance=float('inf')
        )
        
        search_time = time.time() - start_time
        
        if best_node is None:
            # No node found
            return None, float('inf'), search_time
        
        # Calculate actual distance using Haversine formula
        # query_point is (lon, lat), best_node.point is also (lon, lat)
        distance_in_meters = haversine_distance(
            query_point[1],  # query lat
            query_point[0],  # query lon
            best_node.point[1],  # node lat
            best_node.point[0]   # node lon
        )
        
        # If max_distance is specified and distance exceeds it, return None
        if max_distance is not None and distance_in_meters > max_distance:
            return None, distance_in_meters, search_time
        
        return best_node.node_id, distance_in_meters, search_time
    
    def _nearest_recursive(self, node: Optional[KDNode], query: np.ndarray, 
                          best_node: Optional[KDNode], best_distance: float) -> Tuple[KDNode, float]:
        """
        Recursively search for nearest neighbor
        
        Args:
            node: Current node in tree
            query: Query point
            best_node: Current best node found
            best_distance: Current best distance
            
        Returns:
            Tuple of (best_node, best_distance)
        """
        if node is None:
            return best_node, best_distance
        
        # Calculate distance to current node
        distance = np.linalg.norm(node.point - query)
        
        # Update best if current is closer
        if distance < best_distance:
            best_node = node
            best_distance = distance
        
        # Determine which side of the splitting plane the query is on
        axis = node.axis
        diff = query[axis] - node.point[axis]
        
        # Search the side of the tree that the query point is on first
        if diff < 0:
            near_subtree = node.left
            far_subtree = node.right
        else:
            near_subtree = node.right
            far_subtree = node.left
        
        # Search near subtree
        best_node, best_distance = self._nearest_recursive(
            near_subtree, query, best_node, best_distance
        )
        
        # Check if we need to search the far subtree
        # Only search if there could be a closer point on the other side
        if abs(diff) < best_distance:
            best_node, best_distance = self._nearest_recursive(
                far_subtree, query, best_node, best_distance
            )
        
        return best_node, best_distance
    
    def k_nearest_neighbors(self, query_point: Tuple[float, float], k: int) -> List[Tuple[int, float]]:
        """
        Find k nearest neighbors to query point
        
        Args:
            query_point: (lon, lat) coordinates to search from
            k: Number of neighbors to find
            
        Returns:
            List of tuples (node_id, distance_in_meters) sorted by distance
        """
        query = np.array(query_point)
        neighbors = []
        
        self._k_nearest_recursive(self.root, query, k, neighbors)
        
        # Convert distances to meters using Haversine
        neighbors_with_real_distance = []
        for node_id, _ in neighbors:
            # Find the node in the tree to get its coordinates
            node = self._find_node_by_id(self.root, node_id)
            if node:
                distance = haversine_distance(
                    query_point[1], query_point[0],
                    node.point[1], node.point[0]
                )
                neighbors_with_real_distance.append((node_id, distance))
        
        # Sort by distance and return top k
        neighbors_with_real_distance.sort(key=lambda x: x[1])
        return neighbors_with_real_distance[:k]
    
    def _find_node_by_id(self, node: Optional[KDNode], node_id: int) -> Optional[KDNode]:
        """
        Find a node in the tree by its node_id
        
        Args:
            node: Current node in traversal
            node_id: ID to search for
            
        Returns:
            KDNode if found, None otherwise
        """
        if node is None:
            return None
        
        if node.node_id == node_id:
            return node
        
        # Search in both subtrees
        left_result = self._find_node_by_id(node.left, node_id)
        if left_result:
            return left_result
        
        return self._find_node_by_id(node.right, node_id)
    
    def _k_nearest_recursive(self, node: Optional[KDNode], query: np.ndarray, 
                            k: int, neighbors: List[Tuple[int, float]]):
        """
        Recursively search for k nearest neighbors
        
        Args:
            node: Current node in tree
            query: Query point
            k: Number of neighbors to find
            neighbors: List to store neighbors
        """
        if node is None:
            return
        
        # Calculate distance to current node
        distance = np.linalg.norm(node.point - query)
        
        # Add to neighbors list
        neighbors.append((node.node_id, distance))
        
        # Determine which side to search first
        axis = node.axis
        diff = query[axis] - node.point[axis]
        
        if diff < 0:
            near_subtree = node.left
            far_subtree = node.right
        else:
            near_subtree = node.right
            far_subtree = node.left
        
        # Search near subtree
        self._k_nearest_recursive(near_subtree, query, k, neighbors)
        
        # Search far subtree if necessary
        # Check if we have k neighbors and if the splitting plane is close enough
        if len(neighbors) < k or abs(diff) < max(n[1] for n in neighbors[-k:]):
            self._k_nearest_recursive(far_subtree, query, k, neighbors)
    
    def get_stats(self) -> dict:
        """Get statistics about the KD-Tree"""
        return {
            'nodes_count': self.nodes_count,
            'construction_time': self.construction_time,
            'dimensions': self.k
        }


def exhaustive_search(points: List[Tuple[float, float]], node_ids: List[int], 
                     query_point: Tuple[float, float]) -> Tuple[int, float, float]:
    """
    Exhaustive search for nearest neighbor (for comparison)
    
    Args:
        points: List of all points (lon, lat)
        node_ids: List of corresponding node IDs
        query_point: Query point (lon, lat)
        
    Returns:
        Tuple of (node_id, distance_in_meters, search_time)
    """
    start_time = time.time()
    
    min_distance = float('inf')
    nearest_id = None
    
    query_lat = query_point[1]
    query_lon = query_point[0]
    
    for point, node_id in zip(points, node_ids):
        # Calculate real distance using Haversine
        distance = haversine_distance(
            query_lat, query_lon,
            point[1], point[0]  # point is (lon, lat)
        )
        if distance < min_distance:
            min_distance = distance
            nearest_id = node_id
    
    search_time = time.time() - start_time
    
    return nearest_id, min_distance, search_time
