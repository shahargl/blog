# Multilingual Support - Hebrew and English

This blog now supports both English and Hebrew languages using Hugo's built-in multilingual features.

## Language Structure

The content is organized as follows:

```
content/
├── en/          # English content
│   ├── about.md
│   └── posts/
│       ├── getting-started-with-hugo-and-giscus.md
│       ├── building-a-modern-web-app.md
│       └── welcome.md
└── he/          # Hebrew content
    ├── about.md
    └── posts/
        ├── getting-started-with-hugo-and-giscus.md
        └── building-a-modern-web-app.md
```

## Configuration

The multilingual setup is configured in `config.yaml`:

```yaml
languages:
  en:
    languageName: English
    title: Shahar Glazner - Dev Blog
    weight: 1
    params:
      description: "Personal development blog covering software engineering, web development, and tech insights"
      # ... other English-specific settings
      
  he:
    languageName: עברית
    title: שחר גלזנר - בלוג פיתוח
    weight: 2
    params:
      description: "בלוג פיתוח אישי המכסה הנדסת תוכנה, פיתוח web ותובנות טכנולוגיות"
      # ... other Hebrew-specific settings
```

## Features

### Language Switcher
The Stack theme automatically provides a language switcher in the navigation, allowing users to switch between English and Hebrew.

### RTL Support
Hebrew content is automatically displayed with right-to-left (RTL) text direction.

### SEO
Each language has its own:
- Meta descriptions
- Open Graph tags
- Language-specific URLs (e.g., `/he/posts/...`)

### Comments
Each language has its own giscus configuration:
- English: `lang: en`
- Hebrew: `lang: he`

## Creating New Content

### For English
```bash
hugo new en/posts/my-new-post.md
```

### For Hebrew
```bash
hugo new he/posts/my-new-post.md
```

### Front Matter Example

**English:**
```yaml
---
title: "My New Post"
date: 2024-01-15T10:00:00-05:00
draft: false
description: "Description in English"
tags: ["tag1", "tag2"]
categories: ["category1"]
---
```

**Hebrew:**
```yaml
---
title: "הפוסט החדש שלי"
date: 2024-01-15T10:00:00-05:00
draft: false
description: "תיאור בעברית"
tags: ["תג1", "תג2"]
categories: ["קטגוריה1"]
---
```

## URL Structure

- English: `https://shahar.blog/en/posts/post-name/`
- Hebrew: `https://shahar.blog/he/posts/post-name/`
- Default language (English): `https://shahar.blog/posts/post-name/`

## Best Practices

1. **Keep content synchronized**: When you add content in one language, consider adding it in the other.

2. **Use appropriate tags and categories**: Create language-specific tags and categories when needed.

3. **Maintain consistent structure**: Keep the same post structure across languages.

4. **Test both languages**: Always test your site in both languages after making changes.

5. **Consider cultural differences**: Some content might need adaptation rather than direct translation.

## Adding More Languages

To add another language (e.g., Arabic):

1. Add the language configuration to `config.yaml`:
```yaml
languages:
  # ... existing languages ...
  ar:
    languageName: العربية
    title: شاهر جلوازنر - مدونة المطور
    weight: 3
    params:
      # ... Arabic-specific settings
```

2. Create the content directory:
```bash
mkdir -p content/ar/posts
```

3. Add Arabic content following the same structure as Hebrew.

## Troubleshooting

### Language Switcher Not Appearing
- Ensure both languages are properly configured in `config.yaml`
- Check that content exists for both languages
- Verify the theme supports multilingual features

### RTL Not Working
- The Stack theme should automatically detect Hebrew and apply RTL
- Check that Hebrew content is in the `he/` directory
- Verify the language code is set to `he` in the configuration

### Comments Not Working
- Ensure giscus is configured for each language
- Check that the language parameter is set correctly (`lang: he` for Hebrew)
- Verify GitHub Discussions is enabled for the repository 