import os
import json
import base64
import html
import re
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_OWNER = os.environ["REPO_OWNER"]
REPO_NAME = os.environ["REPO_NAME"]
BRANCH = "main"
PASS1_SECRET = os.environ["PASS1"]
PASS2_SECRET = os.environ["PASS2"]
GITHUB_API = "https://api.github.com"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def fail(message):
    print(f"ERROR: {message}")
    raise SystemExit(1)

def get_input(name, default=""):
    value = os.environ.get(name, default)
    return value.strip() if isinstance(value, str) else value

def github_get(path):
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    response = requests.get(url, headers=headers, params={"ref": BRANCH})
    if response.status_code != 200:
        fail(f"GitHub GET failed for {path}: {response.status_code} {response.text}")
    return response.json()

def get_file(path):
    data = github_get(path)
    if isinstance(data, list):
        fail(f"{path} is a directory, not a file.")
    content = data.get("content", "")
    if data.get("encoding") == "base64":
        return base64.b64decode(content).decode("utf-8"), data["sha"]
    return content, data["sha"]

def github_put(path, content, message, sha=None):
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": message,
        "content": encoded,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code not in (200, 201):
        fail(f"GitHub PUT failed for {path}: {response.status_code} {response.text}")
    return response.json()

def clean_slug(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")

def escape_text(value):
    return html.escape(value, quote=True)

def parse_article(full_article):
    blocks = re.split(r"\r?\n\s*\r?\n+", full_article.strip())
    blocks = [b.strip() for b in blocks if b.strip()]
    if not blocks:
        fail("Full article content is empty.")
    title = blocks[0].strip()
    title = re.sub(r"^\*\*(.*?)\*\*$", r"\1", title).strip()
    content = []
    for index, block in enumerate(blocks[1:]):
        block = block.strip()
        block = re.sub(r"^\*\*(.*?)\*\*$", r"\1", block).strip()
        if index % 2 == 0:
            content.append(f'<h2>{escape_text(block)}</h2>')
        else:
            content.append(f'<p>{escape_text(block)}</p>')
            if index == 1:
                content.append('<!-- FIGURE AD PLACEHOLDER -->')
            if index == 3:
                content.append('<!-- SUPPORT WRITER BANNER -->')
    return title, "\n".join(content)

def generate_post_card(post):
    title = escape_text(post["title"])
    image = escape_text(post["featuredImage"])
    link = post["link"]
    return f'''<a href="{link}" class="post-card">
  <img src="{image}" alt="{title}">
  <div class="post-card-content">
    <h3>{title}</h3>
  </div>
</a>'''

def update_blog_index(content, new_card):
    marker = '<!-- ---------------- New Cards Add Here ------------------- -->'
    if marker not in content:
        fail("Blog index marker not found.")
    return content.replace(
        marker,
        marker + "\n" + new_card,
        1
    )

def update_category_index(content, new_card):
    marker = '<!-- New Card -->'
    if marker not in content:
        fail("Category page marker not found.")
    return content.replace(
        marker,
        marker + "\n" + new_card,
        1
    )


def update_home_featured(content, new_card):
    marker = '<!-- Home Card Add Below -->'

    if marker not in content:
        fail("Home Featured marker not found.")

    start = content.index(marker) + len(marker)

    end_marker = '''    </div>
    </div>
  </section>'''

    end = content.find(end_marker, start)

    if end == -1:
        fail("Home Featured section ending not found.")

    featured_area = content[start:end]

    cards = re.findall(
        r'<a href="[^"]+" class="post-card">.*?</a>',
        featured_area,
        flags=re.S
    )

    cards = [new_card] + cards[:14]

    new_featured_area = "\n\n\n" + "\n\n\n".join(cards) + "\n\n"

    return (
        content[:start]
        + new_featured_area
        + content[end:]
    )


def update_sitemap(content, category, slug):
    today = datetime.now(ZoneInfo("Asia/Dhaka")).strftime("%Y-%m-%d")
    new_url = f"https://weirdhub.site/blogs/{category}/{slug}/"
    new_entry = f'''  <url>
    <loc>{new_url}</loc>
    <lastmod>{today}</lastmod>
  </url>
'''
    marker = "</urlset>"
    if marker not in content:
        fail("Sitemap closing tag not found.")
    return content.replace(marker, new_entry + marker, 1)


def update_blogpost_json(content, new_post):
    data = json.loads(content)
    if not isinstance(data, list):
        fail("blogpost.json is not a JSON array.")
    data.append(new_post)
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"

def generate_article_html(title, slug, category, author, featured_image, meta_description, references, full_article, more_posts):
    blocks = re.split(r"\r?\n\s*\r?\n+", full_article.strip())
    blocks = [block.strip() for block in blocks if block.strip()]
    if not blocks:
        fail("Full article content is empty.")
    def clean_text(text):
        return re.sub(r"^\*\*(.*?)\*\*$", r"\1", text, flags=re.S).strip()
    title = clean_text(blocks[0])
    content = ""
    first_paragraph_inserted = False
    for i in range(1, len(blocks)):
        block = clean_text(blocks[i])
        if not block:
            continue
        if i % 2 == 1:
            content += f"      <h2>{block}</h2>\n\n"
        else:
            content += f"      <p>{block}</p>\n\n"
            if not first_paragraph_inserted:
                content += '''      <!--
      <figure>
        <a href="https://www.profitableratecpmnetwork.com/s3vef0gkh?key=e44c948612fcd34afd5a4a4282ce9f92">
          <img src="" alt="" loading="lazy">
        </a>
        <figcaption></figcaption>
      </figure>
      -->

'''
                first_paragraph_inserted = True
            if i == 4:
                content += '''      <br><div class="centerAds">
        <script>
  atOptions = {{
    'key' : '833253cad0d9cbe33ecac475deddcc5c',
    'format' : 'iframe',
    'height' : 50,
    'width' : 320,
    'params' : {{}}
  }};
</script>
<script src="https://www.highrevenueformat.com/833253cad0d9cbe33ecac475deddcc5c/invoke.js"></script>
      </div><br>

      <div>
        <a href="https://www.profitableratecpmnetwork.com/s3vef0gkh?key=e44c948612fcd34afd5a4a4282ce9f92">
          <img src="https://res.cloudinary.com/dhj4ovvav/image/upload/v1788140778/support_juhcsm.webp" alt="" loading="lazy">
        </a>
        <figcaption>By clicking the banner, you can support writer for free</figcaption>
      </div>

'''
    references_html = ""
    if references.strip():
        refs = [r.strip() for r in references.splitlines() if r.strip()]
        refs_html = f'''
        <div class="centerAds">
<script>
  atOptions = {{
    'key' : '47f39551278bad9b7c4e470d1c751af0',
    'format' : 'iframe',
    'height' : 50,
    'width' : 320,
    'params' : {{}}
  }};
</script>
<script src="https://www.highrevenueformat.com/47f39551278bad9b7c4e470d1c751af0/invoke.js"></script>
</div>
<br>
      <hr>

      <section class="references">
        <h2>References</h2>
        <ol>
{chr(10).join(f"          <li>{ref}</li>" for ref in refs)}
        </ol>
      </section>

'''
    more_posts_html = "\n".join(generate_post_card(post) for post in more_posts)
    canonical = f"https://weirdhub.site/blogs/{category}/{slug}/"
    category_names = {
        "update-of-science": "Update of Science",
        "animals": "Animal Facts",
        "brave-works": "Brave Works",
        "hot-topics": "Hot Topics",
        "war-history": "War History",
        "historical-places": "Historical Places",
        "weird-hub": "Weird Hub",
        "famous-persons": "Famous Persons"
    }
    category_name = category_names.get(category, category.replace("-", " ").title())
    today = datetime.now(ZoneInfo("Asia/Dhaka"))
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    date = f"{today.day} {months[today.month - 1]}, {today.year}"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | WeirdHub</title>
<meta name="description" content="{meta_description}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="WeirdHub">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{featured_image}">
<meta property="og:image:secure_url" content="{featured_image}">
<meta property="og:image:type" content="image/webp">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="800">
<meta property="og:image:alt" content="{title}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{meta_description}">
<meta name="twitter:image" content="{featured_image}">
<meta name="theme-color" content="#111827">
<link rel="stylesheet" href="/css/components.css">
<link rel="stylesheet" href="/css/post.css">
<link rel="icon" href="/images/favicon.ico">
</head>
<body>
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
            <a href="/blogs/animals/">Animal Facts</a>
            <a href="/blogs/brave-works/">Brave Works</a>
            <a href="/blogs/hot-topics/">Hot Topics</a>
            <a href="/blogs/war-history/">War History</a>
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
  <article class="post-container">
    <div class="post-header">
      <span class="tag">{category_name.upper()}</span>
      <h1 class="post-title">{title}</h1>
      <div class="post-meta">
        <span>By <strong>{author}</strong></span>
        <span>•</span>
        <span>{date}</span>
      </div>
    </div>
    <a href="https://www.profitableratecpmnetwork.com/s3vef0gkh?key=e44c948612fcd34afd5a4a4282ce9f92">
      <img src="{featured_image}" alt="{title}" title="{title}" class="post-hero" loading="eager" fetchpriority="high" width="1200" height="800">
    </a>
    <div class="post-content">
{content}{references_html}
      <a href="https://www.profitableratecpmnetwork.com/s3vef0gkh?key=e44c948612fcd34afd5a4a4282ce9f92">
        ❤ <b>Support Writer</b> 👈👈👈
      </a>
      <br><br>
    </div>
    <div class="post-footer">
      <p><strong>Share this story:</strong> 
        <a href="https://www.profitableratecpmnetwork.com/s3vef0gkh?key=e44c948612fcd34afd5a4a4282ce9f92">X</a> • 
        <a href="https://www.profitableratecpmnetwork.com/s3vef0gkh?key=e44c948612fcd34afd5a4a4282ce9f92">LinkedIn</a>
      </p>
      <p style="margin-top:12px;">
        <a href="/blogs/{category}/{slug}/">
          &larr; Back to {category_name}
        </a>
      </p>
    </div>
  </article>
  <section class="section more-posts">
    <div class="container">
      <h2 class="section-title">More Posts</h2>
      <div class="grid grid-3" id="more-posts">
{more_posts_html}
      </div>
    </div>
  </section>
<script async="async" data-cfasync="false" src="https://pl31347707.profitableratecpmnetwork.com/ad1aa6a7468f4a598d090b0d7d274eba/invoke.js"></script>
<div id="container-ad1aa6a7468f4a598d090b0d7d274eba"></div>
<div class="centerAds">
<script>
  atOptions = {{
    'key' : '359a046d469c5ec35d9731811bd6e381',
    'format' : 'iframe',
    'height' : 90,
    'width' : 728,
    'params' : {{}}
  }};
</script>
<script src="https://www.highrevenueformat.com/359a046d469c5ec35d9731811bd6e381/invoke.js"></script>
</div>
<footer class="footer">
  <!-- Newsletter Subscription Section -->
  <div class="newsletter-wrapper">
    <div class="newsletter-inner">
      <div class="newsletter-info">
        <h3>Curiosity in Your Inbox</h3>
        <p>Get our weekly digest of the 5 most bizarre, astonishing, and mind-bending stories delivered straight to you.</p>
      </div>
      <form id="newsletter-form" class="newsletter-form">
        <div class="newsletter-input-group">
          <input type="email" id="newsletter-email" placeholder="Enter your email address" required autocomplete="email" />
          <button type="submit" id="newsletter-btn">
            <span class="btn-text">Subscribe</span>
            <span class="btn-spinner" style="display:none;">Joining...</span>
          </button>
        </div>
        <div id="newsletter-status" class="newsletter-status" aria-live="polite"></div>
      </form>
    </div>
  </div>

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
        <li><a href="/blogs/animals/">Animal Facts</a></li>
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
	<li><a href="https://www.facebook.com/weirdhub.site" target="_blank" rel="noopener">Facebook</a></li>
        <li><a href="https://x.com/WeirdHubSite" target="_blank" rel="noopener">Twitter / X</a></li>
      </ul>
    </div>
  </div>

  <div class="footer-bottom">
    <p>&copy; 2026 WeirdHub. All rights reserved. | Built for curious minds worldwide.</p>
  </div>
</footer>
<script src="/components.js"></script>
<script src="https://pl31347708.profitableratecpmnetwork.com/52/a0/e2/52a0e20abd377d32e9156dd711a3ee98.js"></script>
<script src="/js/email-subscribe.js" defer></script>
</body>
</html>'''

def main():
    pass1 = get_input("INPUT_PASS1")
    pass2 = get_input("INPUT_PASS2")

    if pass1 != PASS1_SECRET:
        fail("Pass1 verification failed.")
    if pass2 != PASS2_SECRET:
        fail("Pass2 verification failed.")

    slug = clean_slug(get_input("POST_SLUG"))
    category_input = get_input("POST_CATEGORY")
    category_map = {
        "update of science": "update-of-science",
        "update-of-science": "update-of-science",
        "animal facts": "animals",
        "animals": "animals",
        "brave works": "brave-works",
        "brave-works": "brave-works",
        "hot topics": "hot-topics",
        "hot-topics": "hot-topics",
        "war history": "war-history",
        "war-history": "war-history",
        "historical places": "historical-places",
        "historical-places": "historical-places",
        "weird hub": "weird-hub",
        "weird-hub": "weird-hub",
        "famous persons": "famous-persons",
        "famous-persons": "famous-persons"
    }
    category = category_map.get(category_input.lower())
    if not category:
        fail(f"Invalid category: {category_input}")
    author = get_input("POST_AUTHOR")
    featured_image = get_input("FEATURED_IMAGE")
    meta_description = get_input("META_DESCRIPTION")
    references = get_input("REFERENCES")
    full_article = get_input("FULL_ARTICLE")
    featured = get_input("FEATURED").lower() == "true"

    if not slug:
        fail("Post slug is required.")
    if not category:
        fail("Category is required.")
    if not full_article:
        fail("Full article is required.")

    title, _ = parse_article(full_article)

    blogpost_content, blogpost_sha = get_file("blogpost.json")
    posts = json.loads(blogpost_content)

    if not isinstance(posts, list):
        fail("blogpost.json must contain an array.")

    for post in posts:
        if post.get("postSlug") == slug:
            fail(f"Post slug already exists: {slug}")

    link = f"/blogs/{category}/{slug}/"

    new_post = {
        "title": title,
        "categorySlug": category,
        "postSlug": slug,
        "link": link,
        "featuredImage": featured_image,
        "metaDescription": meta_description
    }

    # Previous six posts, immediately before the new post.
    more_posts = posts[-6:]

    article_html = generate_article_html(
        title=title,
        slug=slug,
        category=category,
        author=author,
        featured_image=featured_image,
        meta_description=meta_description,
        references=references,
        full_article=full_article,
        more_posts=more_posts
    )

    new_blogpost_content = update_blogpost_json(
        blogpost_content,
        new_post
    )

    blog_index_content, blog_index_sha = get_file("blogs/index.html")
    new_card = generate_post_card(new_post)
    new_blog_index_content = update_blog_index(
        blog_index_content,
        new_card
    )

    category_path = f"blogs/{category}/index.html"
    category_content, category_sha = get_file(category_path)
    sitemap_content, sitemap_sha = get_file("sitemap.xml")

    new_category_content = update_category_index(
            category_content,
            new_card
    )

    new_sitemap_content = update_sitemap(
            sitemap_content,
            category,
            slug
    )

    home_index_content = None
    home_index_sha = None
    new_home_index_content = None

    if featured:
        home_index_content, home_index_sha = get_file("index.html")
        new_home_index_content = update_home_featured(
            home_index_content,
            new_card
        )

    article_path = f"blogs/{category}/{slug}/index.html"

    print("Publishing:")
    print(f"Title: {title}")
    print(f"Category: {category}")
    print(f"Slug: {slug}")
    print(f"Article: {article_path}")

    github_put(
        "blogpost.json",
        new_blogpost_content,
        f"Publish blog: {title}",
        blogpost_sha
    )

    github_put(
        "blogs/index.html",
        new_blog_index_content,
        f"Add blog card: {title}",
        blog_index_sha
    )

    github_put(
        category_path,
        new_category_content,
        f"Add category card: {title}",
        category_sha
    )

    github_put(
            article_path,
            article_html,
            f"Create blog post: {title}"
        )

    github_put(
            "sitemap.xml",
            new_sitemap_content,
            f"Update sitemap: {title}",
            sitemap_sha
        )

    if featured:
        github_put(
            "index.html",
            new_home_index_content,
            f"Update Featured Stories: {title}",
            home_index_sha
        )

    print("SUCCESS: Blog post published successfully.")

if __name__ == "__main__":
    main()