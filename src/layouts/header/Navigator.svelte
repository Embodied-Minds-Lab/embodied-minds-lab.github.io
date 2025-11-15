<style lang="less">
	header {
		a {
			position: relative;
			display: inline-block;

			p {
				padding: 5px 10px;
				font-size: 1.1rem;
				text-align: center;
				color: var(--primary-color);
				background-color: transparent;
				transition: color 0.15s ease, background-color 0.15s ease;
			}

			&:hover, &.location {
				p {
					color: var(--background-color);
					background-color: var(--primary-color);
				}
			}
	}
}

@media screen and (max-width: 640px) {
		nav {
			header {
				a {
					display: flex;
					gap: 0.5rem;

					p {
						padding: 0px;
							font-size: 1.1rem;
						white-space: nowrap;

						clip-path: none;
						color: var(--primary-color);
						background-color: var(--background-color);
					}

					&.location {
						font-weight: bold;
					}
				}
			}
		}
	}
</style>

<!-- svelte-ignore a11y_interactive_supports_focus -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div role="button" onclick={() => (menu = false)} class:pointer-events-none={!menu} class:bg-transparent={!menu} class="fixed top-0 left-0 w-screen h-screen pointer-events-auto bg-#aaaaaa88 transition-background-color sm:hidden"></div>

<nav bind:this={navigator} class:transform-translate-x-full={!menu} class="fixed top-0 right-0 flex flex-col justify-between items-start gap-5 p-5 bg-background h-full sm:contents overflow-hidden transition-transform">
    <header class="grid gap-5 c-secondary grid-rows-[repeat(5,1fr)] sm:(grid-rows-none grid-cols-[repeat(4,1fr)])">
		<button onclick={() => (menu = false)} class="sm:hidden">{@render close()}</button>

		<a href={getUrl("/")} class:location={route == getUrl("/") || route.startsWith(getUrl("/preface"))}>
			<p>{t("navigation.home")}</p>
		</a>
        <a href={getUrl("/publications")} class:location={route.startsWith(getUrl("/publications"))}>
            <p>{t("navigation.publications") || "Publications"}</p>
        </a>
        <a href={getUrl("/people")} class:location={route.startsWith(getUrl("/people"))}>
            <p>{t("navigation.people")}</p>
        </a>
        <a href={getUrl("/contact")} class:location={route.startsWith(getUrl("/contact"))}>
			<p>{t("navigation.join") || "Contact"}</p>
		</a>
	</header>

	<footer class="flex flex-col gap-2 sm:gap-5 sm:(flex-row gap-7)">
		<ThemeSwitcher {sun} {moon} />
	</footer>
</nav>

<button onclick={() => (menu = true)} class="sm:hidden">{@render bars()}</button>

<script lang="ts">
	import { i18n } from "astro:config/client";
	import { getRelativeLocaleUrl } from "astro:i18n";
	import { onMount, type Snippet } from "svelte";
	import i18nit from "$i18n";
	import ThemeSwitcher from "./ThemeSwitcher.svelte";

	let { locale, route, baseUrl = '', home, note, jotting, people, about, sun, moon, bars, close }: { locale: string; route: string; baseUrl?: string } & { [key: string]: Snippet } = $props();

	const t = i18nit(locale);
	
	// Helper to construct full URL with base path and locale
	const getUrl = (path: string) => {
		// For home page (empty or "/"), use getRelativeLocaleUrl without path argument
		if (path === "/" || path === "") {
			return getRelativeLocaleUrl(locale);
		}
		// For other pages, use getRelativeLocaleUrl with the path
		return getRelativeLocaleUrl(locale, path);
	};

	// Control mobile menu visibility state
	let menu: boolean = $state(false);
	let navigator: HTMLElement | undefined = $state();

	onMount(() => {
		// Close mobile menu when any navigation link is clicked
		for (const link of navigator!.getElementsByTagName("a")) {
			link.addEventListener("click", () => (menu = false));
		}

		// Set up route tracking for page navigation with Swup integration
		const update_route = () => (route = window.location.pathname);
		if (window.swup) {
			// Register route update hook if Swup is already available
			window.swup.hooks.on("page:load", update_route);
		} else {
			// Wait for Swup to be enabled and then register the hook
			document.addEventListener("swup:enable", () => window.swup?.hooks.on("page:load", update_route));
		}
	});
</script>
