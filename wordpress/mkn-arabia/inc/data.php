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

/** Page slugs that have a designed layout in fragments/. */
function mkn_page_slugs() {
	return array( 'home', 'services', 'pricing', 'work', 'testimonials', 'insights', 'about', 'contact', 'privacy', 'utm' );
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
		$slug = get_post_field( 'post_name', get_queried_object_id() );
		return in_array( $slug, mkn_page_slugs(), true ) ? $slug : '';
	}
	return '';
}
