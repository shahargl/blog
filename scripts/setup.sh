#!/bin/bash

# Hugo Blog Setup Script
# This script helps set up a new Hugo blog with the Stack theme

set -e

echo "🚀 Setting up Hugo blog with Stack theme..."

# Check if Hugo is installed
if ! command -v hugo &> /dev/null; then
    echo "❌ Hugo is not installed. Please install Hugo first:"
    echo "   macOS: brew install hugo"
    echo "   Linux: https://gohugo.io/installation/"
    exit 1
fi

echo "✅ Hugo is installed"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
fi

# Add the Stack theme as a submodule
echo "🎨 Adding Stack theme..."
if [ ! -d "themes/hugo-theme-stack" ]; then
    git submodule add https://github.com/CaiJimmy/hugo-theme-stack.git themes/hugo-theme-stack
else
    echo "✅ Stack theme already exists"
fi

# Update submodules
echo "🔄 Updating submodules..."
git submodule update --init --recursive

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p content/posts
mkdir -p assets/css
mkdir -p layouts/partials

# Create custom CSS file
echo "🎨 Creating custom CSS file..."
cat > assets/css/custom.css << 'EOF'
/* Custom styles for your blog */
/* Add your custom CSS here */

/* Example: Custom link colors */
a {
    color: #007acc;
    text-decoration: none;
}

a:hover {
    color: #005a9e;
    text-decoration: underline;
}

/* Example: Custom code block styling */
pre {
    border-radius: 8px;
    border: 1px solid #e1e4e8;
}

/* Example: Custom blockquote styling */
blockquote {
    border-left: 4px solid #007acc;
    padding-left: 1rem;
    margin-left: 0;
    font-style: italic;
}
EOF

echo "✅ Custom CSS file created"

# Create a sample post
echo "📝 Creating sample post..."
if [ ! -f "content/posts/welcome.md" ]; then
    cat > content/posts/welcome.md << 'EOF'
---
title: "Welcome to My Blog"
date: 2024-01-15T10:00:00-05:00
draft: false
description: "Welcome to my new blog built with Hugo and giscus comments."
tags: ["welcome", "first-post"]
categories: ["general"]
---

# Welcome to My Blog! 🎉

Hello and welcome to my new blog! This is my first post using Hugo and giscus comments.

## What to Expect

I'll be writing about:
- Software development and programming
- Web technologies and frameworks
- Best practices and lessons learned
- Personal projects and experiences

## About This Blog

This blog is built with:
- **[Hugo](https://gohugo.io/)**: Fast static site generator
- **[Stack Theme](https://github.com/CaiJimmy/hugo-theme-stack)**: Clean and modern design
- **[Giscus](https://giscus.app/)**: GitHub Discussions-powered comments

## Get Started

Feel free to:
- Leave comments on posts
- Connect with me on social media
- Share your thoughts and experiences

Thanks for visiting! I'm excited to share my journey with you.

---

*What topics would you like me to write about? Let me know in the comments below!*
EOF
    echo "✅ Sample post created"
else
    echo "✅ Sample post already exists"
fi

# Instructions for giscus setup
echo ""
echo "🔧 Next Steps:"
echo "1. Update config.toml with your information:"
echo "   - Change baseURL to your GitHub Pages URL"
echo "   - Update author name, email, and social links"
echo "   - Configure giscus comments (see README.md for instructions)"
echo ""
echo "2. Set up giscus comments:"
echo "   - Enable Discussions in your GitHub repository"
echo "   - Install giscus app from https://giscus.app/"
echo "   - Update repoId and categoryId in config.toml"
echo ""
echo "3. Test locally:"
echo "   hugo server -D"
echo ""
echo "4. Deploy to GitHub Pages:"
echo "   - Push to main branch"
echo "   - GitHub Actions will automatically deploy"
echo ""
echo "🎉 Setup complete! Happy blogging!" 