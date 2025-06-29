# Quick Start Guide

Get your Hugo blog up and running in 5 minutes!

## 🚀 Immediate Setup

### 1. Run the Setup Script
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Start the Development Server
```bash
hugo server -D
```

Visit `http://localhost:1313` to see your blog!

## 📝 Create Your First Post

```bash
# Using Hugo command
hugo new posts/my-first-post.md

# Or use the Makefile
make new-post
```

## 🔧 Essential Configuration

### Update `config.toml`
Change these values in `config.toml`:

```toml
baseURL = 'https://yourusername.github.io/your-repo-name/'
title = 'Your Name - Dev Blog'
[params]
  author = "Your Name"
  github = "your-github-username"
```

### Set Up Giscus Comments
1. Enable **Discussions** in your GitHub repository settings
2. Go to [giscus.app](https://giscus.app/) and follow setup
3. Update the giscus section in `config.toml` with your IDs

## 🚀 Deploy to GitHub Pages

```bash
git add .
git commit -m "Initial blog setup"
git push origin main
```

GitHub Actions will automatically deploy your site!

## 📚 Useful Commands

```bash
# Start development server
make server
# or
hugo server -D

# Build for production
make build
# or
hugo --minify

# Create new post
make new-post

# Check for issues
make check

# Update theme
make update
```

## 🎯 What's Included

- ✅ **Hugo Static Site Generator**
- ✅ **Stack Theme** (clean, modern design)
- ✅ **Giscus Comments** (GitHub Discussions-powered)
- ✅ **GitHub Actions** (automatic deployment)
- ✅ **Example Blog Posts** (2 comprehensive posts)
- ✅ **Custom CSS** (responsive design)
- ✅ **About Page**
- ✅ **Setup Scripts** (automated setup)
- ✅ **Makefile** (common tasks)

## 📖 Next Steps

1. **Customize**: Edit `config.toml` and `assets/css/custom.css`
2. **Write**: Create new posts in `content/posts/`
3. **Deploy**: Push to GitHub for automatic deployment
4. **Engage**: Enable comments and interact with readers

## 🆘 Need Help?

- 📖 **Full Setup Guide**: See `SETUP.md`
- 📚 **Documentation**: See `README.md`
- 🔧 **Troubleshooting**: Run `make check`

---

**Your blog is ready! Happy blogging! 🎉** 