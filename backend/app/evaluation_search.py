"""
Evaluation module for search algorithms
Compares BFS, DFS, UCS, IDDFS, and A* performance
"""
import random
import json
from typing import List, Dict, Tuple
from .map_loader import MapLoader
from .search_algorithms import SearchAlgorithms


class SearchAlgorithmsEvaluator:
    """Evaluates different search algorithms performance"""
    
    def __init__(self, map_loader: MapLoader):
        """
        Initialize evaluator
        
        Args:
            map_loader: MapLoader instance with loaded graph
        """
        self.map_loader = map_loader
        self.search_algorithms = SearchAlgorithms(map_loader.graph, map_loader)
        self.all_nodes = list(map_loader.graph.nodes())
    
    def select_node_pairs_by_distance(self, min_dist: float, max_dist: float, 
                                     num_pairs: int = 5) -> List[Tuple[int, int]]:
        """
        Select pairs of nodes within a distance range
        
        Args:
            min_dist: Minimum distance in meters
            max_dist: Maximum distance in meters
            num_pairs: Number of pairs to select
            
        Returns:
            List of (start_node, goal_node) tuples
        """
        pairs = []
        attempts = 0
        max_attempts = num_pairs * 100  # Limit attempts
        
        print(f"Selecting {num_pairs} node pairs with distance between {min_dist}m and {max_dist}m...")
        
        while len(pairs) < num_pairs and attempts < max_attempts:
            attempts += 1
            
            # Randomly select two nodes
            node1, node2 = random.sample(self.all_nodes, 2)
            
            # Calculate distance
            distance = self.map_loader.calculate_distance(node1, node2)
            
            # Check if within range
            if min_dist <= distance <= max_dist:
                pairs.append((node1, node2))
                print(f"  Pair {len(pairs)}: Node {node1} -> Node {node2} ({distance:.2f}m)")
        
        if len(pairs) < num_pairs:
            print(f"Warning: Only found {len(pairs)} pairs after {max_attempts} attempts")
        
        return pairs
    
    def evaluate_algorithm_on_pairs(self, algorithm_name: str, pairs: List[Tuple[int, int]]) -> List[Dict]:
        """
        Evaluate a single algorithm on multiple node pairs
        
        Args:
            algorithm_name: Name of algorithm (bfs, dfs, ucs, iddfs, astar)
            pairs: List of (start_node, goal_node) tuples
            
        Returns:
            List of results for each pair
        """
        results = []
        
        for i, (start_node, goal_node) in enumerate(pairs):
            print(f"  Running {algorithm_name.upper()} on pair {i+1}/{len(pairs)}...")
            
            distance = self.map_loader.calculate_distance(start_node, goal_node)
            
            # Run appropriate algorithm with timeout
            timeout = 60.0  # 60 seconds per algorithm run
            if algorithm_name == 'bfs':
                result = self.search_algorithms.solve_bfs(start_node, goal_node, timeout=timeout)
            elif algorithm_name == 'dfs':
                result = self.search_algorithms.solve_dfs(start_node, goal_node, timeout=timeout)
            elif algorithm_name == 'ucs':
                result = self.search_algorithms.solve_ucs(start_node, goal_node)
            elif algorithm_name == 'iddfs':
                result = self.search_algorithms.solve_iddfs(start_node, goal_node)
            elif algorithm_name == 'astar':
                result = self.search_algorithms.solve_astar(start_node, goal_node)
            else:
                continue
            
            # Check if timed out or hit node limit
            if not result.get('success'):
                print(f"    ⚠️ {result.get('error', 'Failed')} - Nodes expanded: {result.get('nodes_expanded', 'N/A')}")
            
            # Add pair information
            result['pair_index'] = i
            result['start_node'] = int(start_node)
            result['goal_node'] = int(goal_node)
            result['straight_line_distance'] = float(distance)
            
            results.append(result)
        
        return results
    
    def evaluate_all_algorithms_on_pairs(self, pairs: List[Tuple[int, int]]) -> Dict:
        """
        Evaluate all algorithms on the same node pairs
        
        Args:
            pairs: List of (start_node, goal_node) tuples
            
        Returns:
            Dictionary with results for all algorithms
        """
        algorithms = ['bfs', 'dfs', 'ucs', 'iddfs', 'astar']
        all_results = {}
        
        for algorithm in algorithms:
            print(f"\nEvaluating {algorithm.upper()}...")
            results = self.evaluate_algorithm_on_pairs(algorithm, pairs)
            all_results[algorithm] = results
        
        return all_results
    
    def calculate_statistics(self, results: Dict) -> Dict:
        """
        Calculate statistics for algorithm results
        
        Args:
            results: Dictionary with algorithm results
            
        Returns:
            Dictionary with statistics
        """
        stats = {}
        
        for algorithm, algo_results in results.items():
            # Filter successful results
            successful = [r for r in algo_results if r.get('success', False)]
            
            if not successful:
                stats[algorithm] = {
                    'success_rate': 0,
                    'avg_time': None,
                    'avg_path_length': None,
                    'avg_cost': None
                }
                continue
            
            # Calculate averages
            times = [r['search_time'] for r in successful]
            path_lengths = [r['path_length'] for r in successful]
            costs = [r['cost'] for r in successful]
            
            stats[algorithm] = {
                'success_rate': len(successful) / len(algo_results),
                'num_successful': len(successful),
                'num_total': len(algo_results),
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'avg_path_length': sum(path_lengths) / len(path_lengths),
                'avg_cost': sum(costs) / len(costs),
                'min_cost': min(costs),
                'max_cost': max(costs)
            }
        
        return stats
    
    def run_distance_range_evaluation(self, min_dist: float, max_dist: float, 
                                     num_pairs: int = 5) -> Dict:
        """
        Run evaluation for a specific distance range
        
        Args:
            min_dist: Minimum distance in meters
            max_dist: Maximum distance in meters
            num_pairs: Number of pairs to evaluate
            
        Returns:
            Dictionary with evaluation results
        """
        print(f"\n{'='*60}")
        print(f"EVALUATING DISTANCE RANGE: {min_dist}m - {max_dist}m")
        print(f"{'='*60}")
        
        # Select node pairs
        pairs = self.select_node_pairs_by_distance(min_dist, max_dist, num_pairs)
        
        if not pairs:
            return {
                'distance_range': {'min': min_dist, 'max': max_dist},
                'num_pairs': 0,
                'error': 'No suitable pairs found'
            }
        
        # Evaluate all algorithms
        results = self.evaluate_all_algorithms_on_pairs(pairs)
        
        # Calculate statistics
        stats = self.calculate_statistics(results)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"SUMMARY FOR RANGE {min_dist}m - {max_dist}m")
        print(f"{'='*60}")
        for algorithm, algo_stats in stats.items():
            print(f"\n{algorithm.upper()}:")
            print(f"  Success rate: {algo_stats['success_rate']*100:.1f}%")
            if algo_stats['avg_time']:
                print(f"  Avg time: {algo_stats['avg_time']*1000:.3f} ms")
                print(f"  Avg path length: {algo_stats['avg_path_length']:.1f} nodes")
                print(f"  Avg cost: {algo_stats['avg_cost']:.2f} meters")
        
        return {
            'distance_range': {'min': min_dist, 'max': max_dist},
            'num_pairs': len(pairs),
            'pairs': [(int(p[0]), int(p[1])) for p in pairs],
            'results': results,
            'statistics': stats
        }
    
    def run_full_evaluation(self, num_pairs_per_range: int = 5) -> Dict:
        """
        Run complete evaluation across all distance ranges
        
        Args:
            num_pairs_per_range: Number of pairs to test per range
            
        Returns:
            Dictionary with all evaluation results
        """
        print("=" * 60)
        print("SEARCH ALGORITHMS EVALUATION")
        print("=" * 60)
        print(f"Graph has {len(self.all_nodes)} nodes")
        
        ranges = [
            (0, 1000, "Short distance (< 1000m)"),
            (1000, 5000, "Medium distance (1000m - 5000m)"),
            (5000, 50000, "Long distance (> 5000m)")
        ]
        
        all_results = {}
        
        for min_dist, max_dist, label in ranges:
            print(f"\n\n{'#'*60}")
            print(f"# {label}")
            print(f"{'#'*60}")
            
            range_results = self.run_distance_range_evaluation(
                min_dist, max_dist, num_pairs_per_range
            )
            all_results[label] = range_results
        
        print(f"\n\n{'='*60}")
        print("OVERALL COMPARISON")
        print(f"{'='*60}")
        
        best_algorithms = {}
        for label, range_results in all_results.items():
            if 'statistics' in range_results:
                stats = range_results['statistics']
                # Find algorithm with best score considering time, distance, and nodes
                valid_algos = {k: v for k, v in stats.items() 
                              if v.get('avg_distance') is not None and v.get('success_rate', 0) > 0}
                if valid_algos:
                    # Calculate composite score for each algorithm
                    # Lower is better for all metrics
                    scores = {}
                    
                    # Get min/max for normalization
                    min_time = min(v['avg_time'] for v in valid_algos.values())
                    max_time = max(v['avg_time'] for v in valid_algos.values())
                    min_dist = min(v['avg_distance'] for v in valid_algos.values())
                    max_dist = max(v['avg_distance'] for v in valid_algos.values())
                    min_nodes = min(v['avg_nodes_expanded'] for v in valid_algos.values())
                    max_nodes = max(v['avg_nodes_expanded'] for v in valid_algos.values())
                    
                    for algo, metrics in valid_algos.items():
                        # Normalize each metric to 0-1 scale (avoid division by zero)
                        time_norm = (metrics['avg_time'] - min_time) / (max_time - min_time) if max_time > min_time else 0
                        dist_norm = (metrics['avg_distance'] - min_dist) / (max_dist - min_dist) if max_dist > min_dist else 0
                        nodes_norm = (metrics['avg_nodes_expanded'] - min_nodes) / (max_nodes - min_nodes) if max_nodes > min_nodes else 0
                        
                        # Weighted score: distance (50%), time (30%), nodes (20%)
                        # Distance is most important for route quality
                        score = (dist_norm * 0.5) + (time_norm * 0.3) + (nodes_norm * 0.2)
                        scores[algo] = score
                    
                    # Find algorithm with lowest (best) score
                    best_algo_name = min(scores.items(), key=lambda x: x[1])[0]
                    best_algo_stats = valid_algos[best_algo_name]
                    
                    best_algorithms[label] = best_algo_name
                    print(f"\n{label}:")
                    print(f"  Best: {best_algo_name.upper()}")
                    print(f"    Score: {scores[best_algo_name]:.3f} (lower is better)")
                    print(f"    Avg Distance: {best_algo_stats['avg_distance']:.1f}m")
                    print(f"    Avg Time: {best_algo_stats['avg_time']:.2f}ms")
                    print(f"    Avg Nodes Expanded: {best_algo_stats['avg_nodes_expanded']:.1f}")
                    print(f"    Path Quality: {'Optimal' if best_algo_name in ['astar', 'ucs'] else 'May be suboptimal'}")
        
        # Overall recommendation based on all ranges
        print(f"\n\n{'='*60}")
        print("OVERALL BEST ALGORITHM")
        print(f"{'='*60}")
        
        # Count which algorithm won most ranges
        if best_algorithms:
            from collections import Counter
            algo_wins = Counter(best_algorithms.values())
            overall_best = algo_wins.most_common(1)[0][0]
            
            print(f"Winner: {overall_best.upper()}")
            print(f"\nWins by range:")
            for label, algo in best_algorithms.items():
                print(f"  {label}: {algo.upper()}")
            
            print(f"\nEvaluation criteria:")
            print(f"  • Distance (50% weight) - Path quality")
            print(f"  • Time (30% weight) - Execution speed")
            print(f"  • Nodes Expanded (20% weight) - Efficiency")
            
            if overall_best in ['astar', 'ucs']:
                print(f"\n✓ {overall_best.upper()} guarantees optimal (shortest) paths")
            else:
                print(f"\n⚠ {overall_best.upper()} may find suboptimal paths")
        else:
            overall_best = 'astar'
            print("Using A* as default recommendation")
        
        print(f"{'='*60}\n")
        
        return {
            'graph_stats': {
                'num_nodes': len(self.all_nodes),
                'num_edges': self.map_loader.graph.number_of_edges()
            },
            'evaluation_ranges': all_results,
            'best_algorithms': best_algorithms,
            'overall_recommendation': overall_best
        }
    
    def save_results(self, results: Dict, filename: str = 'search_evaluation.json'):
        """
        Save evaluation results to JSON file
        
        Args:
            results: Results dictionary
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filename}")
