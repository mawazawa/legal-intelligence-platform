"""
DuckDB-Powered Financial Graph API
Provides high-performance graph analytics for financial transactions
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

import duckdb
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import networkx as nx
import pandas as pd
import numpy as np
from redis import Redis
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "/data/graph/financial.duckdb")
API_KEY = os.getenv("API_KEY", "change_me_in_production")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# Initialize connections
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
security = HTTPBearer()

# Initialize DuckDB
conn = duckdb.connect(DUCKDB_PATH)
# Create tables if not exists
conn.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_account VARCHAR,
    target_account VARCHAR,
    amount DECIMAL(18,2),
    currency VARCHAR(3),
    transaction_date DATE,
    transaction_type VARCHAR,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id VARCHAR UNIQUE,
    entity_type VARCHAR,
    name VARCHAR,
    attributes JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity VARCHAR,
    target_entity VARCHAR,
    relationship_type VARCHAR,
    weight DECIMAL(10,2),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Create indexes
conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_source ON transactions(source_account)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_target ON transactions(target_account)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(transaction_date)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_entity)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_entity)")
# Pydantic models
class Transaction(BaseModel):
    source_account: str
    target_account: str
    amount: float
    currency: str = "USD"
    transaction_date: str
    transaction_type: str
    metadata: Optional[Dict] = {}

class GraphQuery(BaseModel):
    query_type: str = Field(..., description="Type of graph query: paths, community, centrality, anomaly")
    parameters: Dict[str, Any]
    limit: int = 100

class GraphResponse(BaseModel):
    query_type: str
    results: List[Dict]
    execution_time: float
    cached: bool = False

# FastAPI app
app = FastAPI(title="Financial Graph API", version="1.0.0")

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials.credentials

@app.get("/health")
async def health_check():
    try:
        conn.execute("SELECT 1").fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
@app.post("/transactions", dependencies=[Depends(verify_api_key)])
async def create_transaction(transaction: Transaction):
    """Insert a new transaction into the graph"""
    try:
        conn.execute("""
            INSERT INTO transactions 
            (source_account, target_account, amount, currency, transaction_date, transaction_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction.source_account,
            transaction.target_account,
            transaction.amount,
            transaction.currency,
            transaction.transaction_date,
            transaction.transaction_type,
            json.dumps(transaction.metadata)
        ))
        return {"status": "success", "message": "Transaction created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", dependencies=[Depends(verify_api_key)])
async def execute_graph_query(query: GraphQuery) -> GraphResponse:
    """Execute complex graph queries"""
    start_time = time.time()
    
    # Check cache first
    cache_key = f"graph_query:{json.dumps(query.dict(), sort_keys=True)}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        result = json.loads(cached_result)
        result["cached"] = True
        return GraphResponse(**result)
    
    try:
        if query.query_type == "paths":
            results = await find_transaction_paths(query.parameters)
        elif query.query_type == "community":
            results = await detect_communities(query.parameters)
        elif query.query_type == "centrality":
            results = await calculate_centrality(query.parameters)
        elif query.query_type == "anomaly":
            results = await detect_anomalies(query.parameters)
        else:
            raise HTTPException(status_code=400, detail="Invalid query type")        
        execution_time = time.time() - start_time
        response = GraphResponse(
            query_type=query.query_type,
            results=results,
            execution_time=execution_time
        )
        
        # Cache the result
        redis_client.setex(cache_key, 300, json.dumps(response.dict()))
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def find_transaction_paths(params: Dict) -> List[Dict]:
    """Find transaction paths between accounts"""
    source = params.get("source_account")
    target = params.get("target_account")
    max_depth = params.get("max_depth", 5)
    
    # Build graph from transactions
    df = conn.execute("""
        SELECT source_account, target_account, amount, transaction_date
        FROM transactions
        WHERE transaction_date >= ?
    """, (params.get("start_date", "2020-01-01"),)).df()
    
    G = nx.from_pandas_edgelist(
        df, 
        source='source_account', 
        target='target_account',
        edge_attr=['amount'],
        create_using=nx.DiGraph()
    )
    
    # Find all paths
    try:
        paths = list(nx.all_simple_paths(G, source, target, cutoff=max_depth))
        results = []
        for path in paths[:10]:  # Limit to 10 paths
            path_info = {
                "path": path,
                "length": len(path) - 1,
                "total_amount": sum(G[path[i]][path[i+1]]['amount'] for i in range(len(path)-1))
            }
            results.append(path_info)
        return results
    except nx.NetworkXNoPath:
        return []
