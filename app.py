import os
from app import create_app

app = create_app()

@app.route("/")
def home():
    return {
        "project": "MoveMate",
        "status": "Backend Running Successfully 🚀",
        "version": "2.0"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
