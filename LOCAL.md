# Local Development Guide

This guide explains how to develop React apps locally and run them through Hugo for testing the full integration.

## Prerequisites

- [Hugo Extended](https://gohugo.io/installation/) installed
- [Node.js](https://nodejs.org/) (version 18+) installed
- Git and this repository cloned locally

## Local Development Workflow

### Option 1: Quick Setup (Recommended)

Use the Makefile commands for the easiest experience:

```bash
# Build all React apps and start Hugo server
make local

# Or step by step:
make build-apps    # Build all React apps
make server        # Start Hugo development server
```

### Option 2: Manual Setup

If you prefer to understand each step:

#### Step 1: Build React Apps

```bash
# Build all apps at once
npm run build:apps

# Or build individual apps:
cd apps/hello-world
npm install  # If not already installed
npm run build
cd ../..

# For each additional app:
# cd apps/your-app-name
# npm install
# npm run build
# cd ../..
```

#### Step 2: Copy Apps to Hugo Static Directory

```bash
# Create static directories
mkdir -p static/apps

# Copy built apps
cp -r apps/hello-world/dist/* static/apps/hello-world/

# For additional apps:
# mkdir -p static/apps/your-app-name
# cp -r apps/your-app-name/dist/* static/apps/your-app-name/
```

#### Step 3: Start Hugo Development Server

```bash
# Start Hugo server
hugo server -D

# Or use the Makefile
make server
```

#### Step 4: Access Your Apps

- **Blog**: http://localhost:1313
- **Apps Page**: http://localhost:1313/apps/
- **Hello World App**: http://localhost:1313/apps/hello-world/
- **Your Apps**: http://localhost:1313/apps/your-app-name/

## Development Modes

### 1. React App Development

When actively developing a React app, run it in development mode:

```bash
cd apps/hello-world
npm run dev
```

This runs the React app at http://localhost:5173 with:
- ✅ Hot Module Replacement (HMR)
- ✅ Fast refresh
- ✅ Instant updates
- ✅ Development error overlay

### 2. Integration Testing

When testing how the app works within Hugo:

```bash
# Build the app
cd apps/hello-world
npm run build
cd ../..

# Copy to Hugo static directory
cp -r apps/hello-world/dist/* static/apps/hello-world/

# Start Hugo server
hugo server -D
```

Visit http://localhost:1313/apps/hello-world/ to see how it integrates with the blog.

### 3. Full Local Build

To simulate the CI/CD pipeline locally:

```bash
# Build all apps
make build-apps

# Build Hugo site
make build

# Serve the built site
hugo server --source public
```

## NPM Scripts

The root `package.json` includes convenient scripts for managing React apps:

```json
{
  "scripts": {
    "build:apps": "for dir in apps/*/; do if [ -f \"$dir/package.json\" ]; then echo \"Building $(basename \"$dir\")\"; cd \"$dir\" && npm install && npm run build && cd ../..; fi; done",
    "copy:apps": "mkdir -p static/apps && for dir in apps/*/; do if [ -d \"$dir/dist\" ]; then app_name=$(basename \"$dir\"); echo \"Copying $app_name\"; mkdir -p \"static/apps/$app_name\" && cp -r \"$dir/dist/*\" \"static/apps/$app_name/\" 2>/dev/null || cp -r \"$dir/dist/.\" \"static/apps/$app_name/\"; fi; done",
    "local": "npm run build:apps && npm run copy:apps && hugo server -D",
    "clean:apps": "rm -rf static/apps && find apps -name 'dist' -type d -exec rm -rf {} + 2>/dev/null || true"
  }
}
```

Then you can use:

```bash
npm run local        # Build apps and start Hugo server
npm run build:apps   # Build all React apps
npm run copy:apps    # Copy built apps to Hugo static
npm run clean:apps   # Clean all built files
```

## File Watching and Auto-Reload

### Hugo Auto-Reload

Hugo automatically reloads when:
- ✅ Content files (`.md`) change
- ✅ Layout templates change
- ✅ Configuration changes
- ✅ Static files change (including React apps)

### React App Auto-Copy

For automatic copying of React apps during development, you can use file watchers:

```bash
# Install nodemon globally
npm install -g nodemon

# Watch for React app changes and auto-copy
nodemon --watch apps/hello-world/dist --ext js,css,html --exec "cp -r apps/hello-world/dist/* static/apps/hello-world/"
```

## Troubleshooting

### React App Not Showing

1. **Check build output**:
   ```bash
   ls -la apps/hello-world/dist/
   ```

2. **Verify copy operation**:
   ```bash
   ls -la static/apps/hello-world/
   ```

3. **Check Hugo static directory**:
   ```bash
   hugo server -D --verbose
   ```

### Build Errors

1. **Check Node.js version**:
   ```bash
   node --version  # Should be 18+
   ```

2. **Clean and rebuild**:
   ```bash
   cd apps/hello-world
   rm -rf node_modules dist
   npm install
   npm run build
   ```

3. **Check for dependency issues**:
   ```bash
   npm audit
   npm audit fix
   ```

### Hugo Not Finding Apps

1. **Verify Hugo version**:
   ```bash
   hugo version  # Should include "extended"
   ```

2. **Check static directory structure**:
   ```bash
   tree static/  # or ls -R static/
   ```

3. **Test Hugo build**:
   ```bash
   hugo --minify --gc --verbose
   ```

## Performance Tips

### 1. Parallel Building

Build multiple apps in parallel:

```bash
# Build apps in parallel (if you have multiple apps)
cd apps/hello-world && npm run build &
cd apps/another-app && npm run build &
wait  # Wait for all background jobs to complete
```

### 2. Incremental Builds

Only rebuild changed apps:

```bash
# Check if app needs rebuilding
if [ apps/hello-world/src -nt static/apps/hello-world/index.html ]; then
  echo "Rebuilding hello-world..."
  cd apps/hello-world && npm run build && cd ../..
  cp -r apps/hello-world/dist/* static/apps/hello-world/
fi
```

### 3. Development vs Production

Use different build commands for development:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "build:dev": "vite build --mode development"
  }
}
```

## Best Practices

### 1. Development Workflow

1. **Start with React development**: Use `npm run dev` for active development
2. **Test integration regularly**: Build and test through Hugo
3. **Use version control**: Commit frequently during development
4. **Test builds locally**: Before pushing to CI/CD

### 2. File Organization

```
project/
├── apps/
│   ├── hello-world/
│   │   ├── src/           # React source
│   │   ├── dist/          # Built files (auto-generated)
│   │   └── package.json
│   └── another-app/
├── static/
│   └── apps/              # Copied from apps/*/dist/
│       ├── hello-world/
│       └── another-app/
└── content/
    └── en/
        └── apps.md        # Apps showcase page
