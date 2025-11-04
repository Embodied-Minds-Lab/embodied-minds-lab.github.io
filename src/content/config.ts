import { glob } from "astro/loaders";
import { defineCollection, z } from "astro:content";

// Note and Jotting collections removed (directories no longer exist)

/**
 * Preface collection configuration
 * Represents introductory content, site announcements, or special pages
 */
const preface = defineCollection({
	// Load all markdown files
	loader: glob({ pattern: "**/*.md", base: "./src/content/preface" }),
	schema: z.object({
		timestamp: z.date()		// Creation timestamp
	})
});

/**
 * Information collection configuration
 * Represents static content like about pages, policies, or site information
 */
const information = defineCollection({
	// Load both markdown and YAML files for mixed content types
	loader: glob({ pattern: "**/*.(md|yaml)", base: "./src/content/information" })
});

/**
 * Publications collection configuration
 * Represents academic publications metadata
 */
const publications = defineCollection({
    // Load all markdown files except those starting with underscore
    loader: glob({ pattern: ["**/*.md", "!**/_*.md", "!**/_*/*.md"], base: "./src/content/publications" }),
    schema: z.object({
        title: z.string(),
        authors: z.array(z.string()),
        venue: z.string(),
        year: z.number().int(),
        award: z.string().optional(),
        image: z.string().optional(),
        paper: z.string().url().optional(),
        website: z.string().url().optional(),
        code: z.string().url().optional(),
        link: z.string().url().optional(),
        doi: z.string().optional(),
        tags: z.array(z.string()).optional(),
        draft: z.boolean().default(false)
    })
});

export const collections = { preface, information, publications };
