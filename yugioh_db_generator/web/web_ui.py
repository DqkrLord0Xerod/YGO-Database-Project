"""Web interface for the Yu-Gi-Oh! Card Database Generator."""

import os
import sys
import json
import tempfile
from typing import List, Dict, Any
import traceback

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify

# Add parent directory to path to import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yugioh_db_generator.api.card_api import YGOPRODeckAPI
from yugioh_db_generator.core.card_database import CardDatabaseGenerator
from yugioh_db_generator.utils.logging_utils import setup_logging

# Set up logging
logger = setup_logging()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages

# Create cache directory
cache_dir = os.path.join(tempfile.gettempdir(), "yugioh_db_generator_web_cache")
os.makedirs(cache_dir, exist_ok=True)
logger.info(f"Using cache directory: {cache_dir}")

# Global variables to store processing state
current_progress = {
    "total": 0,
    "processed": 0,
    "found": 0,
    "corrected": 0,
    "not_found": 0,
    "status": "idle"  # idle, processing, done, error
}

# Store recent generations for download
recent_outputs = []


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """Handle database generation request."""
    try:
        # Reset progress
        global current_progress
        current_progress = {
            "total": 0,
            "processed": 0,
            "found": 0,
            "corrected": 0,
            "not_found": 0,
            "status": "processing"
        }
        
        # Get form data
        card_list = request.form.get('card_list', '').strip()
        output_format = request.form.get('output_format', 'markdown')
        thread_count = int(request.form.get('thread_count', 4))
        use_cache = 'use_cache' in request.form
        
        # Convert text area to card list
        deck_list = [line.strip() for line in card_list.split('\n') if line.strip() and not line.strip().startswith('#')]
        current_progress['total'] = len(deck_list)
        
        if not deck_list:
            flash('Please enter at least one card name', 'error')
            current_progress['status'] = 'error'
            return redirect(url_for('index'))
            
        # Create temporary files
        fd, output_file = tempfile.mkstemp(suffix=f'.{get_file_extension(output_format)}')
        os.close(fd)
        
        fd, corrections_file = tempfile.mkstemp(suffix='.txt')
        os.close(fd)
        
        # Create a generator with progress tracking
        generator = CardDatabaseGenerator(
            output_file=output_file,
            output_format=output_format,
            max_workers=thread_count,
            cache_dir=cache_dir,
            use_cache=use_cache
        )
        
        # Monkey patch the process card method to track progress
        original_process_card = generator._process_card
        
        def process_card_with_tracking(card_name, current, total):
            try:
                result = original_process_card(card_name, current, total)
                current_progress['processed'] += 1
                if result:
                    if card_name in generator.search_engine.correction_map:
                        current_progress['corrected'] += 1
                    else:
                        current_progress['found'] += 1
                else:
                    current_progress['not_found'] += 1
                return result
            except Exception as e:
                logger.error(f"Error processing card '{card_name}': {e}")
                current_progress['not_found'] += 1
                return None
        
        generator._process_card = process_card_with_tracking
        
        # Generate the database
        try:
            generator.generate_database(deck_list)
            
            # Get name corrections and write to file
            corrections = generator.get_name_corrections()
            with open(corrections_file, 'w', encoding='utf-8') as f:
                f.write("# Yu-Gi-Oh! Card Name Corrections\n")
                f.write("# Original Name -> Corrected Name\n\n")
                for original, corrected in sorted(corrections.items()):
                    f.write(f"{original} -> {corrected}\n")
            
            # Store the output files for download
            global recent_outputs
            recent_outputs.append({
                'id': len(recent_outputs) + 1,
                'output_file': output_file,
                'output_format': output_format,
                'corrections_file': corrections_file,
                'card_count': len(deck_list),
                'corrections_count': len(corrections)
            })
            
            # Limit the number of stored outputs
            if len(recent_outputs) > 10:
                old_output = recent_outputs.pop(0)
                try:
                    os.remove(old_output['output_file'])
                    os.remove(old_output['corrections_file'])
                except:
                    pass
            
            current_progress['status'] = 'done'
            
            flash('Database generated successfully!', 'success')
            return redirect(url_for('results'))
            
        except Exception as e:
            logger.error(f"Error generating database: {traceback.format_exc()}")
            current_progress['status'] = 'error'
            flash(f'Error generating database: {str(e)}', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Unexpected error: {traceback.format_exc()}")
        current_progress['status'] = 'error'
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('index'))

# yugioh_db_generator/web/web_ui.py

