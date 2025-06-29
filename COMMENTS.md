# Setting Up Giscus Comments

This guide will help you set up giscus comments for your Hugo blog. Giscus is a comments system powered by GitHub Discussions.

## What is Giscus?

Giscus is a comments system that uses GitHub Discussions as a backend. It's perfect for developer blogs because:
- ✅ No database required
- ✅ Uses your existing GitHub account
- ✅ Privacy-focused (no tracking)
- ✅ Customizable themes
- ✅ Supports reactions and replies

## Prerequisites

Before setting up giscus, ensure you have:
- ✅ GitHub repository with your blog
- ✅ GitHub account with repository access
- ✅ Discussions enabled on your repository

## Step 1: Enable GitHub Discussions

### 1.1 Go to Repository Settings

1. Navigate to your repository: `https://github.com/shahargl/blog`
2. Click on **Settings** tab
3. Scroll down to **Features** section in the left sidebar

### 1.2 Enable Discussions

1. Find **Discussions** checkbox
2. ✅ Check the box to enable Discussions
3. Click **Save**

### 1.3 Create Discussion Category

1. Go to **Discussions** tab in your repository
2. Click **New discussion**
3. You'll be prompted to create a category
4. Create a category called **"Announcements"** (this is what giscus uses by default)
5. Set it as the default category

## Step 2: Install Giscus App

### 2.1 Visit Giscus Setup

