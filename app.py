from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
import os
import logging
from datetime import timedelta
import uuid

app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample products data
PRODUCTS = [
    {
        'id': '1',
        'name': 'MacBook Pro 16"',
        'price': 2499.99,
        'description': 'Apple M2 Pro chip, 16GB RAM, 512GB SSD',
        'image': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500',
        'category': 'Laptops'
    },
    {
        'id': '2',
        'name': 'iPhone 15 Pro Max',
        'price': 1199.99,
        'description': '6.7" Super Retina XDR display, 256GB',
        'image': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500',
        'category': 'Phones'
    },
    {
        'id': '3',
        'name': 'Sony WH-1000XM5',
        'price': 399.99,
        'description': 'Wireless Noise Cancelling Headphones',
        'image': 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500',
        'category': 'Audio'
    },
    {
        'id': '4',
        'name': 'iPad Pro 12.9"',
        'price': 1099.99,
        'description': 'M2 chip, Liquid Retina XDR display, 256GB',
        'image': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500',
        'category': 'Tablets'
    },
    {
        'id': '5',
        'name': 'Samsung 49" Odyssey G9',
        'price': 1399.99,
        'description': 'DQHD, 240Hz, 1ms, Curved Gaming Monitor',
        'image': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500',
        'category': 'Monitors'
    },
    {
        'id': '6',
        'name': 'Logitech MX Master 3S',
        'price': 99.99,
        'description': 'Wireless Performance Mouse',
        'image': 'https://images.unsplash.com/photo-1625723044792-44de16ccb4e9?w=500',
        'category': 'Accessories'
    }
]

# Routes
@app.route('/')
def index():
    """Home page"""
    try:
        return render_template('index.html', products=PRODUCTS[:3])
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        return "Welcome to TechStore 2026! <a href='/products'>View Products</a>"

@app.route('/products')
def products():
    """Products page"""
    try:
        category = request.args.get('category')
        if category:
            filtered_products = [p for p in PRODUCTS if p['category'].lower() == category.lower()]
        else:
            filtered_products = PRODUCTS
        return render_template('products.html', products=filtered_products)
    except Exception as e:
        logger.error(f"Error rendering products page: {e}")
        return "<h1>Products</h1><p>Unable to load products. Please try again.</p>"

@app.route('/cart')
def cart():
    """Cart page"""
    try:
        cart_items = session.get('cart', [])
        cart_products = []
        total = 0
        
        for item_id in cart_items:
            product = next((p for p in PRODUCTS if p['id'] == item_id), None)
            if product:
                cart_products.append(product)
                total += product['price']
        
        return render_template('cart.html', cart_items=cart_products, total=total)
    except Exception as e:
        logger.error(f"Error rendering cart page: {e}")
        return "<h1>Shopping Cart</h1><p>Unable to load cart. Please try again.</p>"

@app.route('/add-to-cart/<product_id>')
def add_to_cart(product_id):
    """Add item to cart"""
    try:
        if 'cart' not in session:
            session['cart'] = []
        
        session['cart'].append(product_id)
        session.modified = True
        
        return jsonify({
            'success': True, 
            'cart_count': len(session['cart']),
            'message': 'Item added to cart successfully'
        })
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return jsonify({
            'success': False, 
            'message': 'Failed to add item to cart'
        }), 500

@app.route('/remove-from-cart/<product_id>')
def remove_from_cart(product_id):
    """Remove item from cart"""
    try:
        if 'cart' in session:
            session['cart'] = [item for item in session['cart'] if item != product_id]
            session.modified = True
        
        return redirect(url_for('cart'))
    except Exception as e:
        logger.error(f"Error removing from cart: {e}")
        return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    """Checkout page"""
    try:
        cart_items = session.get('cart', [])
        if not cart_items:
            return redirect(url_for('products'))
        
        total = sum([next((p['price'] for p in PRODUCTS if p['id'] == item_id), 0) for item_id in cart_items])
        return render_template('checkout.html', total=total)
    except Exception as e:
        logger.error(f"Error rendering checkout page: {e}")
        return redirect(url_for('cart'))

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': os.environ.get('FLASK_ENV', 'development')
    })

