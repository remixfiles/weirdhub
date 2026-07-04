WeirdHub Static Website
=======================

This is a complete, self-contained static website for weirdhub.site built with pure HTML5, CSS3, and Vanilla JavaScript.

How to view locally:
1. Unzip the folder.
2. Open a terminal in the weirdhub-site directory.
3. Run: python3 -m http.server 8000   (or python -m http.server 8000)
4. Open http://localhost:8000 in your browser.

Alternatively, use any static file server like Live Server extension in VS Code, or serve with nginx/apache.

Features implemented:
- Fully responsive design (desktop, tablet, mobile)
- Beautiful sharp-edged minimal design with light yellow / light gray themes
- Dark mode toggle (persisted in localStorage)
- Sticky navbar with dropdown categories (pure CSS + JS)
- Mobile hamburger menu
- Post cards with 3:2 images, hover color change only (no transform)
- Justified text in blog posts
- Multiple demo blog posts with realistic content
- All category structure as requested (/blogs/category-slug/ and single posts)
- Absolute paths for nav/footer links (/about/, /blogs/ etc.)
- Relative paths avoided for main nav; root-relative for assets
- components.js + components.css loaded on every page
- Nice inline SVG logo + favicon
- Clean typography, good mobile readability with larger desktop fonts
- No frameworks, no Tailwind, no heavy CSS

Demo content includes real posts in:
- Weird Hub
- AI Facts  
- Update of Science

Other categories have placeholder cards linking to structure.

Enjoy exploring!