"""
InsiderEdge - Autonomous AI Crypto Trading Agent
Entry point for local execution and Vercel deployment
"""

# Vercel serverless function handler
def handler(request=None):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {"message": "InsiderEdge is running", "status": "ok"}
    }


# Local execution entry point
if __name__ == "__main__":
    import os
    os.environ.setdefault('PAPER_MODE', 'true')
    
    print("=" * 50)
    print("  InsiderEdge v1.0")
    print("  Autonomous AI Crypto Trading Agent")
    print("  Mode: PAPER TRADING")
    print("  Network: Sepolia Testnet")
    print("  Agent ID: 33")
    print("=" * 50)
    
    try:
        from agent import main
        main()
    except KeyboardInterrupt:
        print("\nAgent stopped.")
    except Exception as e:
        print(f"Error: {e}")