<?php
defined( 'ABSPATH' ) || exit;

/*
 * Working together with All in One SEO (AIOSEO), when it is active.
 * AIOSEO stays the place where titles and descriptions are edited; the theme
 *  - fills AIOSEO's title and description for its pages and articles when they are empty,
 *  - adds the share image and the right og:type when AIOSEO has none,
 *  - adds its Service / FAQ schema to AIOSEO's graph and credits articles to the organisation,
 *  - lists in the image sitemap only the images a designed page really shows (not leftovers
 *    from an older site that used the same page).
 */

function mkn_aioseo_active() {
	return defined( 'AIOSEO_VERSION' ) && function_exists( 'aioseo' );
}

/** Designed page path of a post, or ''. */
function mkn_designed_path( $post ) {
	$post = get_post( $post );
	if ( ! $post || 'page' !== $post->post_type ) {
		return '';
	}
	if ( (int) get_option( 'page_on_front' ) === (int) $post->ID ) {
		return 'home';
	}
	if ( (int) get_option( 'page_for_posts' ) === (int) $post->ID ) {
		return 'insights';
	}
	$path = mkn_page_path( $post );
	return in_array( $path, mkn_page_slugs(), true ) ? $path : '';
}

/* ---------- share tags ---------- */
add_filter( 'aioseo_facebook_tags', function ( $meta ) {
	if ( empty( $meta['og:image'] ) ) {
		$img                         = mkn_asset( 'img/og-image.jpg' );
		$meta['og:image']            = $img;
		$meta['og:image:secure_url'] = is_ssl() ? $img : '';
		$meta['og:image:width']      = 1200;
		$meta['og:image:height']     = 630;
	}
	if ( is_front_page() || ( is_page() && mkn_current_slug() ) ) {
		$meta['og:type'] = 'website';
		foreach ( array_keys( $meta ) as $k ) {
			if ( 0 === strpos( $k, 'article:' ) ) {
				unset( $meta[ $k ] );
			}
		}
	}
	$m = mkn_seo_meta();
	if ( empty( $meta['og:description'] ) && $m['desc'] ) {
		$meta['og:description'] = $m['desc'];
	}
	return $meta;
} );

add_filter( 'aioseo_twitter_tags', function ( $meta ) {
	if ( empty( $meta['twitter:image'] ) ) {
		$meta['twitter:image'] = mkn_asset( 'img/og-image.jpg' );
	}
	$meta['twitter:card'] = 'summary_large_image';
	return $meta;
} );

/* ---------- schema ---------- */
add_filter( 'aioseo_schema_output', function ( $graph ) {
	if ( ! is_array( $graph ) ) {
		return $graph;
	}
	$org_id = trailingslashit( home_url() ) . '#organization';
	if ( isset( aioseo()->options->searchAppearance->global->schema->siteRepresents ) && 'person' === aioseo()->options->searchAppearance->global->schema->siteRepresents ) {
		$org_id = trailingslashit( home_url() ) . '#person';
	}
	foreach ( $graph as $i => $node ) {
		$type = isset( $node['@type'] ) ? (array) $node['@type'] : array();
		if ( array_intersect( $type, array( 'BlogPosting', 'Article', 'NewsArticle' ) ) ) {
			// Articles are written by the MKN ARABIA team, not by a WordPress user account.
			$graph[ $i ]['author'] = array( '@id' => $org_id );
		}
		if ( array_intersect( $type, array( 'WebPage', 'ItemPage', 'CollectionPage' ) ) && isset( $node['author'] ) && is_singular( 'post' ) ) {
			$graph[ $i ]['author'] = array( '@id' => $org_id );
		}
		if ( array_intersect( $type, array( 'Organization' ) ) && empty( $node['areaServed'] ) ) {
			$graph[ $i ]['areaServed'] = mkn_area_served();
		}
	}
	$slug = is_front_page() ? '' : mkn_current_slug();
	if ( $slug ) {
		foreach ( mkn_page_ld( $slug ) as $node ) {
			if ( 'BreadcrumbList' === $node['@type'] ) {
				continue; // AIOSEO prints its own breadcrumbs
			}
			unset( $node['@context'] );
			if ( isset( $node['provider'] ) ) {
				$node['provider'] = array( '@id' => $org_id );
			}
			$graph[] = $node;
		}
	}
	return $graph;
} );

