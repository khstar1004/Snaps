from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_talisman import Talisman
from flask_sqlalchemy import SQLAlchemy
from SnapsAI import InstagramAPI, convert_post, RAGConverter
import os
from dotenv import load_dotenv
import logging
import hashlib
import hmac
import base64
import json

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Define a custom CSP that allows inline styles and scripts
csp = {
    'default-src': "'self'",
    'style-src': "'self' 'unsafe-inline'",
    'script-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
    'img-src': "'self' *.cdninstagram.com *.fbcdn.net data: https://i.ibb.co",
}


Talisman(app, force_https=True, content_security_policy=csp)

# Database configuration for MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://instauser:3094@localhost/instagram_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Environment variables
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')
NGROK_URL = os.getenv('NGROK_URL')
INSTAGRAM_APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET')

instagram_api = InstagramAPI(INSTAGRAM_ACCESS_TOKEN)

# User model definition
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instagram_id = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    access_token = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/instagram-converter')
def instagram_converter():
    return render_template('index6.html')

@app.route('/content-conversion')
def content_conversion():
    return render_template('content_conversion.html')

@app.route('/content-management')
def content_management():
    return render_template('content_management.html')

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/my-page')
def my_page():
    return render_template('my_page.html')

@app.route('/fetch_posts', methods=['POST'])
def fetch_posts():
    app.logger.debug("Fetching posts...")
    try:
        media_items = instagram_api.get_user_media()
        app.logger.debug(f"Media items fetched: {media_items}")
        formatted_posts = instagram_api.format_posts(media_items)
        app.logger.debug(f"Formatted posts: {formatted_posts}")
        return jsonify({"posts": formatted_posts})
    except Exception as e:
        app.logger.error(f"Error fetching posts: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        app.logger.info(f"Received data: {data}")
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        caption = data.get('caption')
        target_platform = data.get('targetPlatform')
        has_image = data.get('hasImage', False)

        if not caption or not target_platform:
            return jsonify({"error": "Missing required fields"}), 400

        # 기본 변환
        basic_converted_post = convert_post(caption, target_platform, has_image)
        app.logger.info(f"Basic converted post: {basic_converted_post}")

        # RAG 변환
        rag_converter = RAGConverter()
        rag_converted_post = rag_converter.generate_enhanced_post(caption, target_platform, has_image)
        app.logger.info(f"RAG converted post: {rag_converted_post}")

        return jsonify({
            "basicConvertedPost": basic_converted_post,
            "ragConvertedPost": rag_converted_post
        })
    except Exception as e:
        app.logger.error(f"Error in /convert route: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/fetch_instagram_stats', methods=['GET'])
def fetch_instagram_stats():
    try:
        stats = instagram_api.get_user_statistics(limit=30)  # 최근 30개 게시물 기준
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"Error fetching Instagram stats: {str(e)}")
        return jsonify({"error": "통계를 가져오는 데 실패했습니다. 잠시 후 다시 시도해주세요."}), 500

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Internal Server Error: {str(e)}")
    return render_template('500.html'), 500

# ... (기타 라우트 및 함수들)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 데이터베이스 테이블 생성

    if NGROK_URL:
        app.logger.info(f"ngrok URL: {NGROK_URL}")
        app.logger.info(f"Callback URL: {NGROK_URL}/auth/instagram/callback")
        app.logger.info(f"Data Deletion URL: {NGROK_URL}/data-deletion")
        app.logger.info(f"Privacy Policy URL: {NGROK_URL}/privacy-policy")

    app.run(host='0.0.0.0', port=5000, debug=True)