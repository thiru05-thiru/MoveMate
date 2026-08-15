import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    # Must bind to 0.0.0.0 for Render to detect the service
    app.run(host="0.0.0.0", port=port)
