# Hugo Blog Makefile
# Common tasks for managing your Hugo blog

.PHONY: help server build clean new-post deploy setup

# Default target
help:
	@echo "Available commands:"
	@echo "  setup      - Initialize the blog (run setup script)"
	@echo "  server     - Start development server"
	@echo "  build      - Build the site for production"
	@echo "  clean      - Clean build artifacts"
	@echo "  new-post   - Create a new blog post"
	@echo "  deploy     - Build and prepare for deployment"
	@echo "  update     - Update Hugo theme"
	@echo "  check      - Check for common issues"

# Initialize the blog
setup:
	@echo "🚀 Setting up Hugo blog..."
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

# Start development server
server:
	@echo "🌐 Starting Hugo development server..."
	@hugo server -D

# Build the site for production
build:
	@echo "🔨 Building site for production..."
	@hugo --minify --gc

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf public/
	@rm -rf resources/
	@rm -rf .hugo_build.lock

# Create a new blog post
new-post:
	@read -p "Enter post title: " title; \
	read -p "Enter post filename (without .md): " filename; \
	hugo new posts/$$filename.md; \
	echo "📝 Created new post: content/posts/$$filename.md"; \
	echo "Edit the front matter and content, then run 'make server' to preview"

# Build and prepare for deployment
deploy:
	@echo "🚀 Building for deployment..."
	@hugo --minify --gc --cleanDestinationDir
	@echo "✅ Site built successfully!"
	@echo "📤 Push to GitHub to deploy:"
	@echo "   git add ."
	@echo "   git commit -m 'Update blog'"
	@echo "   git push origin main"

# Update Hugo theme
update:
	@echo "🔄 Updating Hugo theme..."
	@git submodule update --remote --merge
	@echo "✅ Theme updated!"

# Check for common issues
check:
	@echo "🔍 Checking for common issues..."
	@echo "1. Checking Hugo version..."
	@hugo version
	@echo ""
	@echo "2. Checking if theme exists..."
	@if [ -d "themes/hugo-theme-stack" ]; then \
		echo "✅ Stack theme found"; \
	else \
		echo "❌ Stack theme not found. Run 'make setup'"; \
	fi
	@echo ""
	@echo "3. Checking config.toml..."
	@if [ -f "config.toml" ]; then \
		echo "✅ config.toml found"; \
	else \
		echo "❌ config.toml not found"; \
	fi
	@echo ""
	@echo "4. Checking for posts..."
	@if [ -d "content/posts" ] && [ "$(ls -A content/posts)" ]; then \
		echo "✅ Posts found"; \
		ls content/posts/; \
	else \
		echo "❌ No posts found"; \
	fi

# Install dependencies (if needed)
install:
	@echo "📦 Installing dependencies..."
	@if ! command -v hugo &> /dev/null; then \
		echo "❌ Hugo not found. Please install Hugo:"; \
		echo "   macOS: brew install hugo"; \
		echo "   Linux: https://gohugo.io/installation/"; \
	else \
		echo "✅ Hugo is installed"; \
	fi

# Create a quick post with default content
quick-post:
	@read -p "Enter post title: " title; \
	read -p "Enter post filename (without .md): " filename; \
	read -p "Enter tags (comma-separated): " tags; \
	read -p "Enter category: " category; \
	echo "---" > content/posts/$$filename.md; \
	echo "title: \"$$title\"" >> content/posts/$$filename.md; \
	echo "date: $$(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> content/posts/$$filename.md; \
	echo "draft: false" >> content/posts/$$filename.md; \
	echo "description: \"\"" >> content/posts/$$filename.md; \
	echo "tags: [$$tags]" >> content/posts/$$filename.md; \
	echo "categories: [$$category]" >> content/posts/$$filename.md; \
	echo "---" >> content/posts/$$filename.md; \
	echo "" >> content/posts/$$filename.md; \
	echo "# $$title" >> content/posts/$$filename.md; \
	echo "" >> content/posts/$$filename.md; \
	echo "Your content here..." >> content/posts/$$filename.md; \
	echo "📝 Created new post: content/posts/$$filename.md"

# Show blog statistics
stats:
	@echo "📊 Blog Statistics:"
	@echo "Posts: $$(find content/posts -name "*.md" | wc -l | tr -d ' ')"
	@echo "Pages: $$(find content -name "*.md" | wc -l | tr -d ' ')"
	@echo "Tags: $$(grep -r "tags:" content/ | grep -o '\[.*\]' | tr ',' '\n' | tr -d '[] ' | sort | uniq | wc -l | tr -d ' ')"
	@echo "Categories: $$(grep -r "categories:" content/ | grep -o '\[.*\]' | tr ',' '\n' | tr -d '[] ' | sort | uniq | wc -l | tr -d ' ')" 