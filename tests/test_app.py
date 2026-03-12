import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test the home page loads"""
    rv = client.get('/')
    assert rv.status_code == 200

def test_products_page(client):
    """Test the products page loads"""
    rv = client.get('/products')
    assert rv.status_code == 200

def test_cart_page(client):
    """Test the cart page loads"""
    rv = client.get('/cart')
    assert rv.status_code == 200

def test_health_endpoint(client):
    """Test health check endpoint"""
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.json['status'] == 'healthy'

def test_api_products(client):
    """Test products API endpoint"""
    rv = client.get('/api/products')
    assert rv.status_code == 200
    assert isinstance(rv.json, list)

def test_add_to_cart(client):
    """Test adding item to cart"""
    rv = client.get('/add-to-cart/1')
    assert rv.status_code == 200
    assert rv.json['success'] == True