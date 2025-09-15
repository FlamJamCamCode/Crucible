# Encyclopedia Reader

A self-contained encyclopedia reader for the foundations and historical entries markdown files, featuring enhanced reading capabilities with Marker.js, smart search, concept tooltips, and full browser history support.

## Features

- **Enhanced Reading Experience**: Integrated Marker.js for annotations and highlights
- **Smart Search**: Real-time search across all documents with instant results
- **Concept Tooltips**: Hover over highlighted concepts for definitions from other documents
- **Internal Link Navigation**: Click any internal link to jump to related documents
- **Browser History**: Full HTML5 History API support with back/forward navigation
- **Responsive Design**: Modern, mobile-friendly interface
- **Cross-Reference System**: Automatic concept highlighting and definition tooltips

## Getting Started

### Option 1: Static Version (Recommended - No Server Required!)

Simply open the static HTML file directly in your browser:
```
system share/document-viewer.html
```

This version has all markdown content embedded directly - no server needed!

### Option 2: Server Version (For Development)

1. Run the Python server:
   ```bash
   python serve_encyclopedia.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/server-browser/encyclopedia-reader.html
   ```

### Option 3: Alternative Port

If port 8000 is busy:
```bash
python serve_encyclopedia.py --port 8001
```

Then open: `http://localhost:8001/server-browser/encyclopedia-reader.html`

## Usage

### Navigation
- Use the sidebar to browse documents by category (Foundations or Historical Entries)
- Click on any document title to load it
- Use the breadcrumb navigation to return to home or navigate between sections

### Search
- Type in the search box to find content across all documents
- Results show document title, excerpt, and match count
- Click any result to jump directly to that document

### Reading
- Click the "Add Annotation" button to use Marker.js for highlighting and annotations
- Hover over highlighted concepts (blue dotted underline) for definitions
- Click any internal link to navigate to related documents
- Use browser back/forward buttons for full navigation history

### Concept System
The reader automatically detects and highlights key concepts including:
- Proof of Person (PoP)
- Proof of Utility (PoU)
- Trust Networks
- Discovery OS
- Blob Classes
- AR Phase Engine
- Will Coalescence
- Aiddaemon
- The Crucible
- Daemonia
- Triad
- NSS (Natural Selection System)

## File Structure

```
├── server-browser/
│   ├── encyclopedia-reader.html    # Server-based application
│   ├── serve_encyclopedia.py       # Local server script
│   ├── start_encyclopedia.bat      # Windows startup script
│   └── README.md                   # This file
├── system share/
│   ├── document-viewer.html        # Static version (no server needed!)
│   ├── foundations/                # Foundation documents (54 files)
│   └── historical-entries/         # Historical entries (8 files)
└── generate_static_encyclopedia.py # Script to generate static version
```

## Technical Details

### Dependencies
- **Marker.js 3**: For annotations and highlights
- **Marked.js**: For markdown parsing
- **Prism.js**: For syntax highlighting
- **Vanilla JavaScript**: No framework dependencies

### Browser Compatibility
- Modern browsers with ES6+ support
- HTML5 History API support
- CSS Grid and Flexbox support

### Fixed Issues
- Corrected broken internal links in markdown files
- Fixed path references between documents
- Ensured all concept definitions are properly linked

## Development

The application is built with vanilla HTML, CSS, and JavaScript for maximum compatibility and simplicity. All functionality is contained within the single HTML file, making it easy to deploy and share.

### Key Components
- `appState`: Global state management
- `documentStructure`: Document catalog and metadata
- `loadDocument()`: Document loading and rendering
- `performSearch()`: Search functionality
- `addConceptTooltips()`: Concept highlighting system
- `initializeMarker()`: Marker.js integration
- `setupHistoryAPI()`: Browser history management

## Troubleshooting

### CORS Issues
If you encounter CORS errors when opening the file directly:
- Use the Python server instead of opening the file directly
- The server adds proper CORS headers for local file access

### Missing Files
If documents fail to load:
- Ensure the `system share/` directory structure is intact
- Check that markdown files exist in the correct locations
- Verify file permissions allow reading

### Search Not Working
- Ensure JavaScript is enabled
- Check browser console for errors
- Verify markdown files are accessible via the server

## Contributing

To add new documents or concepts:
1. Add the document to the appropriate directory
2. Update the `documentStructure` object in the HTML file
3. Add concept definitions to the `getConceptDefinition()` function
4. Test all internal links for accuracy

## License

This encyclopedia reader is provided as-is for educational and reference purposes.
