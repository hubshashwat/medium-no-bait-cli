# Medium Terminal Suite 🚀

A high-performance, terminal-based Medium reader designed for developers who value signal over noise. Track your favorite authors and publications, and catch the most relevant stories using custom keyword filters.

## Features

- **Personalized Dashboards**: See updates from exactly who you follow.
- **Keyword Hits**: A dedicated high-signal feed that filters stories by your interests (e.g., AI, Python, Rust).
- **RSS-Powered**: Lightning-fast update checks using official Medium RSS feeds.
- **Terminal Optimization**: Beautiful, non-truncating link display for seamless reading on your browser.
- **Persistence**: Tracks your last access date for every source automatically.

## Quick Start

### Prerequisites
- Python 3.8+
- A terminal (PowerShell, bash, or CMD)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/best-medium-reader.git
   cd best-medium-reader
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App
```bash
python main.py
```

## How It Works

1. **Manage Favorites**: Add authors (use `@username`) and publications (use the pub name from the URL, e.g., `the-startup`) in the Manage menu.
2. **Setup Keywords**: Add specific keywords you want to track across your favorites.
3. **Enjoy Signal**: Use the **Keyword Hits** view to see exactly what you care about, or the **Full Feed** to browse everything new.

## Project Structure
- `main.py`: The central terminal interface.
- `author_updates/`: Logic for tracking and filtering updates.
- `shared/`: Shared models, storage utilities, and the RSS scraper.

---
Built with 💙 for the Medium developer community.
