// components.js - Navbar, Footer injection + interactivity for all pages
// Vanilla JS only

function createNavbar() {
  return `
    <nav class="navbar">
      <div class="nav-container">
        <a href="/" class="logo">
          <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <circle cx="50" cy="50" r="42" fill="none" stroke="#D35400" stroke-width="7"/>
            <path d="M35 38 Q50 28 65 38" fill="none" stroke="#D35400" stroke-width="6" stroke-linecap="round"/>
            <circle cx="50" cy="55" r="6" fill="#D35400"/>
            <line x1="50" y1="61" x2="50" y2="72" stroke="#D35400" stroke-width="5" stroke-linecap="round"/>
          </svg>
          <span>WeirdHub</span>
        </a>

        <div class="nav-links" id="nav-links">
          <a href="/" class="nav-link" data-path="/">Home</a>
          <a href="/blogs/" class="nav-link" data-path="/blogs/">Blogs</a>
          
          <div class="dropdown">
            <button class="nav-link dropdown-btn" aria-haspopup="true" aria-expanded="false">
              Categories 
              <span style="font-size:0.7em; margin-left:2px;">▼</span>
            </button>
            <div class="dropdown-content">
              <a href="/blogs/update-of-science/">Update of Science</a>
              <a href="/blogs/ai-facts/">AI Facts</a>
              <a href="/blogs/political-news/">Political News</a>
              <a href="/blogs/hot-topics/">Hot Topics</a>
              <a href="/blogs/war-update/">War Update</a>
              <a href="/blogs/historical-places/">Historical Places</a>
              <a href="/blogs/weird-hub/">Weird Hub</a>
              <a href="/blogs/famous-persons/">Famous Persons</a>
            </div>
          </div>

          <a href="/about/" class="nav-link" data-path="/about/">About</a>
          <a href="/contact-us/" class="nav-link" data-path="/contact-us/">Contact Us</a>
        </div>

        <div class="nav-actions">
          <button id="theme-toggle" class="theme-btn" aria-label="Toggle theme">🌙</button>
          <button id="mobile-menu-btn" class="mobile-menu-btn" aria-label="Toggle menu">☰</button>
        </div>
      </div>
    </nav>
  `;
}

function createFooter() {
  const year = new Date().getFullYear();
  return `
    <footer class="footer">
      <div class="footer-container">
        <div class="footer-col">
          <h4>WeirdHub</h4>
          <p style="color: var(--muted-color); font-size:0.9rem; line-height:1.6;">Exploring intriguing topics from every corner of the world.</p>
        </div>
        
        <div class="footer-col">
          <h4>Explore</h4>
          <ul>
            <li><a href="/blogs/">All Blogs</a></li>
            <li><a href="/blogs/weird-hub/">Weird Hub</a></li>
            <li><a href="/blogs/ai-facts/">AI Facts</a></li>
            <li><a href="/blogs/update-of-science/">Science Updates</a></li>
          </ul>
        </div>
        
        <div class="footer-col">
          <h4>Company</h4>
          <ul>
            <li><a href="/about/">About Us</a></li>
            <li><a href="/author-message/">Author's Message</a></li>
            <li><a href="/contact-us/">Contact Us</a></li>
            <li><a href="/privacy-policy/">Privacy Policy</a></li>
          </ul>
        </div>
        
        <div class="footer-col">
          <h4>Connect</h4>
          <ul>
            <li><a href="https://twitter.com/weirdhub" target="_blank" rel="noopener">Twitter / X</a></li>
            <li><a href="#" target="_blank" rel="noopener">Instagram</a></li>
            <li><a href="#" target="_blank" rel="noopener">Newsletter</a></li>
          </ul>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; ${year} WeirdHub. All rights reserved. | Built for curious minds worldwide.</p>
      </div>
    </footer>
  `;
}

function setActiveNavLinks() {
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-link[data-path]');
  
  navLinks.forEach(link => {
    const linkPath = link.getAttribute('data-path');
    if (currentPath === linkPath || (linkPath === '/' && currentPath === '/index.html')) {
      link.classList.add('active');
    } else if (currentPath.startsWith(linkPath) && linkPath !== '/') {
      link.classList.add('active');
    }
  });
}

function setupThemeToggle() {
  const toggleBtn = document.getElementById('theme-toggle');
  if (!toggleBtn) return;

  // Set initial icon
  const currentTheme = localStorage.getItem('theme') || 'light';
  if (currentTheme === 'dark') {
    document.documentElement.classList.add('dark');
    toggleBtn.textContent = '☀️';
  } else {
    toggleBtn.textContent = '🌙';
  }

  toggleBtn.addEventListener('click', () => {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    toggleBtn.textContent = isDark ? '☀️' : '🌙';
  });
}

function setupMobileMenu() {
  const menuBtn = document.getElementById('mobile-menu-btn');
  const navLinks = document.getElementById('nav-links');
  if (!menuBtn || !navLinks) return;

  menuBtn.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    menuBtn.textContent = navLinks.classList.contains('open') ? '✕' : '☰';
  });

  // Close menu when clicking a link (mobile)
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 900) {
        navLinks.classList.remove('open');
        menuBtn.textContent = '☰';
      }
    });
  });

  // Close dropdowns or menu on outside click (optional enhancement)
  document.addEventListener('click', (e) => {
    if (!navLinks.contains(e.target) && !menuBtn.contains(e.target) && navLinks.classList.contains('open')) {
      navLinks.classList.remove('open');
      menuBtn.textContent = '☰';
    }
  });
}

function setupDropdownKeyboard() {
  // Basic accessibility for dropdown
  const dropdowns = document.querySelectorAll('.dropdown');
  dropdowns.forEach(dropdown => {
    const btn = dropdown.querySelector('.dropdown-btn');
    const content = dropdown.querySelector('.dropdown-content');
    if (!btn || !content) return;

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const isOpen = content.style.display === 'block';
      content.style.display = isOpen ? 'none' : 'block';
      btn.setAttribute('aria-expanded', !isOpen);
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && content.style.display === 'block') {
        content.style.display = 'none';
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  });
}

function injectComponents() {
  // Inject Navbar
  const navPlaceholder = document.getElementById('navbar-placeholder');
  if (navPlaceholder) {
    navPlaceholder.innerHTML = createNavbar();
  }

  // Inject Footer
  const footerPlaceholder = document.getElementById('footer-placeholder');
  if (footerPlaceholder) {
    footerPlaceholder.innerHTML = createFooter();
  }

  // Setup all interactivity after injection
  setActiveNavLinks();
  setupThemeToggle();
  setupMobileMenu();
  setupDropdownKeyboard();
}

// Auto run on every page
document.addEventListener('DOMContentLoaded', injectComponents);