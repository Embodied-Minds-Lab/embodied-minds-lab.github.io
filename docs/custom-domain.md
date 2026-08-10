# Moving the site to a custom domain

The site currently serves from `https://embodied-minds-lab.github.io` (GitHub Pages, deployed by
`.github/workflows/deploy.yml`). These are the steps to move it to a custom domain such as
`embodiedmindslab.com`.

**Nothing here has been applied** — this is a checklist for when the domain is registered.

## Why now is a good time

As of August 2026 the site had no search presence at all: `robots.txt` blocked every crawler
outside a four-name allowlist, so there is no accumulated index equity to lose. Migrating before
the site gets indexed avoids the usual cost of a domain move (split ranking signals, redirect
chains, re-crawl delay).

`embodiedmindslab.com` did not resolve when checked (`curl` returned no DNS), so it was most
likely unregistered at that point. Verify current availability before planning around it.

## 1. Register the domain

Any registrar works. Prefer one that supports `ALIAS`/`ANAME` records at the apex if you want
`embodiedmindslab.com` (no `www`) as the primary — otherwise the `A` records in step 3 are fine.

## 2. Tell the build about the new domain

Two changes:

**`public/CNAME`** — create it, containing exactly the apex domain and nothing else:

```
embodiedmindslab.com
```

Everything in `public/` is copied verbatim into `dist/`, which is what
`actions/upload-pages-artifact` publishes, so GitHub Pages picks this up automatically on the next
deploy. Do **not** set the custom domain only through the repo settings UI — a Pages deploy that
overwrites `dist/` without a `CNAME` file will clear it.

**`astro.config.ts`** — update `site` (currently line 41):

```ts
site: "https://embodiedmindslab.com",
```

`site` feeds the canonical URL, Open Graph tags, `sitemap-index.xml`, the Atom feed, and the
`Sitemap:` line in `robots.txt`. Leave `base: "/"` alone — it is already correct for an apex domain.

## 3. DNS records

For an apex domain, four `A` records (and optionally the `AAAA` set for IPv6) pointing at GitHub:

```
A     @   185.199.108.153
A     @   185.199.109.153
A     @   185.199.110.153
A     @   185.199.111.153

AAAA  @   2606:50c0:8000::153
AAAA  @   2606:50c0:8001::153
AAAA  @   2606:50c0:8002::153
AAAA  @   2606:50c0:8003::153
```

Plus `www` as a `CNAME` so both hostnames work:

```
CNAME www embodied-minds-lab.github.io.
```

Confirm these IPs against GitHub's current documentation before entering them — GitHub has changed
them before: <https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site>

## 4. Enable HTTPS

In the repo: **Settings → Pages**. The custom domain should already be filled in from `CNAME`.
Wait for the certificate to be issued (usually minutes, occasionally up to 24 hours), then tick
**Enforce HTTPS**. Do not skip this — without it the site serves over plain HTTP and the
`https://` canonical URLs will mismatch.

## 5. Verify

```bash
dig +short embodiedmindslab.com
curl -sI https://embodiedmindslab.com | head -1                      # expect 200
curl -s  https://embodiedmindslab.com/robots.txt                     # Sitemap: line shows new domain
curl -s  https://embodiedmindslab.com/ | grep -o 'rel="canonical" href="[^"]*"'
curl -sI https://embodied-minds-lab.github.io/ | head -1             # expect 301 to the new domain
```

GitHub Pages redirects the old `*.github.io` URL to the custom domain automatically once `CNAME`
is set, so existing links keep working.

## 6. Re-register with search engines

- **Google Search Console**: add `embodiedmindslab.com` as a new property, verify it (DNS TXT
  record is easiest since you control DNS), and submit `https://embodiedmindslab.com/sitemap-index.xml`.
- **Bing Webmaster Tools**: same, and it can import the Google Search Console configuration.
- If a Search Console property already exists for the `github.io` domain, use the **Change of
  Address** tool there to point it at the new one.
