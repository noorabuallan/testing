<?php
defined( 'ABSPATH' ) || exit;

/** Static site data exported by the generator (navigation, departments, bundles, countries, page titles). */
function mkn_site( $key = null ) {
	static $site = null;
	if ( null === $site ) {
		$site = json_decode( (string) file_get_contents( MKN_DIR . '/data/site.json' ), true );
		if ( ! is_array( $site ) ) {
			$site = array();
		}
	}
	if ( null === $key ) {
		return $site;
	}
	return isset( $site[ $key ] ) ? $site[ $key ] : null;
}

/** Seed content shipped with the theme (used by the importer and for default settings). */
function mkn_seed( $key = null ) {
	static $seed = null;
	if ( null === $seed ) {
		$seed = json_decode( (string) file_get_contents( MKN_DIR . '/seed/content.json' ), true );
		if ( ! is_array( $seed ) ) {
			$seed = array();
		}
	}
	if ( null === $key ) {
		return $seed;
	}
	return isset( $seed[ $key ] ) ? $seed[ $key ] : array();
}

/** Page paths that have a designed layout in fragments/ (services, markets/qatar …). */
function mkn_page_slugs() {
	static $slugs = null;
	if ( null === $slugs ) {
		$slugs = array_values( array_diff( array_keys( (array) mkn_site( 'pages' ) ), array( '404' ) ) );
	}
	return $slugs;
}

/** Path of a page (parent/child), e.g. markets/qatar. */
function mkn_page_path( $post ) {
	$post = get_post( $post );
	return $post ? get_page_uri( $post ) : '';
}

/** The slug of the designed page being shown, or '' for any other view. */
function mkn_current_slug() {
	if ( is_front_page() ) {
		return 'home';
	}
	if ( is_home() ) {
		return 'insights';
	}
	if ( is_404() ) {
		return '404';
	}
	if ( is_page() ) {
		$slug = mkn_page_path( get_queried_object_id() );
		return in_array( $slug, mkn_page_slugs(), true ) ? $slug : '';
	}
	return '';
}
