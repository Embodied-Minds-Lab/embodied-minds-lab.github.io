<style lang="less">
	article {
		footer {
			button {
				display: flex;
				align-items: center;
				justify-content: center;

				width: 30px;
				height: 30px;

				margin-top: 0.25rem 0rem 0.5rem;
				border-bottom: 2px solid;

				font-style: var(--monospace);
				font-size: 0.875rem;

				transition: color 0.15s ease-in-out;

				&:hover,
				&.location {
					color: var(--primary-color);
				}
			}
		}
	}

	aside {
		section {
			display: flex;
			flex-direction: column;
			gap: 5px;

			p {
				display: flex;
				flex-direction: row;
				flex-wrap: wrap;
				gap: 5px;

				button {
					border-bottom: 1px solid var(--primary-color);
					padding: 0rem 0.2rem;

					font-size: 0.9rem;
					transition:
						color 0.1s ease-in-out,
						background-color 0.1s ease-in-out;

					&.selected {
						color: var(--background-color);
						background-color: var(--primary-color);
					}

					@media (min-width: 640px) {
						&:hover {
							color: var(--background-color);
							background-color: var(--primary-color);
						}
					}
				}
			}
		}
	}
</style>

<main class="flex flex-col-reverse sm:flex-row gap-10 grow">
	<article class="flex flex-col gap-4 grow">
		{#each list as publication (publication.id)}
			<section animate:flip={{ duration: 150 }} class="flex flex-col sm:flex-row">
				<div class="flex flex-col gap-1">
					<div class="flex gap-1 items-center">
					<a href={getRelativeLocaleUrl(locale, `/publications/${publication.id.split("/").slice(1).join("/")}`)} class="link text-5 font-600">{publication.data.title}</a>
					</div>
					<div class="c-remark">{publication.data.authors.join(", ")}</div>
					<div class="c-remark font-mono text-2.6">
						{publication.data.venue} · {publication.data.year}
						{#if publication.data.award}
							 · <span class="font-bold" style="color: #A51C30;">{publication.data.award}</span>
						{/if}
					</div>
				</div>
				<span class="flex items-center gap-1 sm:ml-a c-remark">
					{#each publication.data.tags as tag}
						<button onclick={() => switch_tag(tag, true)} class="text-3.5 sm:text-sm">#{tag}</button>
					{/each}
				</span>
			</section>
		{/each}

		{#if pages > 1}
			<footer class="sticky bottom-0 flex items-center justify-center gap-3 mt-a pb-1 c-weak bg-background font-mono">
				<button onclick={() => (page = Math.max(1, page - 1))}>{@render left()}</button>
				<button class:location={1 == page} onclick={() => (page = 1)}>{1}</button>

				{#if pages > 7 && page > 4}{@render dots()}{/if}

				{#each Array.from({ length: Math.min(5, pages - 2) }, (_, i) => i + Math.max(2, Math.min(pages - 5, page - 2))) as P (P)}
					<button class:location={P == page} onclick={() => (page = P)} animate:flip={{ duration: 150 }} transition:fade={{ duration: 150 }}>{P}</button>
				{/each}

				{#if pages > 7 && page < pages - 3}{@render dots()}{/if}

				<button class:location={pages == page} onclick={() => (page = pages)}>{pages}</button>
				<button onclick={() => (page = Math.min(pages, page + 1))}>{@render right()}</button>
			</footer>
		{/if}
	</article>

	<aside class="sm:flex-basis-200px flex flex-col gap-5">
		<section>
			<h3>{t("publication.venue")}</h3>
			<p>
				{#each venue_list as venue_item (venue_item)}
					<button class:selected={venue_item == venue} onclick={() => choose_venue(venue_item)}>{venue_item}</button>
				{/each}
			</p>
		</section>

		<section>
			<h3>{t("publication.year")}</h3>
			<p>
				{#each year_list as year_item (year_item)}
					<button class:selected={year_item == year} onclick={() => choose_year(year_item)}>{year_item}</button>
				{/each}
			</p>
		</section>

		<section>
			<h3>{t("publication.tag")}</h3>
			<p>
				{#each tag_list as tag (tag)}
					<button class:selected={tags.includes(tag)} onclick={() => switch_tag(tag)}>{tag}</button>
				{/each}
			</p>
		</section>
	</aside>
</main>

<script lang="ts">
	import { getRelativeLocaleUrl } from "astro:i18n";
	import { onMount, type Snippet } from "svelte";
	import { flip } from "svelte/animate";
	import { fade } from "svelte/transition";
	import i18nit from "$i18n";

	let { locale, publications, venues: venue_list, tags: tag_list, years: year_list, left, right, dots }: { locale: string; publications: any[]; venues: string[]; tags: string[]; years: number[]; left: Snippet; right: Snippet; dots: Snippet } = $props();

	const t = i18nit(locale);

	let initial = $state(false);
	let venue: string | null = $state(null);
	let year: number | null = $state(null);
	let tags: string[] = $state([]);
	let filtered: any[] = $derived.by(() => {
		let list: any[] = publications
			.filter(pub => {
				let match_venue = !venue || pub.data.venue == venue;
				let match_year = !year || pub.data.year == year;
				let match_tags = tags.every(tag => pub.data.tags?.includes(tag));
				return match_venue && match_year && match_tags;
			})
			.sort((a, b) => b.data.year - a.data.year);

		if (!initial) return list;

		let url = getRelativeLocaleUrl(locale, `/publications?page=${page}${venue ? `&venue=${venue}` : ""}${year ? `&year=${year}` : ""}${tags.map(tag => `&tag=${tag}`).join("")}`);

		window.history.replaceState({ url, random: Math.random(), source: "swup" }, "", url);

		return list;
	});

	const size: number = 20;
	let pages: number = $derived(Math.ceil(filtered.length / size));

	let page: number = $state(1);
	$effect(() => {
		page = Math.max(1, Math.min(Math.floor(page), pages));
	});

	let list: any[] = $derived(filtered.slice((page - 1) * size, page * size));

	function switch_tag(tag: string, turn?: boolean) {
		let included = tags.includes(tag);
		if (turn === undefined) turn = !included;
		tags = turn ? (included ? tags : [...tags, tag]) : tags.filter(item => item !== tag);
	}

	function choose_venue(venue_choice: string, turn?: boolean) {
		if (turn === undefined) turn = venue !== venue_choice;
		venue = turn ? venue_choice : null;
	}

	function choose_year(year_choice: number, turn?: boolean) {
		if (turn === undefined) turn = year !== year_choice;
		year = turn ? year_choice : null;
	}

	onMount(() => {
		const params = new URLSearchParams(window.location.search);

		page = Number(params.get("page")) || 1;
		venue = params.get("venue");
		const yearParam = params.get("year");
		year = yearParam ? Number(yearParam) : null;
		tags = params.getAll("tag");

		initial = true;
	});
</script>