# Add this new route
@app.route('/analyzer')
def analyzer():
    """Render the deck analyzer page."""
    return render_template('analyzer.html')

# Add API endpoints for deck analysis
@app.route('/api/analyze-deck', methods=['POST'])
def analyze_deck_api():
    """API endpoint for analyzing a deck."""
    try:
        # Get deck list from request
        deck_list = request.json.get('deckList', '')
        
        # Parse the deck list
        main_deck, extra_deck = [], []
        current_section = 'main'
        
        for line in deck_list.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                if 'extra' in line.lower():
                    current_section = 'extra'
                continue
            
            if current_section == 'main':
                main_deck.append(line)
            else:
                extra_deck.append(line)
        
        # Use the DeckStrengthAnalyzer to analyze the deck
        from yugioh_db_generator.ai.deck_analyzer import DeckStrengthAnalyzer
        
        # Get card data
        from yugioh_db_generator.api.card_api import YGOPRODeckAPI
        api_client = YGOPRODeckAPI(cache_dir=cache_dir, use_cache=True)
        
        # Fetch card data for the deck
        card_data = {}
        all_cards = main_deck + extra_deck
        for card_name in all_cards:
            try:
                card_info = api_client.get_card_by_name(card_name)
                if card_info:
                    card_data[card_name] = card_info
            except Exception as e:
                logger.error(f"Error fetching card data for {card_name}: {e}")
        
        # Initialize the analyzer
        analyzer = DeckStrengthAnalyzer()
        
        # Analyze the deck
        analysis_results = analyzer.analyze_deck(deck_list, card_data)
        
        # Return analysis results as JSON
        return jsonify({
            'success': True,
            'analysis': analysis_results,
            'card_data': card_data
        })
    
    except Exception as e:
        logger.error(f"Error analyzing deck: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/card-image/<card_name>')
def card_image(card_name):
    """API endpoint for getting a card image URL."""
    try:
        # This would normally fetch from an API, but for demo we'll return a placeholder
        return jsonify({
            'success': True,
            'image_url': f"https://ygoprodeck.com/pics/{card_name.replace(' ', '%20')}.jpg"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@app.route('/api/card-details/<card_name>')
def card_details(card_name):
    """API endpoint for getting detailed card information."""
    try:
        # Create API client
        api_client = YGOPRODeckAPI(cache_dir=cache_dir, use_cache=True)
        
        # Get card information
        card_info = api_client.get_card_by_name(card_name)
        
        if card_info:
            # Get rulings for the card
            from yugioh_db_generator.ai.rule_generator import AIRuleGenerator
            
            rule_generator = AIRuleGenerator()
            rulings = rule_generator.generate_rulings(card_name, card_info)
            
            return jsonify({
                'success': True,
                'card': card_info,
                'rulings': rulings
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Card not found: {card_name}"
            }), 404
    except Exception as e:
        logger.error(f"Error getting card details: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    
@app.route('/progress')
def progress():
    """Return the current progress as JSON."""
    return jsonify(current_progress)

@app.route('/analyzer')
def deck_analyzer():  # Changed function name from analyzer to deck_analyzer
    """Show the deck analyzer page."""
    return render_template('analyzer.html')

@app.route('/results')
def results():
    """Show the results of the database generation."""
    return render_template('results.html', outputs=recent_outputs)


@app.route('/download/<int:output_id>/<file_type>')
def download(output_id, file_type):
    """Download a generated file."""
    try:
        # Find the requested output
        output = None
        for out in recent_outputs:
            if out['id'] == output_id:
                output = out
                break
        
        if not output:
            flash('File not found', 'error')
            return redirect(url_for('results'))
        
        # Determine which file to download
        if file_type == 'database':
            filename = f"yugioh_database.{get_file_extension(output['output_format'])}"
            file_path = output['output_file']
        elif file_type == 'corrections':
            filename = "card_name_corrections.txt"
            file_path = output['corrections_file']
        else:
            flash('Invalid file type', 'error')
            return redirect(url_for('results'))
        
        # Send the file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('results'))


@app.route('/example')
def example():
    """Load an example deck list."""
    from yugioh_db_generator.utils.file_utils import get_default_deck_list
    deck_list = get_default_deck_list()
    return jsonify({'deck_list': '\n'.join(deck_list)})


def get_file_extension(output_format):
    """Get the file extension for an output format."""
    extensions = {
        'markdown': 'md',
        'json': 'json',
        'csv': 'csv',
        'text': 'txt'
    }
    return extensions.get(output_format, 'txt')


if __name__ == '__main__':
    # Start the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
