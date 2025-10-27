# Jekyll Setup Guide for LetsGetCrypto

This document explains the Jekyll configuration and how to work with the Jekyll-powered GitHub Pages deployment.

## Overview

LetsGetCrypto now uses Jekyll, a static site generator, for its GitHub Pages deployment. This provides better maintainability, SEO optimization, and the ability to reuse components across pages.

## Jekyll Structure

```
docs/
├── _config.yml          # Jekyll configuration
├── Gemfile              # Ruby dependencies
├── _layouts/            # Page layouts
│   └── default.html     # Main layout template
├── _includes/           # Reusable components
│   ├── header.html      # Site header
│   └── footer.html      # Site footer
├── css/                 # Stylesheets (copied as-is)
├── js/                  # JavaScript (copied as-is)
├── index.html           # Main page (uses Jekyll front matter)
└── _site/              # Generated site (gitignored)
```

## Configuration Files

### _config.yml

The Jekyll configuration file defines:
- Site metadata (title, description, URL)
- Build settings (markdown processor, syntax highlighter)
- Plugin configuration (SEO, feeds, sitemap)
- File exclusions and inclusions

Key settings:
```yaml
title: LetsGetCrypto
description: Advanced Cryptocurrency Trading & Prediction Tool
baseurl: "/letsgetcrypto"
url: "https://aaakaind.github.io"
theme: minima
```

### Gemfile

Defines Ruby gem dependencies:
- `github-pages` - GitHub Pages compatible Jekyll and plugins
- `webrick` - Web server for local testing (Ruby 3.0+)

## Layouts and Includes

### Layouts

Layouts wrap your content with common HTML structure. The `default.html` layout includes:
- HTML5 doctype and head section
- SEO meta tags (via jekyll-seo-tag)
- CSS and JavaScript includes
- Header and footer includes
- Content placeholder

Pages use layouts via front matter:
```yaml
---
layout: default
title: Trading Dashboard
---
```

### Includes

Reusable components that can be included in layouts or pages:

- `header.html` - Site header with logo and status indicator
- `footer.html` - Risk warning and links

Include them with: `{% include header.html %}`

## Working with Jekyll

### Local Development

#### Prerequisites
- Ruby 3.0+ installed
- Bundler gem installed

#### Setup
```bash
cd docs
gem install bundler --user-install
bundle config set --local path 'vendor/bundle'
bundle install
```

#### Build the Site
```bash
bundle exec jekyll build
# Output in _site/ directory
```

#### Serve Locally
```bash
bundle exec jekyll serve --port 8080
# Visit http://localhost:8080/letsgetcrypto/
```

#### Watch for Changes
```bash
bundle exec jekyll serve --watch
# Automatically rebuilds when files change
```

### Adding New Pages

1. Create a new HTML or Markdown file in `docs/`
2. Add Jekyll front matter at the top:
   ```yaml
   ---
   layout: default
   title: My New Page
   description: Description for SEO
   ---
   ```
3. Add your content
4. Link to it from other pages: `{{ '/my-page.html' | relative_url }}`

### Creating New Layouts

1. Create a new file in `docs/_layouts/`
2. Add HTML structure with `{{ content }}` placeholder
3. Reference it in page front matter: `layout: my-layout`

### Adding Includes

1. Create a new file in `docs/_includes/`
2. Add your HTML component
3. Include it: `{% include my-component.html %}`

### Using Variables

Jekyll provides many variables:

- **Site variables**: `{{ site.title }}`, `{{ site.description }}`
- **Page variables**: `{{ page.title }}`, `{{ page.url }}`
- **Relative URLs**: `{{ '/css/style.css' | relative_url }}`
- **Conditionals**: `{% if page.title %}...{% endif %}`

## GitHub Actions Deployment

The workflow in `.github/workflows/deploy-pages.yml` automatically:

1. Checks out the repository
2. Sets up Ruby and installs dependencies
3. Builds the Jekyll site
4. Uploads the `_site/` directory
5. Deploys to GitHub Pages

The workflow runs on:
- Push to `main` branch
- Manual trigger from Actions tab

## Plugins

Jekyll plugins are configured in `_config.yml`:

### jekyll-seo-tag
Adds SEO meta tags automatically:
- Title, description, canonical URL
- Open Graph tags for social media
- Twitter Card tags
- Structured data (JSON-LD)

Usage: `{% seo %}` in layout head

### jekyll-feed
Generates an Atom feed at `/feed.xml` for RSS readers.

### jekyll-sitemap
Generates `sitemap.xml` for search engines.

## Customization

### Changing Site Metadata

Edit `docs/_config.yml`:
```yaml
title: Your Site Title
description: Your description
author: your-username
```

### Modifying Styles

Edit `docs/css/dashboard.css` - Jekyll copies it as-is.

### Updating JavaScript

Edit `docs/js/dashboard.js` - Jekyll copies it as-is.

### Changing Layout

Edit `docs/_layouts/default.html` to modify the page structure.

## Troubleshooting

### Build Errors

**Error: "Dependency Error"**
```bash
cd docs
bundle install
```

**Error: "cannot load such file -- webrick"**
```bash
# Add to Gemfile:
gem "webrick", "~> 1.8"
bundle install
```

### Local Server Issues

**Port already in use:**
```bash
bundle exec jekyll serve --port 8081
```

**Changes not appearing:**
```bash
# Clear Jekyll cache
rm -rf _site .jekyll-cache
bundle exec jekyll serve --watch
```

### GitHub Pages Deployment

**Check the Actions tab** in your repository for build logs.

**Verify GitHub Pages settings:**
1. Go to repository Settings → Pages
2. Source should be "GitHub Actions"
3. Check the deployment URL

## Comparison: Before and After

### Before (Static HTML)
- Single `index.html` with all HTML
- Repeated header/footer code
- Manual SEO tags
- No build process

### After (Jekyll)
- Modular layout system
- Reusable components
- Automatic SEO optimization
- Build process with plugins
- Future-ready for multiple pages

## Migration Notes

The conversion preserved all functionality:
- ✅ All CSS and JavaScript work identically
- ✅ No changes to dashboard behavior
- ✅ Enhanced with SEO tags
- ✅ Added sitemap and RSS feed
- ✅ Improved maintainability

## Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [jekyll-seo-tag Documentation](https://github.com/jekyll/jekyll-seo-tag)
- [Liquid Template Language](https://shopify.github.io/liquid/)

## Next Steps

Consider these enhancements:

1. **Multiple Pages**: Add documentation, about, or guide pages
2. **Blog Posts**: Use Jekyll's built-in blog support
3. **Custom Theme**: Create a custom Jekyll theme
4. **Data Files**: Use `_data/` for configuration data
5. **Collections**: Organize related content in collections

---

For questions or issues with the Jekyll setup, see the main repository documentation or open an issue.
