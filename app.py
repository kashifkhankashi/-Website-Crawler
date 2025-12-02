"""
Flask web application for the website crawler.
Provides a user-friendly web interface for crawling websites.
"""
import os
import json
import csv
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit
import uuid

from crawl import CrawlerRunner

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'output'
# Configure SocketIO for Vercel (serverless-friendly)
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',  # Use threading mode for better serverless compatibility
    logger=False,
    engineio_logger=False
)

# Store active crawls
active_crawls: Dict[str, dict] = {}

# Add error handlers to ensure JSON responses (important for Vercel)
@app.errorhandler(404)
def not_found(error):
    """Return JSON for 404 errors."""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Return JSON for 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON for any unhandled exceptions."""
    return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/')
def index():
    """Main page with crawler form."""
    return render_template('index.html')


@app.route('/api/start-crawl', methods=['POST'])
def start_crawl():
    """Start a new crawl job."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json() or {}
        start_url = data.get('url', '').strip()
        max_depth = int(data.get('max_depth', 10))
        output_dir = data.get('output_dir', 'output')
        clear_cache = data.get('clear_cache', True)  # Clear cache by default
        
        if not start_url:
            return jsonify({'error': 'URL is required'}), 400
    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}'}), 400
    
    # Auto-fix URL (add https:// if missing)
    if not start_url.startswith(('http://', 'https://')):
        start_url = 'https://' + start_url
    
    # Clear HTTP cache if requested
    if clear_cache:
        cache_dir = os.path.join('httpcache', urlparse(start_url).netloc.replace('.', '_'))
        if os.path.exists('httpcache'):
            try:
                import shutil
                # Clear cache for this domain
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                # Or clear entire cache
                # shutil.rmtree('httpcache')
            except Exception as e:
                print(f"Warning: Could not clear cache: {e}")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create output directory for this job
    job_output_dir = os.path.join(output_dir, job_id)
    os.makedirs(job_output_dir, exist_ok=True)
    
    # Store crawl info
    active_crawls[job_id] = {
        'status': 'starting',
        'url': start_url,
        'max_depth': max_depth,
        'output_dir': job_output_dir,
        'progress': 0,
        'message': 'Initializing crawler...',
        'started_at': datetime.now().isoformat(),
        'pages_crawled': 0,
        'links_found': 0,
        'errors': []
    }
    
    # Start crawl in background thread
    thread = threading.Thread(
        target=run_crawl_async,
        args=(job_id, start_url, max_depth, job_output_dir),
        daemon=True
    )
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'status': 'started',
        'message': 'Crawl started successfully'
    })


