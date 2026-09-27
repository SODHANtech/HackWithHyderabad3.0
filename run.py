import uvicorn
from backend.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting VoiceCraft AI - Autonomous Website Builder")
    print(f"🧠 Hindsight Memory Bank: {settings.hindsight_bank_id}")
    print(f"🌐 Dashboard URL: http://localhost:{settings.port}")
    print("=" * 60)
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=True)
