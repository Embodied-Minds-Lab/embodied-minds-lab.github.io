# Embodied Minds Lab Website

Official website for the Embodied Minds Lab at Harvard University, led by Professor Yilun Du.

## 🚀 Quick Start

### Development

```sh
npm install
npm run dev     # Starts local development server at http://localhost:4321
```

### Building

```sh
npm run build   # Builds static site to dist/
```

## 📁 Project Structure

```
├── src/
│   ├── content/
│   │   ├── preface/        # Homepage content
│   │   ├── publications/   # Lab publications
│   │   └── information/    # About, join page content
│   ├── data/
│   │   └── people.ts       # Lab members data
│   ├── pages/
│   │   └── [...locale]/
│   │       ├── index.astro          # Homepage
│   │       ├── people/index.astro   # People page
│   │       └── publications/        # Publications page
│   └── layouts/
├── public/
│   └── people/             # Profile images
├── astro.config.ts         # Astro configuration
└── site.config.json        # Site metadata
```

## 🔧 Configuration

### Site Settings

Edit `site.config.json` to update:
- Site title and description
- Social media links
- Navigation menu

### Astro Configuration

Edit `astro.config.ts` for:
- Base URL and deployment settings
- Build configuration

### Environment Variables

Create a `.env` file for environment-specific settings.

## 👥 Managing People

Edit `src/data/people.ts` to add, remove, or update lab members:

```typescript
{
  name: "Person Name",
  position: "PhD Student",
  image: "/people/person.jpg",
  bio: "Short bio...",
  research: "Research interests...",
  links: {
    website: "https://...",
    email: "email@example.com",
    scholar: "https://scholar.google.com/...",
    github: "https://github.com/..."
  }
}
```

Profile images go in `public/people/`.

## 📝 Managing Publications

Publications are managed as markdown files in `src/content/publications/en/`.

Each publication file should include frontmatter with:
- title
- authors
- venue
- year
- links (paper, project page, etc.)

## 🚀 Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the `main` branch.

### Manual Deployment

1. Build the site: `npm run build`
2. Deploy the `dist/` directory to your hosting platform

## 📦 Tech Stack

- **Framework**: [Astro](https://astro.build/)
- **Styling**: [UnoCSS](https://unocss.dev/)
- **Markdown**: Content collections with frontmatter
- **Deployment**: GitHub Pages via GitHub Actions

## 📄 License

Built with the [ThoughtLite](https://github.com/tuyuritio/astro-theme-thought-lite) Astro theme.
