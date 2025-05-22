# Static Assets for AES Visualizer

This directory contains the static assets (CSS, JavaScript, etc.) for the AES Visualizer application.

## Directory Structure

```
static/
├── css/                  # CSS stylesheets
│   ├── styles.css        # Development version (readable, commented)
│   └── styles.min.css    # Production version (minified)
├── js/                   # JavaScript files
│   ├── script.js         # Development version (readable, commented)
│   └── script.min.js     # Production version (minified)
├── index.html            # Production template for landing page
├── visualize.html        # Production template for visualization page
└── README.md             # This file
```

## Development vs. Production

### Development
During development, use the non-minified versions of the files:
- `css/styles.css`
- `js/script.js`

These files are well-commented and formatted for readability, making them easier to modify and debug.

### Production
For production deployment, use the minified versions:
- `css/styles.min.css`
- `js/script.min.js`

These files have been optimized by:
1. Removing comments and unnecessary whitespace
2. Consolidating redundant styles
3. Using CSS variables for common properties

## Optimizations Made

### CSS Optimizations
- Added CSS variables for common transitions
- Consolidated redundant transition properties
- Improved organization with better section comments
- Created a minified version for production

### JavaScript Optimizations
- Improved code organization with logical sections
- Added JSDoc comments for better documentation
- Created modular functions for better maintainability
- Created a minified version for production

## Usage in Templates

### Development Templates
The original templates in the `templates/` directory reference the original files:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
<script src="{{ url_for('static', filename='script.js') }}"></script>
```

### Production Templates
The production templates in the `static/` directory reference the minified files:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/styles.min.css') }}">
<script src="{{ url_for('static', filename='js/script.min.js') }}"></script>
```

To use the production templates, you would need to modify the Flask routes to render these templates instead of the ones in the `templates/` directory.