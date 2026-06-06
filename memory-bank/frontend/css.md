# CSS (`static/css/style.css`)

## Overview
- **681 lines** of CSS
- CSS custom properties for theming
- Responsive breakpoints: mobile ≤576px, tablet ≤768px, desktop

## Custom properties (`:root`)
```css
--color-primary: #2c3e50;
--color-secondary: #34495e;
--color-accent: #e74c3c;
--color-success: #27ae60;
--color-warning: #f39c12;
--color-info: #3498db;
--color-text: #2c3e50;
--color-text-light: #7f8c8d;
--color-bg: #ecf0f1;
--color-card: #ffffff;
--color-border: #ddd;
--radius: 8px;
--shadow: 0 2px 4px rgba(0,0,0,0.1);
```

## Components styled

| Component | Details |
|-----------|---------|
| Navbar | Fixed top, dark bg, responsive hamburger menu |
| Cards | White bg, shadow, border-radius, padding |
| Tables | Striped rows, hover effect, responsive scroll |
| Buttons | Primary (blue), outline, danger variants |
| Forms | Input, select, textarea with consistent styling |
| Badges | Status badges (active=green, completed=gray) |
| Flash messages | Success (green), error (red), info (blue), warning (yellow) |
| Pagination | Horizontal button group |
| Dashboard grid | 3-column grid for top players, favorites, tournaments |
| Empty state | Centered message with icon |
| Spinner | CSS-only spinning animation |
| Toast | Fixed bottom-right notification |

## Known issues
- Link color `#3498db` may have contrast issues (accessibility audit score 80/100)
- Placeholder text `#7f8c8d` — low contrast on white bg

## Links
- → `frontend/overview.md` — architecture
- → `backend/web-layer.md` — web.py routes