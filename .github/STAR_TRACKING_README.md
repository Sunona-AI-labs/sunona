# 🌟 GitHub Stars Automatic Tracking

This folder contains the GitHub Actions workflow that automatically tracks and updates your GitHub stars on your README.

## 📊 How It Works

1. **Automatic Execution** - Runs every 10 minutes via GitHub Actions
2. **Star Fetching** - Retrieves current star count from GitHub API
3. **Growth Tracking** - Saves historical data in `stars_history.json`
4. **README Update** - Generates beautiful growth chart and updates README
5. **Auto-Commit** - Commits changes back to your repository

## 📁 Files Structure

```
.github/
├── workflows/
│   └── update-stars.yml        # GitHub Actions workflow (10min schedule)
└── STAR_TRACKING_README.md     # This file

scripts/
└── update_stars.py             # Python script that does the heavy lifting

stars_history.json              # Auto-generated: Historical star data
```

## 🚀 Setup Instructions

### 1. Replace Repository URLs

Update the following with your actual GitHub username/repo:

**In README.md:**
```markdown
![Star History Chart](https://api.star-history.com/svg?repos=YOUR-USERNAME/sunona&type=Date)
```

**In update_stars.py:**
- The script automatically reads from `GITHUB_REPOSITORY` environment variable
- Default fallback: `sunona-ai/sunona`

### 2. Initial Commit

Push all files to GitHub:
```bash
git add .github/workflows/update-stars.yml
git add scripts/update_stars.py
git add stars_history.json
git commit -m "🌟 Add automatic GitHub stars tracking"
git push origin main
```

### 3. Verify Workflow

Check GitHub Actions:
1. Go to **Actions** tab in your repository
2. Look for "🌟 Update GitHub Stars" workflow
3. Wait for first run to complete (or trigger manually)

## 📈 Chart Features

- **Beautiful Growth Chart** - Powered by star-history.com
- **Real-time Updates** - Every 10 minutes
- **Historical Data** - All recorded in stars_history.json
- **Responsive** - Works on desktop and mobile

## 🔧 Customization

### Change Update Frequency

Edit `.github/workflows/update-stars.yml`:

```yaml
schedule:
  # Run every X minutes
  - cron: '*/10 * * * *'  # Change 10 to desired minutes
```

Common frequencies:
- Every 5 minutes: `*/5 * * * *`
- Every 30 minutes: `*/30 * * * *`
- Every hour: `0 * * * *`
- Every 6 hours: `0 */6 * * *`
- Daily: `0 0 * * *`

### Modify Chart Appearance

Edit `scripts/update_stars.py` in `create_smooth_star_graph()` function to customize the chart section in README.

## 🐛 Troubleshooting

### Chart Not Updating
- Check GitHub Actions logs for errors
- Verify `GITHUB_TOKEN` has write permissions
- Ensure README contains the exact pattern:
  ```markdown
  ### 📈 GitHub Stars Growth Chart
  ```

### Missing History File
- `stars_history.json` is auto-created on first run
- Check workflow logs for creation confirmation

### No Chart Visible
- Verify your GitHub username/repo in the chart URL
- Visit the chart URL directly: `https://api.star-history.com/svg?repos=YOUR-USERNAME/sunona&type=Date`

## 📊 Data Files

### stars_history.json
```json
{
  "2025-12-29": 42,
  "2025-12-30": 45,
  "2025-12-31": 48
}
```

Tracks one entry per day. Used for historical context and statistics.

## ✨ Features

✅ Automatic every 10 minutes  
✅ Beautiful professional chart  
✅ Historical data tracking  
✅ Zero manual intervention  
✅ Error handling & logging  
✅ Git auto-commit  

## 📝 Notes

- Workflow runs on GitHub's free tier
- No additional costs or setup required
- Uses GitHub Actions built-in permissions
- Respects API rate limits

---

**Maintained by:** Sunona AI Team  
**Last Updated:** December 29, 2025
