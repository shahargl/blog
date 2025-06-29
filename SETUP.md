# Hugo Blog Setup Guide

This guide will walk you through setting up your Hugo blog with giscus comments and GitHub Pages deployment.

## Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) (latest version)
- [Git](https://git-scm.com/)
- GitHub account
- Basic knowledge of Markdown and YAML/TOML

## Step 1: Initial Setup

### Option A: Use the Setup Script (Recommended)

```bash
# Make the script executable and run it
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option B: Manual Setup

1. **Initialize git repository** (if not already done):
   ```bash
   git init
   ```

2. **Add the Stack theme as a submodule**:
   ```bash
   git submodule add https://github.com/CaiJimmy/hugo-theme-stack.git themes/hugo-theme-stack
   git submodule update --init --recursive
   ```

3. **Test the setup**:
   ```bash
   hugo server -D
   ```
   Visit `http://localhost:1313` to see your blog.

## Step 2: Configure Your Blog

### Update `config.toml`

Edit the `config.toml` file with your information:

```toml
baseURL = 'https://yourusername.github.io/your-repo-name/'
languageCode = 'en-us'
title = 'Your Name - Dev Blog'
theme = 'hugo-theme-stack'

[params]
  description = "Your blog description"
  
  # Author configuration
  [params.author]
    name = "Your Name"
    email = "your-email@example.com"
    link = "https://github.com/yourusername"
  
  # Update social links
  github = "your-github-username"
  twitter = "your-twitter-handle"
  linkedin = "your-linkedin-profile"
```

### Important Notes:

- **baseURL**: Must match your GitHub Pages URL exactly
- **title**: Your blog's title
- **author**: Your name, email, and link
- **social links**: Update with your actual social media profiles

## Step 3: Set Up Giscus Comments

### 1. Enable Discussions in Your Repository

1. Go to your GitHub repository
2. Click on **Settings**
3. Scroll down to **Features** section
4. Check **Discussions** to enable it
5. Click **Save**

### 2. Install Giscus App

1. Go to [giscus.app](https://giscus.app/)
2. Follow the setup instructions:
   - Select your repository
   - Choose "Announcements" as the discussion category
   - Select "pathname" as the mapping
   - Choose your preferred theme
   - Copy the generated configuration

### 3. Get Your Repository and Category IDs

From the giscus setup page, you'll get:
- **Repository ID**: A string like `R_kgDOKj1234`
- **Category ID**: A string like `DIC_kwDOKj1234`

### 4. Update Giscus Configuration

Edit `config.toml` and update the giscus section:

```toml
[params.comments]
  enabled = true
  provider = "giscus"
  
  [params.comments.giscus]
    repo = "yourusername/your-repo-name"
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

## Step 4: Create Your First Post

### Using Hugo Command

```bash
hugo new posts/my-first-post.md
```

### Manual Creation

Create a new file in `content/posts/` with the following structure:

```markdown
---
title: "Your Post Title"
date: 2024-01-15T10:00:00-05:00
draft: false
description: "A brief description of your post"
tags: ["tag1", "tag2"]
categories: ["category1"]
---

# Your Post Title

Your content here...

## Section 1

More content...

## Section 2

Even more content...
```

## Step 5: Test Locally

```bash
# Start the development server
hugo server -D

# Or build the site
hugo --minify
```

Visit `http://localhost:1313` to preview your blog.

## Step 6: Deploy to GitHub Pages

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial blog setup"
git push origin main
```

### 2. Configure GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings**
3. Scroll down to **Pages** section
4. Under **Source**, select **GitHub Actions**
5. The workflow will automatically deploy your site

### 3. Verify Deployment

After pushing to the main branch, GitHub Actions will:
1. Build your Hugo site
2. Deploy it to GitHub Pages
3. Make it available at `https://yourusername.github.io/your-repo-name/`

## Step 7: Customization

### Custom CSS

Edit `assets/css/custom.css` to add your own styles.

### Theme Customization

1. Copy templates from `themes/hugo-theme-stack/layouts/` to `layouts/`
2. Customize the copied templates
3. Your changes will override the theme defaults

### Adding Pages

Create new pages in the `content/` directory:

```bash
# Create an about page
hugo new about.md

# Create a contact page
hugo new contact.md
```

## Troubleshooting

### Common Issues

1. **Theme not found**:
   ```bash
   git submodule update --init --recursive
   ```

2. **Giscus comments not showing**:
   - Verify Discussions are enabled in your repository
   - Check that giscus app is installed
   - Verify repoId and categoryId are correct

3. **GitHub Pages not working**:
   - Check that the baseURL in `config.toml` matches your GitHub Pages URL
   - Verify the GitHub Actions workflow is running
   - Check the Actions tab for any errors

4. **Local development issues**:
   ```bash
   # Clear Hugo cache
   hugo --gc
   
   # Check Hugo version
   hugo version
   ```

### Getting Help

- [Hugo Documentation](https://gohugo.io/documentation/)
- [Stack Theme Documentation](https://github.com/CaiJimmy/hugo-theme-stack)
- [Giscus Documentation](https://github.com/giscus/giscus)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

## Next Steps

1. **Write more posts**: Start creating content regularly
2. **Customize the theme**: Make it your own
3. **Add analytics**: Consider adding Google Analytics or Plausible
4. **SEO optimization**: Add meta tags and structured data
5. **Social sharing**: Add Open Graph tags for better social media sharing

## Maintenance

### Regular Tasks

1. **Update Hugo**: Keep Hugo updated to the latest version
2. **Update theme**: Pull latest changes from the Stack theme
3. **Backup content**: Regularly backup your content directory
4. **Monitor performance**: Check site speed and performance

### Commands

```bash
# Update Hugo theme
git submodule update --remote

# Build for production
hugo --minify

# Check for broken links
hugo --minify --gc --cleanDestinationDir
```

---

**Happy blogging! 🚀**

If you have any questions or need help, feel free to open an issue in the repository or leave a comment on any blog post. 