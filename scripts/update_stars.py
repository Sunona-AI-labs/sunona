#!/usr/bin/env python3
"""
Auto-update GitHub stars count with beautiful growth chart
Runs via GitHub Actions every 10 minutes
"""

import re
import requests
import os
import sys
import json
from datetime import datetime
from typing import Optional


def get_star_count(owner: str, repo: str) -> Optional[int]:
    """Fetch star count from GitHub API"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {}
        
        # Use GitHub token if available for higher rate limits
        if token := os.getenv("GITHUB_TOKEN"):
            headers["Authorization"] = f"token {token}"
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("stargazers_count", 0)
    except requests.RequestException as e:
        print(f"❌ Error fetching star count: {e}", file=sys.stderr)
        return None


def load_star_history() -> dict:
    """Load historical star data from JSON file"""
    history_file = "stars_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load star history: {e}")
            return {}
    return {}


def save_star_history(history: dict):
    """Save historical star data to JSON file"""
    history_file = "stars_history.json"
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save star history: {e}")


def create_smooth_star_graph(stars: int, owner: str, repo: str, repo_url: str) -> str:
    """Create a beautiful smooth growth chart using star-history.com"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d')
    
    # Load and update history
    history = load_star_history()
    history[timestamp] = stars
    save_star_history(history)
    
    # Use star-history.com API for beautiful chart
    chart_url = f"https://api.star-history.com/svg?repos={owner}/{repo}&type=Date"
    
    graph = f"""<div align="center">

### 📈 GitHub Stars Growth Chart

![Star History Chart]({chart_url})

*Chart auto-updates every 10 minutes!* ⚡

**Last Updated:** {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}

**[⭐ Star Sunona on GitHub ⭐]({repo_url})**

</div>"""
    
    return graph


def update_readme(stars: int, repo_url: str, owner: str, repo: str) -> bool:
    """Update README with star count and beautiful chart"""
    readme_path = "README.md"
    
    try:
        # Read current README
        if not os.path.exists(readme_path):
            print(f"❌ README.md not found at {readme_path}", file=sys.stderr)
            return False
            
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Create backup
        backup_path = f"{readme_path}.backup"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Generate beautiful star graph
        star_graph = create_smooth_star_graph(stars, owner, repo, repo_url)
        
        # Use regex to find and replace the stars section
        pattern = r"(<div align=\"center\">\n\n### 📈 GitHub Stars Growth.*?</div>)"
        
        if re.search(pattern, content, re.DOTALL):
            # Replace existing section
            updated_content = re.sub(pattern, star_graph, content, flags=re.DOTALL)
            print(f"✅ Updated existing stars section")
        else:
            print(f"⚠️  Stars section not found, verifying format...")
            return False
        
        # Validate content before writing
        if not updated_content or len(updated_content) < len(content) * 0.8:
            print(f"❌ Content validation failed: Updated content too small", file=sys.stderr)
            return False
        
        # Write updated README
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        # Clean up backup
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        print(f"✅ README.md updated successfully with {stars} stars!")
        return True
        
    except IOError as e:
        print(f"❌ File I/O error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error updating README: {e}", file=sys.stderr)
        return False


def main():
    """Main execution function"""
    # Get repository info from GitHub Actions environment
    repo_full = os.getenv("GITHUB_REPOSITORY", "Sunona-AI-labs/sunona")
    owner, repo = repo_full.split("/")
    
    # Build repository URL
    repo_url = f"https://github.com/{owner}/{repo}"
    
    print(f"🔍 Fetching star count for {repo_url}...")
    
    stars = get_star_count(owner, repo)
    
    if stars is None:
        print(f"⚠️  Could not fetch star count, skipping update", file=sys.stderr)
        return 1
    
    if stars < 0:
        print(f"❌ Invalid star count: {stars}", file=sys.stderr)
        return 1
    
    print(f"⭐ Found {stars} stars!")
    
    success = update_readme(stars, repo_url, owner, repo)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
