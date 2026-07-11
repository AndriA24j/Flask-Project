from ext import app
import routes
app.register_blueprint(routes.profile_bp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)