"""
Search algorithms implementation using SimpleAI

UNINFORMED/BLIND SEARCH (no heuristic):
- BFS (Breadth-First Search) - explores level by level
- DFS (Depth-First Search) - explores depth-first
- IDDFS (Iterative Deepening DFS) - combines DFS with BFS advantages

INFORMED SEARCH (uses cost/heuristic information):
- UCS (Uniform Cost Search) - uses path cost g(n) to prioritize nodes
- A* - uses f(n) = g(n) + h(n) with Euclidean heuristic

Note: All algorithms use graph_search=True to avoid infinite loops in cyclic graphs.
The classification (informed/uninformed) refers to whether they use problem-specific
information (heuristics/costs), not the search strategy (graph vs tree search).
"""
from simpleai.search import SearchProblem, breadth_first, depth_first, uniform_cost, limited_depth_first, astar
from simpleai.search.models import SearchNode
from typing import List, Tuple, Optional, Dict
import time
import math
import geopy.distance


class RoutePlanningProblem(SearchProblem):
    """
    Search problem for route planning using SimpleAI
    """
    
    def __init__(self, graph, map_loader, start_node: int, goal_node: int):
        """
        Initialize route planning problem
        
        Args:
            graph: NetworkX graph from OSMnx
            map_loader: MapLoader instance
            start_node: Starting node ID
            goal_node: Goal node ID
        """
        self.graph = graph
        self.map_loader = map_loader
        self.goal_node = goal_node
        
        # Call parent constructor with initial state
        super().__init__(initial_state=start_node)
        
        # Statistics and limits
        self.nodes_expanded = 0
        self.max_depth = 0
        self.max_nodes_limit = 5000  # Allow more exploration for better results
    
    def actions(self, state):
        """
        Return available actions from a state (successor nodes)
        
        Args:
            state: Current node ID
            
        Returns:
            List of successor node IDs
        """
        self.nodes_expanded += 1
        
        # Prevent excessive node expansion
        if self.nodes_expanded > self.max_nodes_limit:
            return []
        
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
        Uses Euclidean distance
        
        Args:
            state: Current node ID
            
        Returns:
            Estimated distance to goal
        """
        return self._euclidean_distance(state, self.goal_node)
    
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
    
    def solve_bfs(self, start_node: int, goal_node: int, timeout: float = 10.0) -> Dict:
        """
        Solve using Breadth-First Search (uninformed/blind search)
        Note: Uses graph_search=False (tree search) - explores without memory
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            timeout: Maximum time in seconds (default 10s)
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        problem = RoutePlanningProblem(self.graph, self.map_loader, start_node, goal_node)
        
        try:
            result = breadth_first(problem, graph_search=False)
            search_time = time.time() - start_time
            
            # Check timeout
            if search_time > timeout:
                return {
                    'algorithm': 'BFS',
                    'success': False,
                    'error': f'Timeout exceeded ({timeout}s)',
                    'search_time': search_time,
                    'nodes_expanded': problem.nodes_expanded
                }
            
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
                'search_time': search_time,
                'nodes_expanded': problem.nodes_expanded
            }
        
        return {
            'algorithm': 'BFS',
            'success': False,
            'error': 'No path found',
            'search_time': time.time() - start_time,
            'nodes_expanded': problem.nodes_expanded
        }
    
    def solve_dfs(self, start_node: int, goal_node: int, timeout: float = 10.0) -> Dict:
        """
        Solve using Depth-First Search (uninformed/blind search)
        Note: Uses graph_search=True to avoid infinite loops
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            timeout: Maximum time in seconds (default 10s)
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        problem = RoutePlanningProblem(self.graph, self.map_loader, start_node, goal_node)
        
        try:
            result = depth_first(problem, graph_search=True)
            search_time = time.time() - start_time
            
            # Check timeout
            if search_time > timeout:
                return {
                    'algorithm': 'DFS',
                    'success': False,
                    'error': f'Timeout exceeded ({timeout}s)',
                    'search_time': search_time,
                    'nodes_expanded': problem.nodes_expanded
                }
            
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
                'search_time': search_time,
                'nodes_expanded': problem.nodes_expanded
            }
        
        return {
            'algorithm': 'DFS',
            'success': False,
            'error': 'No path found',
            'search_time': time.time() - start_time,
            'nodes_expanded': problem.nodes_expanded
        }
    
    def solve_ucs(self, start_node: int, goal_node: int) -> Dict:
        """
        Solve using Uniform Cost Search (informed search - uses cost information)
        
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
        Solve using Iterative Deepening Depth-First Search (uninformed/blind search)
        Manually implements IDDFS by calling limited DFS with increasing depths
        Note: Uses graph_search=False (tree search) - explores without memory
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            max_depth: Maximum depth to search (default 50 for small graphs)
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        print(f"IDDFS: Solving from {start_node} to {goal_node} with max_depth={max_depth}")
        
        problem = RoutePlanningProblem(self.graph, self.map_loader, start_node, goal_node)
        
        # Iterative deepening: try increasing depth limits
        for depth in range(1, max_depth + 1):
            try:
                # Reset nodes expanded counter for each iteration
                iteration_problem = RoutePlanningProblem(self.graph, self.map_loader, start_node, goal_node)
                
                # Try limited depth first search at this depth
                result = limited_depth_first(iteration_problem, graph_search=False, depth_limit=depth)
                
                if result:
                    path = [node[1] for node in result.path()]
                    search_time = time.time() - start_time
                    print(f"IDDFS: Found path with {len(path)} nodes at depth {depth}")
                    return {
                        'algorithm': 'IDDFS',
                        'success': True,
                        'path': path,
                        'path_length': len(path),
                        'search_time': search_time,
                        'nodes_expanded': iteration_problem.nodes_expanded,
                        'cost': self._calculate_path_cost(path),
                        'depth_reached': depth
                    }
                    
            except Exception as e:
                # If error at this depth, continue to next depth
                if "maximum recursion depth" in str(e).lower():
                    print(f"IDDFS: Recursion limit at depth {depth}, trying next")
                    continue
                # For other errors, only fail if we've tried all depths
                if depth == max_depth:
                    search_time = time.time() - start_time
                    print(f"IDDFS: Error at max depth {max_depth}: {str(e)}")
                    return {
                        'algorithm': 'IDDFS',
                        'success': False,
                        'error': str(e),
                        'search_time': search_time
                    }
        
        # No solution found within depth limit
        search_time = time.time() - start_time
        print(f"IDDFS: No path found within depth limit of {max_depth}")
        return {
            'algorithm': 'IDDFS',
            'success': False,
            'error': f'No path found within depth limit of {max_depth}',
            'search_time': search_time
        }
    
    def solve_astar(self, start_node: int, goal_node: int) -> Dict:
        """
        Solve using A* search with Euclidean heuristic (informed search - uses heuristic)
        
        Args:
            start_node: Starting node ID
            goal_node: Goal node ID
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        problem = RoutePlanningProblem(
            self.graph, 
            self.map_loader, 
            start_node, 
            goal_node
        )
        
        try:
            result = astar(problem, graph_search=True)
            search_time = time.time() - start_time
            
            if result:
                path = [node[1] for node in result.path()]
                return {
                    'algorithm': 'A* (Euclidean)',
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
                'algorithm': 'A* (Euclidean)',
                'success': False,
                'error': str(e),
                'search_time': search_time
            }
        
        return {
            'algorithm': 'A* (Euclidean)',
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
        
        # A* with Euclidean heuristic
        results.append(self.solve_astar(start_node, goal_node))
        
        return results
