#!/usr/bin/env python3
"""
Test script to debug knowledge base search issues
"""
import asyncio
import requests
import json

async def test_search():
    """Test different search queries to see what content is found"""
    
    base_url = "http://localhost:8001/api/ai/knowledge/search"
    
    test_queries = [
        "How do I start the AutoBoss machine?",
        "Step 3 Pre-operation Check and Warm-Up",
        "turn on master switch",
        "Section 8 Step 3",
        "startup procedure",
        "Pre-operation Check",
        "Warm-Up",
        "master switch PLC",
        "Attach umbilical hose",
        "start up via remote control"
    ]
    
    print("Testing knowledge base search with different queries...\n")
    
    for query in test_queries:
        print(f"=== QUERY: '{query}' ===")
        
        try:
            response = requests.post(base_url, json={
                "query": query,
                "limit": 3
            })
            
            if response.status_code == 200:
                results = response.json()
                print(f"Found {len(results)} results")
                
                for i, result in enumerate(results):
                    doc = result['document']
                    content = result['matched_content']
                    score = result['relevance_score']
                    
                    print(f"\nResult {i+1} (Score: {score:.4f}):")
                    print(f"Title: {doc['title']}")
                    print(f"Content preview: {content[:200]}...")
                    
                    # Check if this contains startup instructions
                    if any(keyword in content.lower() for keyword in ['turn on master switch', 'step 3', 'pre-operation', 'warm-up']):
                        print("*** CONTAINS STARTUP CONTENT ***")
                        print(f"Full content: {content}")
                        
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")
            
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_search())