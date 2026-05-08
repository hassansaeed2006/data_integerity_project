from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from config import config
import os
from auth_routes import auth_bp
from document_routes import doc_bp
from admin_routes import admin_bp

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'assets'))
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(doc_bp)
    app.register_blueprint(admin_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Serve frontend
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/assets/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)
    
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cert_path = os.path.join(base_dir, 'certificates', 'cert.pem')
    key_path = os.path.join(base_dir, 'certificates', 'key.pem')
    
    # Enforce HTTPS for secure communication requirement.
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        raise FileNotFoundError(
            f"HTTPS certificate files not found. Expected:\n- {cert_path}\n- {key_path}"
        )

    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=(cert_path, key_path),
        debug=False
    )
