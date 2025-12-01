"""
KD-Tree implementation for efficient nearest neighbor search
Based on the spatial partitioning algorithm for k-dimensional points
"""
import numpy as np
from typing import List, Tuple, Optional
import time


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
    
    def nearest_neighbor(self, query_point: Tuple[float, float]) -> Tuple[int, float, float]:
        """
        Find nearest neighbor to query point
        
        Args:
            query_point: (x, y) coordinates to search from
            
        Returns:
            Tuple of (node_id, distance, search_time)
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
        
        return best_node.node_id, best_distance, search_time
    
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
            query_point: (x, y) coordinates to search from
            k: Number of neighbors to find
            
        Returns:
            List of tuples (node_id, distance) sorted by distance
        """
        query = np.array(query_point)
        neighbors = []
        
        self._k_nearest_recursive(self.root, query, k, neighbors)
        
        # Sort by distance and return top k
        neighbors.sort(key=lambda x: x[1])
        return neighbors[:k]
    
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
        points: List of all points
        node_ids: List of corresponding node IDs
        query_point: Query point
        
    Returns:
        Tuple of (node_id, distance, search_time)
    """
    start_time = time.time()
    
    query = np.array(query_point)
    min_distance = float('inf')
    nearest_id = None
    
    for point, node_id in zip(points, node_ids):
        distance = np.linalg.norm(np.array(point) - query)
        if distance < min_distance:
            min_distance = distance
            nearest_id = node_id
    
    search_time = time.time() - start_time
    
    return nearest_id, min_distance, search_time