@app.route('/api/products')
def api_products():
    """API endpoint for products"""
    return jsonify(PRODUCTS)

@app.route('/api/cart')
def api_cart():
    """API endpoint for cart"""
    cart_items = session.get('cart', [])
    cart_details = []
    
    for item_id in cart_items:
        product = next((p for p in PRODUCTS if p['id'] == item_id), None)
        if product:
            cart_details.append(product)
    
    return jsonify({
        'items': cart_details,
        'count': len(cart_items),
        'total': sum(item['price'] for item in cart_details)
    })

@app.route('/clear-cart')
def clear_cart():
    """Clear all items from cart"""
    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204  # No content response

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors gracefully"""
    logger.warning(f"404 error: {request.path}")
    try:
        return render_template('404.html'), 404
    except:
        # Fallback HTML if template is missing
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 - Page Not Found | TechStore 2026</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
                .container { max-width: 600px; padding: 40px; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px); }
                h1 { font-size: 6rem; margin: 0; line-height: 1; }
                h2 { margin: 20px 0; }
                a { color: white; text-decoration: none; padding: 10px 20px; border: 2px solid white; border-radius: 5px; margin: 10px; display: inline-block; }
                a:hover { background: white; color: #667eea; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404</h1>
                <h2>Page Not Found</h2>
                <p>The page you're looking for doesn't exist or has been moved.</p>
                <div>
                    <a href="/">Go Home</a>
                    <a href="/products">Browse Products</a>
                </div>
            </div>
        </body>
        </html>
        ''', 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors gracefully"""
    logger.error(f'Server Error: {error}')
    try:
        return render_template('500.html'), 500
    except:
        # Fallback HTML if template is missing
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>500 - Server Error | TechStore 2026</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
                .container { max-width: 600px; padding: 40px; background: rgba(255,255,255,0.1); border-radius: 10px; backdrop-filter: blur(10px); }
                h1 { font-size: 6rem; margin: 0; line-height: 1; }
                h2 { margin: 20px 0; }
                a { color: white; text-decoration: none; padding: 10px 20px; border: 2px solid white; border-radius: 5px; margin: 10px; display: inline-block; }
                a:hover { background: white; color: #667eea; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>500</h1>
                <h2>Internal Server Error</h2>
                <p>Something went wrong on our end. We're working to fix it as soon as possible.</p>
                <div>
                    <a href="/">Go Home</a>
                    <a href="/products">Browse Products</a>
                </div>
            </div>
        </body>
        </html>
        ''', 500

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(429)
def ratelimit_error(error):
    """Handle rate limit errors"""
    return jsonify({'error': 'Too many requests'}), 429

# Before request handlers
@app.before_request
def before_request():
    """Actions to perform before each request"""
    # Set secure headers
    if request.is_secure:
        pass  # Add secure headers logic here
    
    # Log requests in debug mode
    if app.debug:
        logger.debug(f"Request: {request.method} {request.path}")

# After request handlers
@app.after_request
def after_request(response):
    """Add security headers to all responses"""
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' https: data:;"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

# CLI commands
@app.cli.command('init-db')
def init_db_command():
    """Initialize the database (placeholder)"""
    logger.info('Initialized the database')

# Context processors
@app.context_processor
def utility_processor():
    """Add utility functions to template context"""
    def get_cart_count():
        return len(session.get('cart', []))
    
    return dict(
        get_cart_count=get_cart_count,
        app_name="TechStore 2026",
        current_year=__import__('datetime').datetime.now().year
    )

# Template filters
@app.template_filter('currency')
def currency_filter(value):
    """Format value as currency"""
    try:
        return f"${value:,.2f}"
    except:
        return value

@app.template_filter('pluralize')
def pluralize_filter(number, singular='', plural='s'):
    """Return plural or singular suffix based on number"""
    return singular if number == 1 else plural

# Initialize app
if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run in debug mode only in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting TechStore 2026 application on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode
    )