1. Go to [giscus.app](https://giscus.app/)
2. You'll see a setup form

### 2.2 Configure Giscus

Fill in the form with your details:

**Repository:**
- Select your repository: `shahargl/blog`

**Discussion Category:**
- Choose: `Announcements` (or the category you created)

**Mapping:**
- Select: `pathname` (recommended for blogs)

**Theme:**
- Choose: `Preferred color scheme` (follows user's system preference)

**Language:**
- Select: `English`

**Position:**
- Choose: `Top` or `Bottom` (your preference)

**Enable reactions:**
- ✅ Check this box

**Enable metadata:**
- ❌ Leave unchecked (for privacy)

**Enable strict mode:**
- ❌ Leave unchecked

### 2.3 Install Giscus App

1. Click **Install giscus** button
2. You'll be redirected to GitHub
3. Click **Install** to authorize giscus for your repository
4. Select your repository: `shahargl/blog`
5. Click **Install**

## Step 3: Get Your Configuration

### 3.1 Copy Configuration

After installation, giscus will show you a configuration snippet. It will look like this:

```html
<script src="https://giscus.app/client.js"
        data-repo="shahargl/blog"
        data-repo-id="R_kgDOKj1234"
        data-category="Announcements"
        data-category-id="DIC_kwDOKj1234"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="top"
        data-theme="preferred_color_scheme"
        data-lang="en"
        crossorigin="anonymous"
        async>
</script>
```

### 3.2 Note Your IDs

Write down these important values:
- **Repository ID**: `R_kgDOKj1234` (your actual ID will be different)
- **Category ID**: `DIC_kwDOKj1234` (your actual ID will be different)

## Step 4: Update Hugo Configuration

### 4.1 Edit config.toml

Update your `config.toml` file with the actual IDs from giscus:

```toml
[params.comments]
  enabled = true
  provider = "giscus"
  
  [params.comments.giscus]
    repo = "shahargl/blog"
    repoId = "YOUR_ACTUAL_REPO_ID"  # Replace with your actual repo ID
    category = "Announcements"
    categoryId = "YOUR_ACTUAL_CATEGORY_ID"  # Replace with your actual category ID
    mapping = "pathname"
    strict = "0"
    reactionsEnabled = "1"
    emitMetadata = "0"
    inputPosition = "top"
    theme = "preferred_color_scheme"
    lang = "en"
    loading = "lazy"
```

### 4.2 Replace Placeholder IDs

Replace the placeholder IDs with your actual values:
- `YOUR_ACTUAL_REPO_ID` → Your actual repository ID
- `YOUR_ACTUAL_CATEGORY_ID` → Your actual category ID

## Step 5: Deploy Changes

### 5.1 Commit and Push

```bash
# Add your changes
git add config.toml

# Commit
git commit -m "Configure giscus comments with actual IDs"

# Push to trigger deployment
git push origin main
```

### 5.2 Wait for Deployment

1. Go to **Actions** tab in your repository
2. Monitor the deployment workflow
3. Wait for it to complete successfully

## Step 6: Test Comments

### 6.1 Visit Your Blog

1. Go to your blog: `https://shahar.blog`
2. Navigate to any blog post
3. Scroll down to see the comments section

### 6.2 Test Commenting

1. Click **Sign in with GitHub** (if not already signed in)
2. Write a test comment
3. Submit the comment
4. Verify it appears on the page

## Troubleshooting

### Common Issues

#### 1. "giscus is not installed on this repository"

**Problem:** Giscus app isn't properly installed

**Solutions:**
- Go to [giscus.app](https://giscus.app/) and reinstall the app
- Check that you selected the correct repository
- Verify the app is installed in your repository settings

#### 2. Comments Don't Appear

**Problem:** Comments section is empty or missing

**Solutions:**
- Check that Discussions are enabled in repository settings
- Verify the category exists and is named "Announcements"
- Check browser console for JavaScript errors
- Verify the repoId and categoryId are correct

#### 3. Wrong Repository ID

**Problem:** Comments are pointing to the wrong repository

**Solution:**
- Go to [giscus.app](https://giscus.app/)
- Select the correct repository
- Copy the new repoId and update config.toml

#### 4. Category Not Found

**Problem:** Category doesn't exist or has wrong name

**Solution:**
- Go to your repository's Discussions tab
- Create a category named "Announcements"
- Update the categoryId in config.toml

### Debugging Steps

#### 1. Check Repository Settings

1. Go to your repository settings
2. **Settings** → **Integrations** → **Installed GitHub Apps**
3. Verify giscus is listed and enabled

#### 2. Check Discussions

1. Go to **Discussions** tab in your repository
2. Verify the "Announcements" category exists
3. Try creating a test discussion

#### 3. Check Browser Console

1. Open browser developer tools (F12)
2. Go to **Console** tab
3. Look for any JavaScript errors related to giscus

#### 4. Verify Configuration

```bash
# Test Hugo build locally
hugo --minify

# Check for configuration errors
hugo check
```

### Getting Your Actual IDs

If you need to find your actual repository and category IDs:

#### Repository ID
1. Go to [giscus.app](https://giscus.app/)
2. Select your repository
3. The repoId will be displayed in the configuration

#### Category ID
1. Go to your repository's Discussions tab
2. Click on the "Announcements" category
3. The category ID will be in the URL or you can get it from giscus setup

## Advanced Configuration

### Custom Themes

You can customize the giscus theme by changing the `theme` parameter:

```toml
[params.comments.giscus]
  theme = "light"           # Light theme
  theme = "dark"            # Dark theme
  theme = "preferred_color_scheme"  # System preference
  theme = "transparent_dark"        # Transparent dark
  theme = "cobalt"                  # Cobalt theme
  theme = "noborder_light"          # Light without border
  theme = "noborder_dark"           # Dark without border
```

### Comment Position

Change where comments appear:

```toml
[params.comments.giscus]
  inputPosition = "top"     # Comments at top
  inputPosition = "bottom"  # Comments at bottom
```

### Reactions

Enable or disable reactions:

```toml
[params.comments.giscus]
  reactionsEnabled = "1"    # Enable reactions
  reactionsEnabled = "0"    # Disable reactions
```

## Best Practices

### 1. Security
- Keep your repository public for giscus to work
- Use HTTPS for your blog (GitHub Pages enforces this)
- Don't share your repoId/categoryId publicly (though they're not sensitive)

### 2. Performance
- Giscus loads asynchronously, so it won't slow down your blog
- Comments are cached by GitHub's CDN
- No database queries needed

### 3. Moderation
- You can moderate comments through GitHub Discussions
- Set up notifications for new comments
- Use GitHub's built-in moderation tools

### 4. Backup
- Comments are stored in GitHub Discussions
- They're automatically backed up with your repository
- You can export discussions if needed

## Support

If you're still having issues:

1. **Check giscus documentation**: [github.com/giscus/giscus](https://github.com/giscus/giscus)
2. **GitHub Discussions help**: [docs.github.com/en/discussions](https://docs.github.com/en/discussions)
3. **Hugo documentation**: [gohugo.io/content-management/comments](https://gohugo.io/content-management/comments)

---

**Your comments system should now be working! 🎉**

Test it by visiting any blog post and leaving a comment. 