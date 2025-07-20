# Personal Dev Blog

A modern, fast personal blog built with Hugo and featuring giscus comments for better reader engagement.

## Features

- ⚡ **Fast**: Built with Hugo, one of the fastest static site generators
- 💬 **Comments**: Integrated giscus comments powered by GitHub Discussions
- 📱 **Responsive**: Clean, modern design that works on all devices
- 🚀 **Auto-deploy**: GitHub Actions automatically builds and deploys to GitHub Pages
- 🎨 **Customizable**: Easy to customize theme and styling
- 📊 **SEO Optimized**: Built-in SEO features and meta tags
- ⚛️ **React Apps**: Standalone React applications integrated with the blog

## Tech Stack

- **[Hugo](https://gohugo.io/)**: Static site generator
- **[Stack Theme](https://github.com/CaiJimmy/hugo-theme-stack)**: Clean and modern theme
- **[React](https://react.dev/)**: Interactive applications with Vite
- **[Giscus](https://giscus.app/)**: GitHub Discussions-powered comments
- **[GitHub Pages](https://pages.github.com/)**: Hosting and deployment
- **[GitHub Actions](https://github.com/features/actions)**: CI/CD pipeline

## Quick Start

### Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) (latest version)
- [Git](https://git-scm.com/)
- GitHub account

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/shaharglazner/blog.git
   cd blog
   ```

2. **Initialize submodules**
   ```bash
   git submodule update --init --recursive
   ```

3. **Start the development server**
   ```bash
   hugo server -D
   ```

4. **Open your browser**
   Navigate to `http://localhost:1313` to see your blog

### Creating New Posts

```bash
hugo new posts/your-post-title.md
```

Edit the front matter and content, then save. The post will appear in your blog.

### Creating React Apps

```bash
cd apps
npm create vite@latest my-app -- --template react
cd my-app
npm install
# Update vite.config.js with base: '/apps/my-app/'
```

See [APPS.md](APPS.md) for React apps integration guide and [LOCAL.md](LOCAL.md) for local development workflow.

## Setting Up Giscus Comments

1. **Enable Discussions** in your GitHub repository
   - Go to your repository settings
   - Scroll down to "Features" section
   - Check "Discussions"

2. **Install giscus app**
   - Go to [giscus.app](https://giscus.app/)
   - Follow the setup instructions
   - Install the giscus app on your repository

3. **Get your repository and category IDs**
   - Repository ID: Found in the giscus setup page
   - Category ID: Found in the giscus setup page

4. **Update configuration**
   - Edit `config.toml`
   - Replace the placeholder IDs with your actual IDs:
     ```toml
     [params.comments.giscus]
       repo = "yourusername/your-repo"
       repoId = "your-actual-repo-id"
       categoryId = "your-actual-category-id"
     ```

## Deployment

This blog is automatically deployed to GitHub Pages using GitHub Actions. The workflow:

1. Triggers on pushes to the `main` branch
2. Builds the Hugo site
3. Deploys to GitHub Pages

### Manual Deployment

If you need to deploy manually:

1. **Build the site**
   ```bash
   hugo --minify
   ```

2. **Deploy to GitHub Pages**
   - Push your changes to the `main` branch
   - GitHub Actions will automatically build and deploy

## Configuration

### Site Configuration

Edit `config.toml` to customize:

- Site title and description
- Author information
- Social media links
- Giscus comments settings
- Menu structure

### Theme Customization

The blog uses the Stack theme. You can customize it by:

1. **Creating custom CSS**
   - Create `assets/css/custom.css`
   - Add your custom styles

2. **Modifying theme templates**
   - Copy templates from `themes/hugo-theme-stack/layouts/` to `layouts/`
   - Customize as needed

## File Structure

```
blog/
├── .github/workflows/    # GitHub Actions
├── content/              # Blog content
│   ├── posts/           # Blog posts
│   └── about.md         # About page
├── themes/              # Hugo themes
├── config.toml          # Site configuration
├── .gitmodules          # Git submodules
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you have questions or need help:

- Check the [Hugo documentation](https://gohugo.io/documentation/)
- Visit the [Stack theme repository](https://github.com/CaiJimmy/hugo-theme-stack)
- Read the [giscus documentation](https://github.com/giscus/giscus)

---

**Happy blogging! 🚀**
