# 3TL Website

Hugo static site for 3TL documentation.

## Development

```bash
hugo server
```

View at http://localhost:1313

## Build

```bash
hugo --minify
```

Output in `public/` directory.

## Deploy

### GitHub Pages

1. Build: `hugo --minify`
2. Push `public/` to `gh-pages` branch
3. Enable GitHub Pages in repository settings

Or use GitHub Actions (see `.github/workflows/` in parent directory).

### Netlify

1. Connect repository
2. Build command: `hugo --minify`
3. Publish directory: `public`

## Structure

- `content/` - Markdown content
- `layouts/` - HTML templates  
- `static/` - CSS, images
- `hugo.toml` - Configuration

## Content

- `content/_index.md` - Home page
- `content/docs/_index.md` - Documentation

Add new pages in `content/` directory.