def run_crawl_async(job_id: str, start_url: str, max_depth: int, output_dir: str):
    """Run crawl in background thread and emit progress updates."""
    try:
        # Update status - Initializing
        active_crawls[job_id]['status'] = 'initializing'
        active_crawls[job_id]['message'] = 'Initializing crawler...'
        active_crawls[job_id]['progress'] = 5
        
        socketio.emit('progress', {
            'job_id': job_id,
            'status': 'initializing',
            'message': 'Initializing crawler...',
            'progress': 5
        })
        
        import time
        time.sleep(0.5)  # Brief delay to show initialization
        
        # Update status - Starting crawl
        active_crawls[job_id]['status'] = 'crawling'
        active_crawls[job_id]['message'] = 'Starting to crawl website...'
        active_crawls[job_id]['progress'] = 10
        
        socketio.emit('progress', {
            'job_id': job_id,
            'status': 'crawling',
            'message': 'Starting to crawl website...',
            'progress': 10
        })
        
        # Run crawler in subprocess with progress tracking
        from crawl import CrawlerRunner
        
        # Track progress by monitoring output directory
        progress_file = os.path.join(output_dir, 'progress.json')
        
        runner = CrawlerRunner(
            start_url=start_url,
            max_depth=max_depth,
            output_dir=output_dir,
            use_subprocess=True,
            progress_file=progress_file,
            job_id=job_id
        )
        
        # Start progress monitoring thread
        def monitor_progress():
            last_pages = 0
            max_iterations = 3600  # Max 1 hour
            iteration = 0
            while active_crawls[job_id]['status'] in ['crawling', 'initializing', 'processing'] and iteration < max_iterations:
                try:
                    # Check if progress file exists and read it
                    if os.path.exists(progress_file):
                        with open(progress_file, 'r') as f:
                            progress_data = json.load(f)
                            pages = progress_data.get('pages_crawled', 0)
                            links = progress_data.get('links_found', 0)
                            
                            if pages > last_pages or pages > 0:
                                # Calculate progress: 10-60% for crawling
                                estimated_total = max(20, pages * 2)  # Estimate based on current pages
                                crawl_progress = min(60, 10 + (pages / estimated_total) * 50)
                                
                                active_crawls[job_id]['pages_crawled'] = pages
                                active_crawls[job_id]['links_found'] = links
                                active_crawls[job_id]['progress'] = int(crawl_progress)
                                active_crawls[job_id]['message'] = f'Crawling... Found {pages} pages, {links} links'
                                
                                socketio.emit('progress', {
                                    'job_id': job_id,
                                    'status': 'crawling',
                                    'message': f'Crawling... Found {pages} pages, {links} links',
                                    'progress': int(crawl_progress),
                                    'pages_crawled': pages,
                                    'links_found': links
                                })
                                
                                last_pages = pages
                except Exception as e:
                    pass
                iteration += 1
                time.sleep(1)  # Check every second
        
        monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        monitor_thread.start()
        
        # Run the crawl
        runner.run()
        
        # Update status - Processing
        active_crawls[job_id]['status'] = 'processing'
        active_crawls[job_id]['message'] = 'Processing results and checking links...'
        active_crawls[job_id]['progress'] = 70
        
        socketio.emit('progress', {
            'job_id': job_id,
            'status': 'processing',
            'message': 'Processing results and checking links...',
            'progress': 70
        })
        
        time.sleep(0.5)
        
        # Update status - Generating reports
        active_crawls[job_id]['status'] = 'generating'
        active_crawls[job_id]['message'] = 'Generating reports...'
        active_crawls[job_id]['progress'] = 90
        
        socketio.emit('progress', {
            'job_id': job_id,
            'status': 'generating',
            'message': 'Generating reports...',
            'progress': 90
        })
        
        # Update status - Completed
        active_crawls[job_id]['status'] = 'completed'
        active_crawls[job_id]['message'] = 'Crawl completed successfully!'
        active_crawls[job_id]['progress'] = 100
        active_crawls[job_id]['completed_at'] = datetime.now().isoformat()
        active_crawls[job_id]['pages_crawled'] = len(runner.crawled_items)
        active_crawls[job_id]['output_files'] = {
            'json': os.path.join(output_dir, 'report.json'),
            'csv': os.path.join(output_dir, 'summary.csv'),
            'sitemap': os.path.join(output_dir, 'sitemap.txt')
        }
        
        socketio.emit('progress', {
            'job_id': job_id,
            'status': 'completed',
            'message': 'Crawl completed successfully!',
            'progress': 100,
            'pages_crawled': len(runner.crawled_items),
            'links_found': len(runner.all_internal_links)
        })
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        
        active_crawls[job_id]['status'] = 'error'
        active_crawls[job_id]['message'] = f'Error: {error_msg}'
        if 'errors' not in active_crawls[job_id]:
            active_crawls[job_id]['errors'] = []
        active_crawls[job_id]['errors'].append(error_msg)
        
        socketio.emit('progress', {
            'job_id': job_id,
            'status': 'error',
            'message': f'Error: {error_msg}',
            'progress': 0
        })


@app.route('/api/crawl-status/<job_id>')
def get_crawl_status(job_id: str):
    """Get status of a crawl job."""
    try:
        # Debug logging (can be removed in production)
        if job_id not in active_crawls:
            print(f"Job {job_id} not in active_crawls. Active jobs: {list(active_crawls.keys())[:3]}")
        
        if job_id not in active_crawls:
            # Check if results exist (crawl might have completed before)
            json_path = os.path.join('output', job_id, 'report.json')
            if os.path.exists(json_path):
                return jsonify({
                    'status': 'completed',
                    'message': 'Crawl completed (results found)',
                    'job_id': job_id,
                    'progress': 100
                })
            
            # Also check default output location
            default_json_path = os.path.join('output', 'report.json')
            if os.path.exists(default_json_path):
                return jsonify({
                    'status': 'completed',
                    'message': 'Crawl completed (results found in default location)',
                    'job_id': job_id,
                    'progress': 100
                })
            
            # Return a status indicating job not found
            return jsonify({
                'status': 'not_found',
                'message': f'Job {job_id} not found. It may have been removed or never started properly.',
                'job_id': job_id,
                'error': True,
                'suggestion': 'Please try starting a new crawl.'
            })
        
        # Return current status
        crawl_info = active_crawls[job_id]
        return jsonify({
            'job_id': job_id,
            'status': crawl_info.get('status', 'unknown'),
            'progress': crawl_info.get('progress', 0),
            'message': crawl_info.get('message', ''),
            'pages_crawled': crawl_info.get('pages_crawled', 0),
            'links_found': crawl_info.get('links_found', 0)
        })
    except Exception as e:
        return jsonify({
            'error': f'Error getting crawl status: {str(e)}',
            'job_id': job_id
        }), 500


