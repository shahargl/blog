---
title: "Getting Started with Hugo and Giscus Comments"
date: 2024-01-15T10:00:00-05:00
draft: false
description: "A comprehensive guide to setting up a personal blog with Hugo and integrating giscus comments for better reader engagement."
tags: ["hugo", "giscus", "blog", "web-development"]
categories: ["tutorials"]
---

# Getting Started with Hugo and Giscus Comments

Building a personal blog can be an exciting journey, especially when you choose the right tools. In this post, I'll walk you through setting up a Hugo-based blog with giscus comments integration for better reader engagement.

## Why Hugo?

Hugo is a fast, modern static site generator written in Go. It's perfect for blogs because:

- **Speed**: Hugo is incredibly fast, generating thousands of pages in seconds
- **Simplicity**: No complex build processes or dependencies
- **Flexibility**: Extensive theming and customization options
- **GitHub Pages Ready**: Perfect for hosting on GitHub Pages

## Why Giscus?

Giscus is a comments system powered by GitHub Discussions. It's ideal for developer blogs because:

- **GitHub Integration**: Uses your existing GitHub account
- **No Database**: Comments are stored as GitHub Discussions
- **Privacy Focused**: No tracking or ads
- **Customizable**: Easy to style and configure

## Setting Up Hugo

First, install Hugo on your system:

```bash
# macOS with Homebrew
brew install hugo

# Or download from GitHub releases
# https://github.com/gohugoio/hugo/releases
```

Create a new Hugo site:

```bash
hugo new site my-blog
cd my-blog
```

## Installing a Theme

For this blog, I'm using the Stack theme, which is clean and modern:

```bash
git init
git submodule add https://github.com/CaiJimmy/hugo-theme-stack/ themes/hugo-theme-stack
```

## Configuration

The `config.toml` file is the heart of your Hugo site. Here's a basic configuration:

```toml
baseURL = 'https://yourusername.github.io/your-repo/'
languageCode = 'en-us'
title = 'Your Blog Title'
theme = 'hugo-theme-stack'

[params]
  description = "Your blog description"
  author = "Your Name"
  
  [params.comments]
    enabled = true
    provider = "giscus"
    
    [params.comments.giscus]
      repo = "yourusername/your-repo"
      repoId = "your-repo-id"
      category = "Announcements"
      categoryId = "your-category-id"
      mapping = "pathname"
      theme = "preferred_color_scheme"
```

## Setting Up Giscus

1. **Enable Discussions** in your GitHub repository
2. **Install giscus app** from the GitHub Marketplace
3. **Get your repository ID** and category ID
4. **Configure the giscus settings** in your `config.toml`

## Creating Your First Post

```bash
hugo new posts/my-first-post.md
```

Here's an example post structure:

```markdown
---
title: "My First Blog Post"
date: 2024-01-15T10:00:00-05:00
draft: false
description: "This is my first blog post using Hugo and giscus."
tags: ["first-post", "hugo"]
categories: ["general"]
---

# My First Blog Post

Welcome to my blog! This is my first post using Hugo and giscus comments.

## Code Example

Here's some code to demonstrate syntax highlighting:

```python
def hello_world():
    print("Hello, World!")
    return "Success!"

# Call the function
result = hello_world()
print(result)
```

## Next Steps

- Write more posts
- Customize your theme
- Engage with readers through comments
- Share your knowledge with the community

## Conclusion

Hugo and giscus make an excellent combination for developer blogs. The setup is straightforward, the performance is excellent, and the community engagement through comments adds real value to your content.

What do you think about this setup? Have you tried Hugo or giscus before? Let me know in the comments below! 