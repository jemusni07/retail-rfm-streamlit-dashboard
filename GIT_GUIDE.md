# Git Commit Guide for RFM Streamlit Dashboard

This guide explains exactly what to commit to GitHub and what to avoid.

## ✅ COMMIT THESE FILES

### Core Application Files
- `main.py` - Your main Streamlit application
- `pyproject.toml` - Project configuration and dependencies
- `requirements.txt` - Python dependencies for deployment

### Deployment Files
- `Dockerfile` - Docker container configuration
- `.dockerignore` - Files to exclude from Docker builds
- `DEPLOYMENT.md` - Deployment instructions

### Configuration Templates
- `env_template.txt` - Template for environment variables (safe to commit)

### Documentation
- `README.md` - Project documentation (if you create one)
- `GIT_GUIDE.md` - This guide

### Version Control
- `.gitignore` - Files to ignore in Git

## ❌ NEVER COMMIT THESE FILES

### Secrets and Environment Variables
- `.env` - Contains your actual Databricks credentials
- `.env.local` - Local environment overrides
- `.env.production` - Production environment variables
- Any file containing actual passwords, API keys, or tokens

### Python Cache and Build Files
- `__pycache__/` - Python bytecode cache
- `*.pyc` - Compiled Python files
- `*.pyo` - Optimized Python files
- `build/` - Build artifacts
- `dist/` - Distribution files
- `*.egg-info/` - Package metadata

### Virtual Environments
- `.venv/` - Your virtual environment
- `venv/` - Alternative virtual environment folder
- `ENV/` - Environment folder

### IDE and Editor Files
- `.vscode/` - VS Code settings
- `.idea/` - PyCharm/IntelliJ settings
- `*.swp` - Vim swap files
- `*.swo` - Vim swap files

### OS Generated Files
- `.DS_Store` - macOS folder metadata
- `Thumbs.db` - Windows thumbnail cache
- `.Trashes` - macOS trash files

### Lock Files (Optional)
- `uv.lock` - UV package manager lock file (some teams commit this, others don't)

## 🚀 Step-by-Step Git Setup

### 1. Initialize Git Repository (if not already done)
```bash
git init
```

### 2. Add Files to Git
```bash
# Add all files that should be committed
git add main.py
git add pyproject.toml
git add requirements.txt
git add Dockerfile
git add .dockerignore
git add DEPLOYMENT.md
git add env_template.txt
git add .gitignore
git add GIT_GUIDE.md
```

### 3. Check What You're About to Commit
```bash
# See what files are staged for commit
git status

# See the actual changes
git diff --cached
```

### 4. Make Your First Commit
```bash
git commit -m "Initial commit: RFM Streamlit Dashboard with deployment configuration"
```

### 5. Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name it `retail-rfm-streamlit-dashboard`
4. Don't initialize with README (you already have files)
5. Click "Create repository"

### 6. Connect Local Repository to GitHub
```bash
# Add GitHub as remote origin
git remote add origin https://github.com/YOUR_USERNAME/retail-rfm-streamlit-dashboard.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

## 🔒 Security Checklist

Before pushing to GitHub, verify:

- [ ] No `.env` file is being committed
- [ ] No actual API keys or passwords in any files
- [ ] Only `env_template.txt` is committed (template file)
- [ ] No virtual environment folders are included
- [ ] No cache files (`__pycache__`) are included
- [ ] No IDE-specific files are included

## 🔍 Verify Your .gitignore is Working

```bash
# Check what files Git is tracking
git ls-files

# Check what files are ignored
git status --ignored
```

## 📝 Future Commits

### When making changes:
```bash
# Check what files have changed
git status

# Add specific files (avoid using git add .)
git add main.py
git add requirements.txt

# Commit with descriptive message
git commit -m "Add new visualization feature"

# Push to GitHub
git push
```

### Good Commit Messages:
- "Add customer segmentation filters"
- "Fix Databricks connection timeout issue"
- "Update deployment documentation"
- "Improve chart styling and colors"

### Bad Commit Messages:
- "fix"
- "update"
- "changes"
- "work in progress"

## 🚨 Common Mistakes to Avoid

1. **Never use `git add .`** - Always add files individually to avoid committing secrets
2. **Don't commit `.env` files** - Even if they seem empty
3. **Check `git status` before every commit** - Make sure you're only committing intended files
4. **Don't commit large files** - Use Git LFS for large datasets if needed
5. **Don't commit temporary files** - Let `.gitignore` handle these

## 🛠️ If You Accidentally Commit Secrets

### If you haven't pushed yet:
```bash
# Remove file from staging
git reset HEAD .env

# Remove file from Git tracking
git rm --cached .env

# Add to .gitignore
echo ".env" >> .gitignore

# Commit the .gitignore change
git add .gitignore
git commit -m "Add .env to .gitignore"
```

### If you already pushed:
1. Remove the file from Git history (this is complex)
2. Change your secrets immediately
3. Consider the repository compromised

## 📋 Quick Reference Commands

```bash
# Check repository status
git status

# See what files are ignored
git check-ignore -v *

# View commit history
git log --oneline

# Create a new branch
git checkout -b feature/new-feature

# Switch back to main
git checkout main

# Merge branch
git merge feature/new-feature
```

Remember: **When in doubt, don't commit it!** It's always safer to ask or check what a file contains before adding it to your repository.
