# Run this to patch your API
import sys
sys.path.insert(0, '/workspaces/Neuro-genomic-AI')

# Backup original
import shutil
try:
    shutil.copy('src/api/main.py', 'src/api/main.py.backup')
    print("Backup created: src/api/main.py.backup")
except:
    pass

# Read main.py
with open('src/api/main.py', 'r') as f:
    content = f.read()

# Add missing endpoints if not present
if '/api/v1/status' not in content:
    # Find where to insert
    insert_point = content.find('app = FastAPI(')
    if insert_point == -1:
        insert_point = content.find('def create_app')
    
    new_routes = '''
# Dashboard health endpoints
@app.get("/api/v1/health")
@app.get("/api/health") 
async def dashboard_health():
    return {"status": "ok", "service": "neuro-genomic-ai"}

@app.get("/api/v1/status")
async def dashboard_status():
    return {
        "api_ok": True,
        "model_loaded": False,
        "inference_status": "idle",
        "system": {"status": "operational"}
    }

@app.post("/api/v1/upload")
async def mock_upload():
    return {"file_id": "test_123", "message": "Upload endpoint ready"}

@app.get("/api/v1/analysis/{file_id}")
async def mock_analysis(file_id: str):
    return {"file_id": file_id, "status": "pending"}
'''
    
    # Insert after app definition
    content = content.replace('app = FastAPI()', 'app = FastAPI()\n' + new_routes)
    
    with open('src/api/main.py', 'w') as f:
        f.write(content)
    print("Added missing endpoints to src/api/main.py")
else:
    print("Endpoints already exist")
