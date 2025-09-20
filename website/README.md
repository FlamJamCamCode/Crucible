# The New World Encyclopedia - Website

A comprehensive, deployable website containing all documents from the New World system.

## Quick Deployment

### Option 1: DigitalOcean/Azure/Linode
1. Create a new droplet/server
2. Install Apache: `sudo apt update && sudo apt install apache2`
3. Upload all files to `/var/www/html/`
4. Set permissions: `sudo chown -R www-data:www-data /var/www/html/`
5. Enable Apache: `sudo systemctl enable apache2 && sudo systemctl start apache2`
6. Visit your server's IP address

### Option 2: Shared Hosting (cPanel, etc.)
1. Upload all files to your `public_html` directory
2. Ensure `index.html` is in the root
3. Visit your domain

### Option 3: GitHub Pages
1. Upload to a GitHub repository
2. Enable GitHub Pages in repository settings
3. Select source branch

## File Structure
- `index.html` - Main encyclopedia interface
- `.htaccess` - Apache configuration
- `README.md` - This file

## Features
- **Complete Offline Functionality** - All content embedded
- **Fast Search** - Real-time filtering across all documents
- **Category Filtering** - Filter by document type
- **Responsive Design** - Works on all devices
- **Markdown Rendering** - Full markdown support with syntax highlighting
- **No Database Required** - Pure HTML/CSS/JavaScript

## Content Included
- All foundation documents
- Historical entries
- Dialectical analysis
- Magic and polymorphic systems
- Economic frameworks
- Technical architecture
- And much more...

## Browser Support
- Chrome/Edge 80+
- Firefox 75+
- Safari 13+
- Mobile browsers

## Customization
Edit `index.html` to modify:
- Colors and styling
- Add new documents
- Change layout
- Add features

Generated on: 2025-09-18