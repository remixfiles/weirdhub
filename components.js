// components.js - Interactivity and Card Renderers for WeirdHub
// Vanilla JS only

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

  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 900) {
        navLinks.classList.remove('open');
        menuBtn.textContent = '☰';
      }
    });
  });

  document.addEventListener('click', (e) => {
    if (!navLinks.contains(e.target) && !menuBtn.contains(e.target) && navLinks.classList.contains('open')) {
      navLinks.classList.remove('open');
      menuBtn.textContent = '☰';
    }
  });
}

function setupDropdownKeyboard() {
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

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && content.style.display === 'block') {
        content.style.display = 'none';
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  });
}

// ========= Homepage & Post Cards Render ========

let blogPosts = [];

async function loadBlogPosts() {
  if (blogPosts.length) return blogPosts;

  try {
    const response = await fetch("/blogpost.json");
    blogPosts = await response.json();
    return blogPosts;
  } catch (err) {
    console.error("Failed to load blogpost.json", err);
    return [];
  }
}

function createPostCard(post) {
  return `
    <a href="${post.link}" class="post-card">
      <img
        src="${post.featuredImage}"
        alt="${post.title}"
        loading="lazy"
        decoding="async">
      <div class="post-card-content">
        <h3>${post.title}</h3>
      </div>
    </a>
  `;
}

function shuffle(array) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

async function renderLatestPosts() {
  const container = document.getElementById("latest-posts");
  if (!container) return;

  const posts = await loadBlogPosts();
  container.innerHTML = shuffle(posts)
    .slice(0, 6)
    .map(createPostCard)
    .join("");
}

// Initialize all UI events and homepage post loader
document.addEventListener('DOMContentLoaded', () => {
  setActiveNavLinks();
  setupThemeToggle();
  setupMobileMenu();
  setupDropdownKeyboard();
  renderLatestPosts();
});