async def detect_communities(params: Dict) -> List[Dict]:
    """Detect communities in the transaction network"""
    min_transactions = params.get("min_transactions", 5)
    
    # Get transaction data
    df = conn.execute("""
        SELECT source_account, target_account, COUNT(*) as transaction_count, 
               SUM(amount) as total_amount
        FROM transactions
        GROUP BY source_account, target_account
        HAVING COUNT(*) >= ?
    """, (min_transactions,)).df()
    
    # Build graph
    G = nx.from_pandas_edgelist(
        df,
        source='source_account',
        target='target_account',
        edge_attr=['transaction_count', 'total_amount']
    )
    
    # Detect communities
    communities = nx.community.greedy_modularity_communities(G)
    
    results = []
    for i, community in enumerate(communities):
        community_list = list(community)
        subgraph = G.subgraph(community_list)
        
        results.append({
            "community_id": i,
            "size": len(community_list),
            "members": community_list[:20],  # Limit members shown
            "total_edges": subgraph.number_of_edges(),
            "density": nx.density(subgraph)
        })
    
    return sorted(results, key=lambda x: x['size'], reverse=True)[:10]

async def calculate_centrality(params: Dict) -> List[Dict]:
    """Calculate centrality measures for accounts"""
    centrality_type = params.get("centrality_type", "pagerank")
    
    # Build transaction graph
    df = conn.execute("""
        SELECT source_account, target_account, amount
        FROM transactions
        WHERE transaction_date >= ?
    """, (params.get("start_date", "2020-01-01"),)).df()    
    G = nx.from_pandas_edgelist(
        df,
        source='source_account',
        target='target_account',
        edge_attr='amount',
        create_using=nx.DiGraph()
    )
    
    # Calculate centrality
    if centrality_type == "pagerank":
        centrality = nx.pagerank(G, weight='amount')
    elif centrality_type == "betweenness":
        centrality = nx.betweenness_centrality(G, weight='amount')
    elif centrality_type == "degree":
        centrality = nx.degree_centrality(G)
    else:
        centrality = nx.eigenvector_centrality(G, weight='amount')
    
    # Format results
    results = [
        {
            "account": account,
            "centrality_score": score,
            "rank": rank + 1
        }
        for rank, (account, score) in enumerate(
            sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:50]
        )
    ]
    
    return results

async def detect_anomalies(params: Dict) -> List[Dict]:
    """Detect anomalous transactions using statistical methods"""
    threshold = params.get("threshold", 3.0)  # Standard deviations
    
    # Get transaction statistics
    stats = conn.execute("""
        SELECT 
            source_account,
            target_account,
            amount,
            transaction_date,
            AVG(amount) OVER (PARTITION BY source_account) as avg_amount,
            STDDEV(amount) OVER (PARTITION BY source_account) as std_amount
        FROM transactions
        WHERE transaction_date >= ?
    """, (params.get("start_date", "2020-01-01"),)).df()    
    # Calculate z-scores
    stats['z_score'] = (stats['amount'] - stats['avg_amount']) / stats['std_amount']
    
    # Find anomalies
    anomalies = stats[abs(stats['z_score']) > threshold]
    
    results = []
    for _, row in anomalies.iterrows():
        results.append({
            "source_account": row['source_account'],
            "target_account": row['target_account'],
            "amount": float(row['amount']),
            "transaction_date": str(row['transaction_date']),
            "z_score": float(row['z_score']),
            "expected_amount": float(row['avg_amount']),
            "deviation": float(abs(row['amount'] - row['avg_amount']))
        })
    
    return sorted(results, key=lambda x: abs(x['z_score']), reverse=True)[:50]

@app.get("/stats", dependencies=[Depends(verify_api_key)])
async def get_statistics():
    """Get database statistics"""
    stats = {}
    
    # Transaction stats
    tx_stats = conn.execute("""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT source_account) as unique_sources,
            COUNT(DISTINCT target_account) as unique_targets,
            SUM(amount) as total_volume,
            AVG(amount) as avg_transaction_size,
            MIN(transaction_date) as earliest_date,
            MAX(transaction_date) as latest_date
        FROM transactions
    """).fetchone()
    
    stats['transactions'] = {
        "total": tx_stats[0],
        "unique_sources": tx_stats[1],
        "unique_targets": tx_stats[2],
        "total_volume": float(tx_stats[3]) if tx_stats[3] else 0,
        "avg_size": float(tx_stats[4]) if tx_stats[4] else 0,
        "date_range": f"{tx_stats[5]} to {tx_stats[6]}"
    }
    
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)