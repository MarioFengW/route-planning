"""
Search algorithms implementation using SimpleAI
Implements: BFS, DFS, UCS, IDDFS, and A*
"""
from simpleai.search import SearchProblem, breadth_first, depth_first, uniform_cost, iterative_limited_depth_first, astar
from simpleai.search.models import SearchNode
from typing import List, Tuple, Optional, Dict
import time
import math
import geopy.distance


class RoutePlanningProblem(SearchProblem):
    """
    Search problem for route planning using SimpleAI
    """
    
    def __init__(self, graph, map_loader, start_node: int, goal_node: int, 
                 heuristic_type: str = 'euclidean'):
        """
        Initialize route planning problem
        
        Args:
            graph: NetworkX graph from OSMnx
            map_loader: MapLoader instance
            start_node: Starting node ID
            goal_node: Goal node ID
            heuristic_type: Type of heuristic ('euclidean', 'haversine', 'manhattan')
        """
        self.graph = graph
        self.map_loader = map_loader
        self.goal_node = goal_node
        self.heuristic_type = heuristic_type
        
        # Call parent constructor with initial state
        super().__init__(initial_state=start_node)
        
        # Statistics
        self.nodes_expanded = 0
        self.max_depth = 0
    
    def actions(self, state):
        """
        Return available actions from a state (successor nodes)
        
        Args:
            state: Current node ID
            
        Returns:
            List of successor node IDs
        """
        self.nodes_expanded += 1
        return self.map_loader.get_successors(state)
    
    def result(self, state, action):
        """
        Return resulting state after taking an action
        
        Args:
            state: Current node ID
            action: Action to take (successor node ID)
            
        Returns:
            New state (node ID)
        """
        return action
    
    def is_goal(self, state):
        """
        Check if state is the goal
        
        Args:
            state: Current node ID
            
        Returns:
            True if goal reached
        """
        return state == self.goal_node
    
    def cost(self, state, action, state2):
        """
        Cost of moving from state to state2 via action
        Used for UCS and A*
        
        Args:
            state: Current node ID
            action: Action taken
            state2: Resulting node ID
            
        Returns:
            Cost (edge length in meters)
        """
        edge_data = self.map_loader.get_edge_data(state, state2)
        if edge_data:
            return edge_data.get('length', 0)
        return 0
    
    def heuristic(self, state):
        """
        Heuristic function for A* (estimated distance to goal)
        
        Args:
            state: Current node ID
            
        Returns:
            Estimated distance to goal
        """
        if self.heuristic_type == 'euclidean':
            return self._euclidean_distance(state, self.goal_node)
        elif self.heuristic_type == 'haversine':
            return self._haversine_distance(state, self.goal_node)
        elif self.heuristic_type == 'manhattan':
            return self._manhattan_distance(state, self.goal_node)
        else:
            return 0
    
    def _euclidean_distance(self, node1: int, node2: int) -> float:
        """Calculate Euclidean distance between two nodes"""
        coord1 = self.map_loader.get_node_coords(node1)
        coord2 = self.map_loader.get_node_coords(node2)
        
        if coord1 and coord2:
            dx = coord2[0] - coord1[0]
            dy = coord2[1] - coord1[1]
            # Approximate conversion: 1 degree ≈ 111km
            return math.sqrt(dx**2 + dy**2) * 111000
        return 0
    
    def _haversine_distance(self, node1: int, node2: int) -> float:
        """Calculate Haversine distance between two nodes (great circle distance)"""
        coord1 = self.map_loader.get_node_latlon(node1)
        coord2 = self.map_loader.get_node_latlon(node2)
        
        if coord1 and coord2:
            return geopy.distance.distance(coord1, coord2).m
        return 0
    
    def _manhattan_distance(self, node1: int, node2: int) -> float:
        """Calculate Manhattan distance between two nodes"""
        coord1 = self.map_loader.get_node_coords(node1)
        coord2 = self.map_loader.get_node_coords(node2)
        
        if coord1 and coord2:
            dx = abs(coord2[0] - coord1[0])
            dy = abs(coord2[1] - coord1[1])
            # Approximate conversion: 1 degree ≈ 111km
            return (dx + dy) * 111000
        return 0


