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
    app.run(debug=True)