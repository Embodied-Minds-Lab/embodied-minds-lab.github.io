#!/usr/bin/env python3
"""
Scraper to extract publication data from Yilun Du's website
"""
import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin
import re
from pathlib import Path

def clean_filename(filename):
    """Clean filename to be filesystem safe"""
    return re.sub(r'[^\w\-_.]', '_', filename)

def get_existing_titles(content_dir="src/content/publications/en"):
    """Return set of titles already present in the content directory."""
    titles = set()
    path = Path(content_dir)
    if not path.exists():
        return titles
    for md_file in path.glob("*.md"):
        content = md_file.read_text(encoding='utf-8')
        match = re.search(r'^title:\s*"(.*?)"', content, re.MULTILINE)
        if match:
            titles.add(match.group(1).replace('\\"', '"'))
    return titles


def scrape_publications(existing_titles=None, start_id=0):
    if existing_titles is None:
        existing_titles = set()

    url = "https://yilundu.github.io/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    publications = []
    new_id = start_id

    pub_headers = soup.find_all('h5')

    for header in pub_headers:
        try:
            title = header.get_text(strip=True)

            # Skip section headers and the JS toggle line
            if title in ['News', 'Research Highlights'] or title.startswith('Publications'):
                continue

            # Skip already-scraped publications
            if title in existing_titles:
                continue

            # Authors
            authors_elem = header.find_next_sibling('h6')
            authors = []
            if authors_elem:
                authors = [a.strip() for a in authors_elem.get_text(strip=True).split(',')]

            # Links
            links = {}
            links_elem = header.find_next_sibling('p')
            if links_elem:
                for link in links_elem.find_all('a'):
                    link_text = link.get_text(strip=True)
                    link_url = link.get('href', '')
                    links[link_text.lower().replace(' ', '_').replace('/', '_')] = link_url

            # Venue and year
            venue_elem = header.find_next('p')
            venue = ""
            year = 2024

            if venue_elem:
                venue_text = venue_elem.get_text(strip=True)
                year_match = re.search(r'(20\d{2})', venue_text)
                if year_match:
                    year = int(year_match.group(1))
                venue = venue_text.split('/')[0].strip() if '/' in venue_text else venue_text

            # Image: the site uses a .row div with .col-l (image) and .col-r (text) siblings
            image_url = None
            row_parent = header.find_parent(class_='row')
            if row_parent:
                img = row_parent.find('img')
                if img and img.get('src'):
                    image_url = urljoin(url, img['src'])

            pub_data = {
                'title': title,
                'authors': authors,
                'venue': venue,
                'year': year,
                'links': links,
                'image_url': image_url,
                'id': f"pub_{new_id:03d}"
            }

            publications.append(pub_data)
            new_id += 1

        except Exception as e:
            print(f"Error processing publication '{title[:60]}': {e}")
            continue

    return publications

def download_images(publications, output_dir="public/publications"):
    """Download publication images"""
    os.makedirs(output_dir, exist_ok=True)
    
    for pub in publications:
        if pub.get('image_url'):
            try:
                img_response = requests.get(pub['image_url'], timeout=10)
                if img_response.status_code == 200:
                    # Get extension from URL
                    ext = pub['image_url'].split('.')[-1].split('?')[0]
                    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                        ext = 'jpg'
                    
                    filename = f"{pub['id']}.{ext}"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    # Update pub data with local path
                    pub['image'] = f"/publications/{filename}"
                    print(f"Downloaded image for: {pub['title'][:50]}...")
            except Exception as e:
                print(f"Error downloading image for {pub['title']}: {e}")

def create_markdown_files(publications, output_dir="src/content/publications/en"):
    """Create markdown files for each publication"""
    os.makedirs(output_dir, exist_ok=True)
    
    for pub in publications:
        # Create safe filename from id
        filename = f"{pub['id']}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Build frontmatter
        frontmatter = f"""---
title: "{pub['title'].replace('"', '\\"')}"
authors:
{chr(10).join(f'  - "{author}"' for author in pub['authors'])}
venue: "{pub['venue']}"
year: {pub['year']}
image: "{pub.get('image', '')}"
"""
        
        # Add links if available
        if pub['links']:
            if pub['links'].get('paper'):
                frontmatter += f'paper: "{pub["links"]["paper"]}"\n'
            if pub['links'].get('website') or pub['links'].get('project_page'):
                website = pub['links'].get('website') or pub['links'].get('project_page')
                frontmatter += f'website: "{website}"\n'
            if pub['links'].get('code'):
                frontmatter += f'code: "{pub["links"]["code"]}"\n'
        
        frontmatter += "draft: false\n---\n\n"
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
        
        print(f"Created: {filename}")

def main():
    content_dir = "src/content/publications/en"
    existing_titles = get_existing_titles(content_dir)
    print(f"Found {len(existing_titles)} existing publications — skipping those.")

    # Start new IDs after the highest existing pub_NNN
    existing_ids = [
        int(p.stem.split('_')[1])
        for p in Path(content_dir).glob("pub_*.md")
        if p.stem.split('_')[1].isdigit()
    ]
    start_id = max(existing_ids) + 1 if existing_ids else 0

    print(f"Scraping new publications from https://yilundu.github.io/ (IDs start at pub_{start_id:03d})...")
    publications = scrape_publications(existing_titles=existing_titles, start_id=start_id)
    print(f"Found {len(publications)} new publications")
    
    # Save raw data as JSON for reference
    with open('publications_data.json', 'w', encoding='utf-8') as f:
        json.dump(publications, f, indent=2, ensure_ascii=False)
    print("Saved raw data to publications_data.json")
    
    # Download images
    print("\nDownloading images...")
    download_images(publications)
    
    # Create markdown files
    print("\nCreating markdown files...")
    create_markdown_files(publications)
    
    print("\nDone!")

if __name__ == "__main__":
    main()

