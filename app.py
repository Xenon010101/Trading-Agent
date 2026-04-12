"""
InsiderEdge - Autonomous AI Crypto Trading Agent
Entry point for local execution and Vercel deployment
"""
import os

os.environ.setdefault('PAPER_MODE', 'true')

# Vercel serverless function handler
def app(environ, start_response):
    """WSGI app for Vercel"""
    status = '200 OK'
    headers = [('Content-Type', 'application/json')]
    start_response(status, headers)
    return [b'{"status": "ok", "message": "InsiderEdge running"}']


# Handler for serverless
def handler(request=None):
    """Vercel Python handler"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {"message": "InsiderEdge is running", "status": "ok"}
    }


# Local execution
def run():
    """Run the agent locally"""
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


if __name__ == "__main__":
    run()