# Deploying Your Hugo Blog to GitHub Pages

This guide provides detailed instructions for deploying your Hugo blog to GitHub Pages using GitHub Actions.

## Prerequisites

Before deploying, ensure you have:

- ✅ Hugo blog set up and working locally
- ✅ GitHub repository created and pushed to GitHub
- ✅ GitHub account with repository access
- ✅ Hugo Extended version installed (for GitHub Actions)

## Step 1: Prepare Your Repository

### 1.1 Update Configuration

Edit `config.toml` and update the `baseURL` to match your GitHub Pages URL:

```toml
# For repository-based GitHub Pages (recommended)
baseURL = 'https://shahargl.github.io/blog/'

# For user/organization GitHub Pages
# baseURL = 'https://yourusername.github.io/'
```

**Important:** The baseURL must match your GitHub Pages URL exactly, including the trailing slash.

### 1.2 Verify GitHub Actions Workflow

Ensure the `.github/workflows/deploy.yml` file exists and contains the correct configuration:

```yaml
name: Deploy Hugo site to Pages

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

defaults:
  run:
    shell: bash

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0

      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v4

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true

      - name: Build with Hugo
        env:
          HUGO_ENVIRONMENT: production
          HUGO_ENV: production
        run: |
          hugo \
            --gc \
            --minify \
            --baseURL "${{ steps.pages.outputs.base_url }}/"

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Step 2: Configure GitHub Pages

### 2.1 Enable GitHub Pages

1. Go to your GitHub repository
2. Click on **Settings** tab
3. Scroll down to **Pages** section in the left sidebar
4. Under **Source**, select **GitHub Actions**
5. Click **Save**

### 2.2 Configure Repository Settings

1. In the same **Settings** page, scroll down to **Features** section
2. Enable **Discussions** (required for giscus comments)
3. Click **Save**

### 2.3 Set Repository Permissions

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**
4. Click **Save**

## Step 3: Deploy Your Blog

### 3.1 Push to GitHub

```bash
# Add all files to git
git add .

# Commit your changes
git commit -m "Initial blog deployment"

# Push to main branch
git push origin main
```

### 3.2 Monitor Deployment

1. Go to your repository on GitHub
2. Click on **Actions** tab
3. You should see a workflow running called "Deploy Hugo site to Pages"
4. Click on the workflow to monitor its progress

### 3.3 Verify Deployment

Once the workflow completes successfully:

1. Go to **Settings** → **Pages**
2. You should see a green checkmark indicating successful deployment
3. Your site URL will be displayed (e.g., `https://yourusername.github.io/your-repo-name/`)
4. Click the URL to visit your live blog

## Step 4: Set Up Custom Domain (Optional)

### 4.1 Configure Custom Domain

1. Go to **Settings** → **Pages**
2. Under **Custom domain**, enter your domain (e.g., `blog.yourdomain.com`)
3. Check **Enforce HTTPS**
4. Click **Save**

### 4.2 Update DNS Records

Add a CNAME record in your domain's DNS settings:

```
Type: CNAME
Name: blog (or @ for root domain)
Value: yourusername.github.io
TTL: 3600
```

### 4.3 Update Hugo Configuration

Update `config.toml` with your custom domain:

```toml
baseURL = 'https://blog.yourdomain.com/'
```

## Step 5: Configure Giscus Comments

### 5.1 Install Giscus App

