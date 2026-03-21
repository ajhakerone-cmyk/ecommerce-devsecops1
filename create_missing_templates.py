import os

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# 404.html content
four_oh_four = '''{% extends "base.html" %}

{% block title %}Page Not Found - TechStore 2026{% endblock %}

{% block content %}
<section class="error-page">
    <div class="error-container">
        <div class="error-code">404</div>
        <h1 class="error-title">Page Not Found</h1>
        <p class="error-message">Oops! The page you're looking for doesn't exist or has been moved.</p>
        <div class="error-actions">
            <a href="/" class="btn-primary">
                <i class="fas fa-home"></i> Back to Home
            </a>
            <a href="/products" class="btn-secondary">
                <i class="fas fa-shopping-bag"></i> Browse Products
            </a>
        </div>
    </div>
</section>
{% endblock %}'''

# 500.html content
five_hundred = '''{% extends "base.html" %}

{% block title %}Server Error - TechStore 2026{% endblock %}

{% block content %}
<section class="error-page">
    <div class="error-container">
        <div class="error-code">500</div>
        <h1 class="error-title">Internal Server Error</h1>
        <p class="error-message">Something went wrong on our end. We're working to fix it as soon as possible.</p>
        <div class="error-actions">
            <a href="/" class="btn-primary">
                <i class="fas fa-home"></i> Back to Home
            </a>
            <a href="/products" class="btn-secondary">
                <i class="fas fa-shopping-bag"></i> Browse Products
            </a>
        </div>
        <p class="error-help">
            <i class="fas fa-envelope"></i> 
            If the problem persists, please <a href="mailto:support@techstore2026.com">contact support</a>
        </p>
    </div>
</section>
{% endblock %}'''

# Write files
with open('templates/404.html', 'w') as f:
    f.write(four_oh_four)

with open('templates/500.html', 'w') as f:
    f.write(five_hundred)

print("✅ Created 404.html and 500.html in templates/ directory")