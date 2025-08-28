#!/usr/bin/env python3
"""
Development server runner that starts both FastAPI and Celery worker
"""
import subprocess
import sys
import signal
import os
from multiprocessing import Process
import time


def run_fastapi():
    """Run FastAPI server"""
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "src.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ]
    subprocess.run(cmd)


def run_celery():
    """Run Celery worker"""
    cmd = [
        sys.executable, "-m", "celery", 
        "-A", "src.tasks.celery", 
        "worker", 
        "--loglevel=info", 
        "--pool=solo"
    ]
    subprocess.run(cmd)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n\nShutting down services...')
    sys.exit(0)


def main():
    """Main function to start both processes"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Starting Contract Intelligence Parser Development Server")
    print("=" * 60)
    print("📡 FastAPI Server: http://0.0.0.0:8000")
    print("⚙️  Celery Worker: Processing contracts asynchronously")
    print("=" * 60)
    print("Press Ctrl+C to stop both services\n")
    
    # Start FastAPI process
    fastapi_process = Process(target=run_fastapi, name="FastAPI-Server")
    
    # Start Celery process  
    celery_process = Process(target=run_celery, name="Celery-Worker")
    
    try:
        fastapi_process.start()
        time.sleep(2)  # Give FastAPI time to start
        celery_process.start()
        
        # Wait for both processes
        fastapi_process.join()
        celery_process.join()
        
    except KeyboardInterrupt:
        print("\n\nReceived interrupt signal. Shutting down...")
    finally:
        # Terminate processes
        if fastapi_process.is_alive():
            fastapi_process.terminate()
            fastapi_process.join(timeout=5)
            if fastapi_process.is_alive():
                fastapi_process.kill()
                
        if celery_process.is_alive():
            celery_process.terminate()
            celery_process.join(timeout=5)
            if celery_process.is_alive():
                celery_process.kill()
        
        print("✅ All services stopped successfully")


if __name__ == "__main__":
    main()