@app.route('/api/crawl-results/<job_id>')
def get_crawl_results(job_id: str):
    """Get results of a completed crawl."""
    try:
        json_path = None
        
        # First, try to get path from active_crawls
        if job_id in active_crawls:
            crawl_info = active_crawls[job_id]
            if crawl_info['status'] != 'completed':
                return jsonify({'error': 'Crawl not completed yet'}), 400
            json_path = crawl_info.get('output_files', {}).get('json')
        
        # If not in active_crawls or path not found, try to find the file directly
        if not json_path or not os.path.exists(json_path):
            # Try different possible locations
            possible_paths = [
                os.path.join('output', job_id, 'report.json'),
                os.path.join('output', 'report.json'),  # Fallback to default output
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    json_path = path
                    break
        
        # Load JSON report if found
        if json_path and os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                return jsonify(report_data)
            except json.JSONDecodeError as e:
                return jsonify({'error': f'Invalid JSON file: {str(e)}'}), 500
            except Exception as e:
                return jsonify({'error': f'Error reading results: {str(e)}'}), 500
        
        # If job_id is 'default', try the default output location
        if job_id == 'default':
            default_path = os.path.join('output', 'report.json')
            if os.path.exists(default_path):
                try:
                    with open(default_path, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    return jsonify(report_data)
                except Exception as e:
                    return jsonify({'error': f'Error reading default results: {str(e)}'}), 500
        
        return jsonify({'error': 'Results not found. The crawl may not have completed or the results were deleted.'}), 404
    except Exception as e:
        return jsonify({'error': f'Error loading results: {str(e)}'}), 500


@app.route('/api/download/<job_id>/<file_type>')
def download_file(job_id: str, file_type: str):
    """Download crawl results file."""
    file_path = None
    
    # First, try to get path from active_crawls
    if job_id in active_crawls:
        crawl_info = active_crawls[job_id]
        output_files = crawl_info.get('output_files', {})
        file_path = output_files.get(file_type)
    
    # If not in active_crawls or path not found, try to find the file directly
    if not file_path or not os.path.exists(file_path):
        # Map file types to filenames
        file_names = {
            'json': 'report.json',
            'csv': 'summary.csv',
            'sitemap': 'sitemap.txt'
        }
        
        filename = file_names.get(file_type)
        if not filename:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Try different possible locations
        possible_paths = [
            os.path.join('output', job_id, filename),
            os.path.join('output', filename),  # Fallback to default output
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)


@app.route('/results/<job_id>')
def results_page(job_id: str):
    """Display results page for a crawl job."""
    # Always render the page - let JavaScript handle missing results gracefully
    return render_template('results.html', job_id=job_id)


@app.route('/api/list-jobs')
def list_jobs():
    """List all available crawl jobs (results that exist)."""
    jobs = []
    
    # Check active crawls
    for job_id, crawl_info in active_crawls.items():
        jobs.append({
            'job_id': job_id,
            'url': crawl_info.get('url', ''),
            'status': crawl_info.get('status', 'unknown'),
            'started_at': crawl_info.get('started_at', ''),
            'pages_crawled': crawl_info.get('pages_crawled', 0)
        })
    
    # Also check for completed jobs in output directory
    output_dir = 'output'
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path):
                # Check if it's a job directory with results
                json_path = os.path.join(item_path, 'report.json')
                if os.path.exists(json_path):
                    # Check if already in active_crawls
                    if not any(j['job_id'] == item for j in jobs):
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                report_data = json.load(f)
                            jobs.append({
                                'job_id': item,
                                'url': report_data.get('pages', [{}])[0].get('url', '') if report_data.get('pages') else '',
                                'status': 'completed',
                                'started_at': report_data.get('crawl_date', ''),
                                'pages_crawled': report_data.get('total_pages', 0)
                            })
                        except:
                            pass
    
    return jsonify({'jobs': jobs})


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    emit('connected', {'message': 'Connected to crawler server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    pass


if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Run Flask app with SocketIO
    print("\n" + "="*60)
    print("Website Crawler - Web Interface")
    print("="*60)
    print("\nStarting server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