/* ---------- image sitemap: what the designed page shows ---------- */
add_filter( 'aioseo_sitemap_images', function ( $images, $post ) {
	$path = mkn_designed_path( $post );
	if ( ! $path || 'insights' === $path ) {
		return $images;
	}
	$html = mkn_fragment( $path );
	preg_match_all( '/<img\b[^>]*\ssrc="([^"]+)"/i', $html, $m );
	$out = array();
	foreach ( $m[1] as $src ) {
		$src = html_entity_decode( $src, ENT_QUOTES, 'UTF-8' );
		if ( preg_match( '/\.(webp|png|jpe?g)$/i', wp_parse_url( $src, PHP_URL_PATH ) ) ) {
			$out[ $src ] = $src;
		}
	}
	return array_values( $out );
}, 10, 2 );

/**
 * Write the theme's titles and descriptions into AIOSEO.
 * $overwrite false: only where AIOSEO has nothing yet (runs after every theme update).
 * $overwrite true: replace (the «مزامنة» button), for pages that kept an older site's values.
 */
function mkn_aioseo_sync( $overwrite = false ) {
	if ( ! mkn_aioseo_active() || ! class_exists( '\AIOSEO\Plugin\Common\Models\Post' ) ) {
		return 0;
	}
	$pages = (array) mkn_site( 'pages' );
	$jobs  = array();
	foreach ( $pages as $path => $pg ) {
		if ( '404' === (string) $path || 'utm' === $path ) {
			continue;
		}
		$id = 'home' === $path ? (int) get_option( 'page_on_front' ) : ( 'insights' === $path ? (int) get_option( 'page_for_posts' ) : 0 );
		if ( ! $id ) {
			$p  = get_page_by_path( $path, OBJECT, array( 'page' ) );
			$id = $p ? $p->ID : 0;
		}
		if ( $id ) {
			$jobs[ $id ] = array( $pg['title'], $pg['desc'] );
		}
	}
	$designed = array_keys( $jobs );
	foreach ( get_posts( array( 'post_type' => 'post', 'posts_per_page' => -1, 'post_status' => 'publish', 'fields' => 'ids' ) ) as $id ) {
		if ( get_post_meta( $id, '_mkn_seed_key', true ) ) {
			$designed[] = $id; // the theme's own articles
		}
		$t = mkn_meta( $id, 'seo_title' );
		$d = has_excerpt( $id ) ? get_post_field( 'post_excerpt', $id ) : '';
		if ( $t || $d ) {
			$jobs[ $id ] = array( $t, $d );
		}
	}
	$n = 0;
	// The internal campaign-link tool stays out of search results and the sitemap.
	$utm = get_page_by_path( 'utm', OBJECT, array( 'page' ) );
	if ( $utm ) {
		$row = \AIOSEO\Plugin\Common\Models\Post::getPost( $utm->ID );
		if ( empty( $row->robots_noindex ) ) {
			$row->robots_default  = false;
			$row->robots_noindex  = true;
			$row->robots_nofollow = true;
			$row->save();
			$n++;
		}
	}
	foreach ( $jobs as $id => $td ) {
		$row     = \AIOSEO\Plugin\Common\Models\Post::getPost( $id );
		$changed = false;
		$force   = $overwrite && in_array( $id, $designed, true ); // other articles: fill only if empty
		if ( $td[0] && ( $force || empty( $row->title ) ) ) {
			$row->title = $td[0];
			$changed    = true;
		}
		if ( $td[1] && ( $force || empty( $row->description ) ) ) {
			$row->description = $td[1];
			$changed          = true;
		}
		if ( $changed ) {
			$row->save();
			$n++;
		}
	}
	return $n;
}

/**
 * Designed pages that were already on the site from an older theme keep their old title and
 * text (not shown anymore, but read by SEO plugins). This gives them the theme's titles and
 * moves the old text to a revision.
 */
function mkn_sync_designed_pages() {
	$n = 0;
	foreach ( mkn_seed_pages() as $path => $title ) {
		$p = get_page_by_path( $path, OBJECT, array( 'page' ) );
		if ( ! $p ) {
			continue;
		}
		if ( $p->post_title === $title && '' === trim( $p->post_content ) ) {
			continue;
		}
		$content = $p->post_content;
		if ( '' !== trim( $content ) ) {
			// Keep the old text: as a revision when revisions are on, and always in a field on the page.
			if ( wp_revisions_enabled( $p ) ) {
				$last = wp_get_post_revisions( $p->ID, array( 'posts_per_page' => 1 ) );
				$last = $last ? reset( $last ) : null;
				if ( ! $last || $last->post_content !== $content ) {
					_wp_put_post_revision( $p );
				}
			}
			update_post_meta( $p->ID, '_mkn_old_content', wp_slash( $content ) );
		}
		wp_update_post( array( 'ID' => $p->ID, 'post_title' => $title, 'post_content' => '' ) );
		$n++;
	}
	return $n;
}
