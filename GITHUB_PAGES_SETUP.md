# GitHub Pages Setup - Final Steps

✅ **Files have been committed to the `gh-pages` branch locally!**

## Step 1: Push to GitHub

Run this command in your terminal:

```bash
cd /Users/krishmishra/Desktop/Agent
git push origin gh-pages
```

If you get authentication issues, you may need to use a personal access token or SSH.

## Step 2: Enable GitHub Pages

1. Go to your GitHub repository: https://github.com/krishmishraghub/The_Mind_Studio
2. Click on **Settings** (top right of the repository page)
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select:
   - **Deploy from a branch**
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
5. Click **Save**

## Step 3: Access Your Website

After enabling Pages, GitHub will provide you with a URL like:
- `https://krishmishraghub.github.io/The_Mind_Studio/`

**Note:** It may take a few minutes (2-10 minutes) for the site to become available after enabling Pages.

## Troubleshooting

- If the site doesn't load, check the **Actions** tab in your GitHub repository for build/deployment status
- Make sure the `gh-pages` branch is pushed successfully
- Verify that `index.html` is in the root of the `gh-pages` branch

## Alternative: Use a Custom Domain

After deployment, you can add a custom domain in the same Pages settings if needed.

---

**Quick Command Summary:**
```bash
# Make sure you're on gh-pages branch
git checkout gh-pages

# Push to GitHub (if not already done)
git push origin gh-pages
```

