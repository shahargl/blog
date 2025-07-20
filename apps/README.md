# React Apps Directory

This directory contains standalone React applications that are integrated with the Hugo blog through the CI/CD pipeline.

## Directory Structure

```
apps/
├── README.md              # This file
├── hello-world/           # Example React app
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   └── dist/             # Build output (auto-generated)
└── your-new-app/         # Future apps follow the same structure
```

## How It Works

1. **Development**: Each app is a standalone React app using Vite
2. **Local Development**: Run `npm run dev` in any app directory
3. **CI/CD Integration**: GitHub Actions automatically builds all apps
4. **Hugo Integration**: Built apps are served at `/apps/{app-name}/`

## Creating a New App

### Option 1: Using Vite (Recommended)

```bash
# Navigate to apps directory
cd apps

# Create new React app with Vite
npm create vite@latest my-new-app -- --template react

# Navigate to the new app
cd my-new-app

# Install dependencies
npm install
```

### Option 2: Copy from Hello World

```bash
# Copy the hello-world app as a template
cp -r apps/hello-world apps/my-new-app

# Navigate to the new app
cd apps/my-new-app

# Install dependencies
npm install

# Update package.json name
# Edit package.json and change "name": "my-new-app"
```

## Required Configuration

Each app must have the following configuration:

### 1. Vite Configuration (`vite.config.js`)

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/apps/your-app-name/',  // Important: must match your app directory name
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: undefined,
      }
    }
  }
})
```

### 2. Package.json Scripts

Your `package.json` must include these scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

## Development Workflow

### Local Development

```bash
# Navigate to your app
cd apps/your-app-name

# Start development server
npm run dev

# Open in browser: http://localhost:5173
```

### Testing the Build

```bash
# Build the app
npm run build

# Preview the built app
npm run preview
```

### Navigation Integration

Add navigation links in your React app to connect back to the blog:

```jsx
// Example navigation in your React component
<div className="navigation">
  <a href="/" className="back-link">← Back to Blog</a>
  <a href="/posts" className="posts-link">View Posts →</a>
</div>
```

## CI/CD Integration

The GitHub Actions workflow automatically:

1. **Detects Apps**: Scans the `apps/` directory for subdirectories with `package.json`
2. **Builds Apps**: Runs `npm ci` and `npm run build` for each app
3. **Copies to Hugo**: Copies built files to `static/apps/{app-name}/`
4. **Hugo Build**: Builds the Hugo site with integrated apps

### Workflow Details

```yaml
- name: Build React Apps
  run: |
    # Find all React apps and build them
    for app_dir in apps/*/; do
      if [ -d "$app_dir" ] && [ -f "$app_dir/package.json" ]; then
        app_name=$(basename "$app_dir")
        cd "$app_dir"
        npm ci
        npm run build
        mkdir -p "../../static/apps/$app_name"
        cp -r dist/* "../../static/apps/$app_name/"
        cd "../.."
      fi
    done
```

## Accessing Your Apps

Once deployed, your apps will be available at:

- **Local Hugo**: `http://localhost:1313/apps/your-app-name/`
- **Production**: `https://yourdomain.com/apps/your-app-name/`

## Hugo Integration

### Adding Apps to the Apps Page

Edit `content/en/apps.md` and `content/he/apps.md` to add your new app:

```markdown
### 🎯 Your New App

Description of what your app does.

**[Launch Your App →](/apps/your-app-name/)**
```

### Navigation Menu

Apps are automatically included in the main navigation through the Hugo configuration.

## Best Practices

### 1. App Structure

- Keep each app self-contained
- Use meaningful app names (kebab-case)
- Include a clear description in package.json
- Add navigation back to the blog

### 2. Styling

- Use a consistent color scheme
- Make apps responsive (mobile-friendly)
- Consider the blog's overall design language
- Add proper loading states

### 3. Performance

- Use Vite's built-in optimizations
- Implement code splitting for larger apps
- Optimize images and assets
- Test build sizes

### 4. Dependencies

- Keep dependencies minimal and up-to-date
- Use the same React version across apps when possible
- Avoid conflicting global styles

## Troubleshooting

### Build Fails in CI/CD

1. **Check package.json**: Ensure all required scripts exist
2. **Test locally**: Run `npm run build` in your app directory
3. **Check dependencies**: Ensure all dependencies are in package.json
4. **Review logs**: Check GitHub Actions logs for specific errors

### App Not Loading

1. **Check base path**: Ensure `vite.config.js` has correct base URL
2. **Verify build output**: Check that files exist in `/static/apps/your-app/`
3. **Check Hugo build**: Ensure Hugo successfully builds with your app

### Navigation Issues

1. **Relative paths**: Use absolute paths for navigation (`/` not `./`)
2. **Hugo URLs**: Match the URL structure Hugo expects
3. **Multi-language**: Consider both English and Hebrew navigation

## Example Apps

### Hello World (`apps/hello-world/`)

A comprehensive example demonstrating:
- React hooks (useState, useEffect)
- Real-time updates
- Interactive components
- Modern styling
- Blog navigation integration

Use this as a reference for creating new apps.

## Contributing

When adding new apps:

1. Follow the structure and conventions outlined here
2. Test locally before committing
3. Update the apps page content
4. Consider adding documentation for complex apps
5. Ensure responsive design

## Support

For issues or questions:
- Check this documentation first
- Review the hello-world app as an example
- Check GitHub Actions logs for CI/CD issues
- Refer to the main blog README.md

---

**Happy app building! 🚀** 