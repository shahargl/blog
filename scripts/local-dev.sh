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