1. Go to [giscus.app](https://giscus.app/)
2. Follow the setup instructions:
   - Select your repository
   - Choose "Announcements" as the discussion category
   - Select "pathname" as the mapping
   - Choose your preferred theme
   - Copy the generated configuration

### 5.2 Update Configuration

Edit `config.toml` and update the giscus section with your actual IDs:

```toml
[params.comments]
  enabled = true
  provider = "giscus"
  
  [params.comments.giscus]
    repo = "shahargl/blog"
    repoId = "your-actual-repo-id"
    category = "Announcements"
    categoryId = "your-actual-category-id"
    mapping = "pathname"
    strict = "0"
    reactionsEnabled = "1"
    emitMetadata = "0"
    inputPosition = "top"
    theme = "preferred_color_scheme"
    lang = "en"
    loading = "lazy"
```

### 5.3 Redeploy

After updating the configuration:

```bash
git add .
git commit -m "Configure giscus comments"
git push origin main
```

## Step 6: Continuous Deployment

### 6.1 Automatic Deployment

Your blog will automatically deploy whenever you:

- Push changes to the `main` branch
- Create a pull request to the `main` branch
- Manually trigger the workflow

### 6.2 Manual Deployment

To manually trigger deployment:

1. Go to **Actions** tab in your repository
2. Click on "Deploy Hugo site to Pages"
3. Click **Run workflow**
4. Select the branch and click **Run workflow**

## Troubleshooting

### Common Issues

#### 1. Build Failures

**Problem:** GitHub Actions workflow fails during build

**Solutions:**
- Check that Hugo Extended is specified in the workflow
- Verify all required files are committed
- Check the Actions logs for specific error messages

```yaml
- name: Setup Hugo
  uses: peaceiris/actions-hugo@v2
  with:
    hugo-version: 'latest'
    extended: true  # Make sure this is set
```

#### 2. Theme Not Found

**Problem:** Hugo can't find the Stack theme

**Solution:** Ensure the theme submodule is properly initialized

```bash
git submodule update --init --recursive
```

#### 3. Wrong Base URL

**Problem:** Links and assets don't work correctly

**Solution:** Verify the baseURL in `config.toml` matches your GitHub Pages URL exactly

```toml
# For repository-based pages
baseURL = 'https://yourusername.github.io/your-repo-name/'

# For user/organization pages
baseURL = 'https://yourusername.github.io/'
```

#### 4. Giscus Comments Not Showing

**Problem:** Comments don't appear on blog posts

**Solutions:**
- Verify Discussions are enabled in repository settings
- Check that giscus app is installed on your repository
- Verify repoId and categoryId are correct
- Check browser console for JavaScript errors

#### 5. 404 Errors

**Problem:** Pages return 404 errors

**Solutions:**
- Check that the baseURL is correct
- Verify all content files are committed
- Check that the GitHub Actions workflow completed successfully
- Clear browser cache and try again

### Debugging Commands

```bash
# Test build locally
hugo --minify

# Check Hugo version
hugo version

# Validate configuration
hugo check

# Build with verbose output
hugo --minify --verbose
```

### Getting Help

If you encounter issues:

1. **Check GitHub Actions logs** - Go to Actions tab and view workflow logs
2. **Verify local build** - Run `hugo --minify` locally to test
3. **Check Hugo documentation** - [Hugo Documentation](https://gohugo.io/documentation/)
4. **Review GitHub Pages docs** - [GitHub Pages Documentation](https://docs.github.com/en/pages)
5. **Check giscus docs** - [Giscus Documentation](https://github.com/giscus/giscus)

## Best Practices

### 1. Regular Updates

- Keep Hugo updated to the latest version
- Regularly update the Stack theme
- Monitor GitHub Actions for any issues

### 2. Content Management

- Use descriptive commit messages
- Preview changes locally before pushing
- Keep content organized in appropriate directories

### 3. Performance

- Optimize images before adding to posts
- Use Hugo's built-in minification
- Monitor site performance with tools like Google PageSpeed Insights

### 4. Security

- Keep dependencies updated
- Use HTTPS (enforced by GitHub Pages)
- Regularly review repository permissions

## Monitoring and Maintenance

### 1. Check Deployment Status

Regularly check:
- GitHub Actions workflow status
- GitHub Pages deployment status
- Site availability and performance

### 2. Update Dependencies

```bash
# Update Hugo theme
git submodule update --remote

# Update Hugo locally
brew upgrade hugo  # macOS
```

### 3. Backup Content

Regularly backup your content:
- Commit all changes to git
- Consider using GitHub's backup features
- Keep local copies of important content

---

**Your blog is now deployed and ready for the world! 🌍**

For additional help or questions, refer to the main [README.md](README.md) or [SETUP.md](SETUP.md) files. 