# Moltbot Skills Explorer

A fast, searchable, and sortable index of [Moltbot skills](https://clawdhub.com/skills).

## Features
- **Instant Search**: Find skills by name or functionality (description).
- **Sorting**: Sort by GitHub star count or alphabetically.
- **Auto-updates**: Data is automatically refreshed every 6 hours via GitHub Actions.

## How it works
The project uses a Python scraper (`update_skills.py`) to fetch data from ClawdHub. The frontend is a simple static HTML page that uses `Fuse.js` for client-side searching.