class SearchAlgorithms:
    """
    Wrapper class for search algorithms using SimpleAI
    """
    
    def __init__(self, graph, map_loader):
        """
        Initialize search algorithms
        
        Args:
            graph: NetworkX graph from OSMnx
            map_loader: MapLoader instance
        """
        self.graph = graph
        self.map_loader = map_loader
    
    def solve_bfs(self, start_node: int, goal_node: int) -> Dict:
        """
        Solve using Breadth-First Search
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        problem = RoutePlanningProblem(self.graph, self.map_loader, start_node, goal_node)
        
        try:
            result = breadth_first(problem, graph_search=True)
            search_time = time.time() - start_time
            
            if result:
                path = [node[1] for node in result.path()]
                return {
                    'algorithm': 'BFS',
                    'success': True,
                    'path': path,
                    'path_length': len(path),
                    'search_time': search_time,
                    'nodes_expanded': problem.nodes_expanded,
                    'cost': self._calculate_path_cost(path)
                }
        except Exception as e:
            search_time = time.time() - start_time
            return {
                'algorithm': 'BFS',
                'success': False,
                'error': str(e),
                'search_time': search_time
            }
        
        return {
            'algorithm': 'BFS',
            'success': False,
            'search_time': time.time() - start_time
        }
    
    def solve_dfs(self, start_node: int, goal_node: int) -> Dict:
        """
        Solve using Depth-First Search
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        problem = RoutePlanningProblem(self.graph, self.map_loader, start_node, goal_node)
        
        try:
            result = depth_first(problem, graph_search=True)
            search_time = time.time() - start_time
            
            if result:
                path = [node[1] for node in result.path()]
                return {
                    'algorithm': 'DFS',
                    'success': True,
                    'path': path,
                    'path_length': len(path),
                    'search_time': search_time,
                    'nodes_expanded': problem.nodes_expanded,
                    'cost': self._calculate_path_cost(path)
                }
        except Exception as e:
            search_time = time.time() - start_time
            return {
                'algorithm': 'DFS',
                'success': False,
                'error': str(e),
                'search_time': search_time
            }
        
        return {
            'algorithm': 'DFS',
            'success': False,
            'search_time': time.time() - start_time
        }
    
    def solve_ucs(self, start_node: int, goal_node: int) -> Dict:
        """
        Solve using Uniform Cost Search
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        problem = RoutePlanningProblem(self.graph, self.map_loader, start_node, goal_node)
        
        try:
            result = uniform_cost(problem, graph_search=True)
            search_time = time.time() - start_time
            
            if result:
                path = [node[1] for node in result.path()]
                return {
                    'algorithm': 'UCS',
                    'success': True,
                    'path': path,
                    'path_length': len(path),
                    'search_time': search_time,
                    'nodes_expanded': problem.nodes_expanded,
                    'cost': self._calculate_path_cost(path)
                }
        except Exception as e:
            search_time = time.time() - start_time
            return {
                'algorithm': 'UCS',
                'success': False,
                'error': str(e),
                'search_time': search_time
            }
        
        return {
            'algorithm': 'UCS',
            'success': False,
            'search_time': time.time() - start_time
        }
    
    def solve_iddfs(self, start_node: int, goal_node: int, max_depth: int = 50) -> Dict:
        """
        Solve using Iterative Deepening Depth-First Search
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            max_depth: Maximum depth to search
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        problem = RoutePlanningProblem(self.graph, self.map_loader, start_node, goal_node)
        
        try:
            result = iterative_limited_depth_first(problem, graph_search=True, depth_limit=max_depth)
            search_time = time.time() - start_time
            
            if result:
                path = [node[1] for node in result.path()]
                return {
                    'algorithm': 'IDDFS',
                    'success': True,
                    'path': path,
                    'path_length': len(path),
                    'search_time': search_time,
                    'nodes_expanded': problem.nodes_expanded,
                    'cost': self._calculate_path_cost(path)
                }
        except Exception as e:
            search_time = time.time() - start_time
            return {
                'algorithm': 'IDDFS',
                'success': False,
                'error': str(e),
                'search_time': search_time
            }
        
        return {
            'algorithm': 'IDDFS',
            'success': False,
            'search_time': time.time() - start_time
        }
    
    def solve_astar(self, start_node: int, goal_node: int, heuristic_type: str = 'haversine') -> Dict:
        """
        Solve using A* search
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            heuristic_type: Type of heuristic to use
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        problem = RoutePlanningProblem(
            self.graph, 
            self.map_loader, 
            start_node, 
            goal_node,
            heuristic_type=heuristic_type
        )
        
        try:
            result = astar(problem, graph_search=True)
            search_time = time.time() - start_time
            
            if result:
                path = [node[1] for node in result.path()]
                return {
                    'algorithm': f'A* ({heuristic_type})',
                    'success': True,
                    'path': path,
                    'path_length': len(path),
                    'search_time': search_time,
                    'nodes_expanded': problem.nodes_expanded,
                    'cost': self._calculate_path_cost(path)
                }
        except Exception as e:
            search_time = time.time() - start_time
            return {
                'algorithm': f'A* ({heuristic_type})',
                'success': False,
                'error': str(e),
                'search_time': search_time
            }
        
        return {
            'algorithm': f'A* ({heuristic_type})',
            'success': False,
            'search_time': time.time() - start_time
        }
    
    def _calculate_path_cost(self, path: List[int]) -> float:
        """
        Calculate total cost of a path
        
        Args:
            path: List of node IDs
            
        Returns:
            Total path cost in meters
        """
        total_cost = 0
        for i in range(len(path) - 1):
            edge_data = self.map_loader.get_edge_data(path[i], path[i + 1])
            if edge_data:
                total_cost += edge_data.get('length', 0)
        return total_cost
    
    def solve_all(self, start_node: int, goal_node: int) -> List[Dict]:
        """
        Solve using all algorithms and return results
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            
        Returns:
            List of results from all algorithms
        """
        results = []
        
        # BFS
        results.append(self.solve_bfs(start_node, goal_node))
        
        # DFS
        results.append(self.solve_dfs(start_node, goal_node))
        
        # UCS
        results.append(self.solve_ucs(start_node, goal_node))
        
        # IDDFS
        results.append(self.solve_iddfs(start_node, goal_node))
        
        # A* with different heuristics
        results.append(self.solve_astar(start_node, goal_node, 'haversine'))
        results.append(self.solve_astar(start_node, goal_node, 'euclidean'))
        
        return results
