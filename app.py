from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database file
DB_FILE = 'data.json'

# ============ Database Helpers ============
def load_data():
    """Load all data from JSON file"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    """Save data to JSON file"""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_next_id():
    """Generate unique ID"""
    data = load_data()
    if not data:
        return 1
    try:
        max_id = max(int(item.get('id', 0)) for item in data if item.get('id'))
        return max_id + 1
    except:
        return len(data) + 1

# ============ API ENDPOINTS ============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Backend running on port 5000'}), 200

@app.route('/api/data', methods=['GET'])
def get_all_data():
    """Fetch all data"""
    try:
        data = load_data()
        return jsonify({'data': data, 'count': len(data)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['POST'])
def create_data():
    """Create new record"""
    try:
        item = request.get_json()
        
        # Validate JSON
        if not item:
            return jsonify({'error': 'No data provided'}), 400
        
        all_data = load_data()
        
        # Check limit
        if len(all_data) >= 999:
            return jsonify({'error': 'Database limit (999) reached'}), 400
        
        # Add unique ID
        item['id'] = str(get_next_id())
        item['__backendId'] = item['id']  # For SDK compatibility
        all_data.append(item)
        save_data(all_data)
        
        item_type = item.get('type', 'unknown')
        print(f"✅ Created {item_type}: ID {item['id']}")
        
        return jsonify({'success': True, 'data': item, 'id': item['id']}), 201
    except Exception as e:
        print(f"❌ Create Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/data/<item_id>', methods=['PUT'])
def update_data(item_id):
    """Update existing record"""
    try:
        new_data = request.get_json()
        
        if not new_data:
            return jsonify({'error': 'No data provided'}), 400
        
        all_data = load_data()
        
        for i, item in enumerate(all_data):
            if str(item.get('id')) == item_id or str(item.get('__backendId')) == item_id:
                # Preserve the ID
                new_data['id'] = item['id']
                new_data['__backendId'] = item['id']
                all_data[i] = new_data
                save_data(all_data)
                print(f"✅ Updated: ID {item_id}")
                return jsonify({'success': True, 'data': new_data}), 200
        
        return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        print(f"❌ Update Error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/data/<item_id>', methods=['DELETE'])
def delete_data(item_id):
    """Delete record"""
    try:
        all_data = load_data()
        
        for i, item in enumerate(all_data):
            if str(item.get('id')) == item_id or str(item.get('__backendId')) == item_id:
                deleted = all_data.pop(i)
                save_data(all_data)
                print(f"✅ Deleted: ID {item_id}")
                return jsonify({'success': True, 'data': deleted}), 200
        
        return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        print(f"❌ Delete Error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/', methods=['GET'])
def index():
    """Root route - backend is running"""
    return jsonify({
        'app': 'AR Car Rentals Backend',
        'status': 'running',
        'port': 5000,
        'api': 'http://localhost:5000/api',
        'endpoints': {
            'GET /api/health': 'Check backend status',
            'GET /api/data': 'Fetch all records',
            'POST /api/data': 'Create new record',
            'PUT /api/data/<id>': 'Update record',
            'DELETE /api/data/<id>': 'Delete record'
        }
    }), 200

# ============ ERROR HANDLERS ============
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============ START SERVER ============
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AR Car Rentals Backend - Flask Server")
    print("="*60)
    print("✅ Server running on: http://localhost:5000")
    print("📁 Database file: data.json (auto-created)")
    print("🔗 CORS enabled for frontend")
    print("🔌 API Base: http://localhost:5000/api")
    print("\n📋 Endpoints:")
    print("   GET  /api/health         → Health check")
    print("   GET  /api/data           → Fetch all data")
    print("   POST /api/data           → Create new record")
    print("   PUT  /api/data/<id>      → Update record")
    print("   DELETE /api/data/<id>    → Delete record")
    print("\n⏱️  Session: 30 minutes")
    print("💾 Limit: 999 records max")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=True)