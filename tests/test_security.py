import pytest
from app import app
import html

def test_xss_protection(client):
    """Test XSS protection in templates"""
    rv = client.get('/products?category=<script>alert("xss")</script>')
    assert b'<script>' not in rv.data

def test_sql_injection_protection(client):
    """Test SQL injection protection (though using no SQL)"""
    rv = client.get('/products?category=1\' OR \'1\'=\'1')
    assert rv.status_code == 200

def test_session_security(client):
    """Test session security settings"""
    rv = client.get('/')
    cookie = client.get_cookie('session')
    if cookie:
        assert cookie.get('httponly', False)
        assert cookie.get('secure', False)