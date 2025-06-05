"""
Neo4j Graph Query Performance Debugger
Focus on financial transaction pattern detection
"""

from neo4j import GraphDatabase
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

class GraphQueryDebugger:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.debug_dir = Path("./graph_debug")
        self.debug_dir.mkdir(exist_ok=True)
        
        # Performance metrics storage
        self.query_metrics = []
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('graph_debug.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def profile_query(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Profile a Cypher query with detailed metrics"""
        with self.driver.session() as session:
            # Explain query plan
            explain_query = f"EXPLAIN {query}"
            explain_result = session.run(explain_query, params or {})
            plan = explain_result.consume().plan
            
            # Profile query execution
            profile_query = f"PROFILE {query}"
            start_time = time.time()
            result = session.run(profile_query, params or {})
            records = list(result)
            end_time = time.time()
            
            summary = result.consume()
            
            metrics = {
                'query': query,
                'params': params,
                'execution_time': end_time - start_time,
                'db_hits': summary.profile.get('db_hits', 0),
                'rows_returned': len(records),
                'timestamp': datetime.now().isoformat(),
                'plan': self._extract_plan_details(plan),
                'profile': summary.profile
            }
            
            self.query_metrics.append(metrics)
            self.logger.info(f"Query executed in {metrics['execution_time']:.3f}s")
            
            return metrics
    
    def analyze_financial_patterns(self):
        """Debug common financial pattern queries"""
        test_queries = {
            'money_flow': """
                MATCH path = (sender:Account)-[t:TRANSFER*1..5]->(receiver:Account)
                WHERE t.amount > $threshold
                RETURN path, reduce(total = 0, r IN relationships(path) | total + r.amount) as total_flow
                ORDER BY total_flow DESC
                LIMIT 10
            """,
            
            'circular_transactions': """
                MATCH path = (a:Account)-[t:TRANSFER*3..6]->(a)
                WHERE ALL(r IN relationships(path) WHERE r.amount > $min_amount)
                RETURN path, length(path) as cycle_length
            """,
            
            'suspicious_timing': """
                MATCH (a:Account)-[t1:TRANSFER]->(b:Account)-[t2:TRANSFER]->(c:Account)
                WHERE abs(t1.timestamp - t2.timestamp) < $time_window
                AND t1.amount > $threshold
                RETURN a, b, c, t1, t2
            """
        }
        
        results = {}
        for query_name, query in test_queries.items():
            params = {
                'threshold': 10000,
                'min_amount': 5000,
                'time_window': 3600  # 1 hour
            }
            
            self.logger.info(f"Testing query: {query_name}")
            metrics = self.profile_query(query, params)
            results[query_name] = metrics
            
            # Generate optimization suggestions
            suggestions = self.suggest_optimizations(metrics)
            results[query_name]['optimizations'] = suggestions
        
        # Save analysis
        with open(self.debug_dir / 'financial_pattern_analysis.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
