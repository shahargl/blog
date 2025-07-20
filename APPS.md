# React Apps Integration

This Hugo blog supports standalone React applications that are automatically built and deployed alongside the blog content.

## Quick Start

### Create a New App

```bash
# Navigate to apps directory
cd apps

# Create new React app
npm create vite@latest my-app -- --template react

# Configure the app
cd my-app
npm install

# Update vite.config.js base path
# base: '/apps/my-app/'
```

### Local Development

```bash
# Develop the app locally
cd apps/my-app
npm run dev

# Test the app build
npm run build

# Run the Hugo blog locally
hugo server -D
```

### Deploy

```bash
# Commit and push to main
git add .
git commit -m "Add new React app: my-app"
git push origin main

# GitHub Actions will automatically:
# 1. Build all React apps
# 2. Copy to Hugo static directory  
# 3. Build and deploy Hugo site
```

## How It Works

1. **Apps Directory**: All React apps live in `apps/`
2. **Standalone Development**: Each app can be developed independently
3. **Automatic Building**: CI/CD builds all apps and integrates with Hugo
4. **Static Hosting**: Apps are served at `/apps/{app-name}/`

## Key Files

- `apps/README.md` - Detailed documentation
- `apps/hello-world/` - Example React app
- `.github/workflows/deploy.yml` - CI/CD pipeline
- `content/en/apps.md` - Apps showcase page

## Features

- ✅ **Independent Development**: `npm run dev` in any app directory
- ✅ **Automatic CI/CD**: GitHub Actions builds and deploys everything
- ✅ **Hugo Integration**: Apps served through the blog
- ✅ **Modern Tooling**: Vite for fast development and optimized builds
- ✅ **Navigation**: Seamless integration with blog navigation

## Example: Hello World App

Visit `/apps/hello-world/` to see a fully functional React app integrated with the blog.

## Documentation

For complete documentation, see:
- [Apps README](apps/README.md) - Comprehensive guide
- [LOCAL.md](LOCAL.md) - Local development workflow
- [Main README](README.md) - Blog setup and deployment

---

**Start building interactive experiences for your blog! 🚀** 