```

### 3. Git Ignore

Make sure your `.gitignore` includes:

```gitignore
# React build outputs
apps/*/dist/
apps/*/node_modules/

# Hugo outputs
public/
resources/

# Static app copies (optional - these are auto-generated)
static/apps/
```

## Integration Testing

### 1. Test Navigation

- ✅ Blog → Apps page
- ✅ Apps page → Individual apps  
- ✅ Individual apps → Back to blog
- ✅ Multi-language navigation

### 2. Test Responsive Design

```bash
# Start Hugo server
hugo server -D

# Test different screen sizes in browser dev tools
# Test on actual mobile devices
```

### 3. Test Performance

```bash
# Build optimized version
hugo --minify --gc

# Test with browser dev tools
# Check Lighthouse scores
# Monitor bundle sizes
```

## Automation Scripts

### Build and Watch Script

Create `scripts/local-dev.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting local development..."

# Build all React apps
echo "📦 Building React apps..."
for dir in apps/*/; do
  if [ -f "$dir/package.json" ]; then
    app_name=$(basename "$dir")
    echo "Building $app_name..."
    cd "$dir"
    npm install
    npm run build
    cd ../..
    
    # Copy to static directory
    mkdir -p "static/apps/$app_name"
    cp -r "$dir/dist/"* "static/apps/$app_name/"
    echo "✅ $app_name built and copied"
  fi
done

echo "🌐 Starting Hugo development server..."
hugo server -D
```

Make it executable and run:

```bash
chmod +x scripts/local-dev.sh
./scripts/local-dev.sh
```

---

**Happy local development! 🚀**

For more information, see:
- [Apps README](apps/README.md) - Complete React apps documentation
- [Main README](README.md) - Blog setup and deployment
- [APPS.md](APPS.md) - Quick reference for React apps integration 