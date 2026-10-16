<?php
defined( 'ABSPATH' ) || exit;

add_action( 'after_setup_theme', function () {
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'editor-styles' );
} );

/* ---------- lean front end: no emoji script, no embeds, no generator tag ---------- */
remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
remove_action( 'wp_print_styles', 'print_emoji_styles' );
remove_action( 'admin_print_scripts', 'print_emoji_detection_script' );
remove_action( 'admin_print_styles', 'print_emoji_styles' );
remove_action( 'wp_head', 'wp_generator' );
remove_action( 'wp_head', 'wlwmanifest_link' );
remove_action( 'wp_head', 'rsd_link' );
remove_action( 'wp_head', 'wp_shortlink_wp_head' );
remove_action( 'wp_head', 'wp_oembed_add_discovery_links' );
remove_action( 'wp_head', 'rest_output_link_wp_head' );
add_filter( 'xmlrpc_enabled', '__return_false' );

/* ---------- comments are not used on this site ---------- */
add_filter( 'comments_open', '__return_false', 20 );
add_filter( 'pings_open', '__return_false', 20 );
add_filter( 'comments_array', '__return_empty_array', 10 );
add_action( 'admin_menu', function () {
	remove_menu_page( 'edit-comments.php' );
} );
add_action( 'init', function () {
	remove_post_type_support( 'post', 'comments' );
	remove_post_type_support( 'page', 'comments' );
}, 100 );
add_action( 'wp_before_admin_bar_render', function () {
	global $wp_admin_bar;
	$wp_admin_bar->remove_menu( 'comments' );
} );

/* ---------- styles and scripts ---------- */
function mkn_asset_ver( $rel ) {
	$file = MKN_DIR . '/assets/' . $rel;
	return file_exists( $file ) ? (string) filemtime( $file ) : MKN_VERSION;
}

add_action( 'wp_enqueue_scripts', function () {
	wp_enqueue_style( 'mkn-fonts', MKN_URI . '/assets/css/fonts.css', array(), mkn_asset_ver( 'css/fonts.css' ) );
	wp_enqueue_style( 'mkn-style', MKN_URI . '/assets/css/style.css', array( 'mkn-fonts' ), mkn_asset_ver( 'css/style.css' ) );

	wp_enqueue_script( 'mkn-tracking', MKN_URI . '/assets/js/tracking.js', array(), mkn_asset_ver( 'js/tracking.js' ), array( 'strategy' => 'defer', 'in_footer' => false ) );
	wp_add_inline_script( 'mkn-tracking', 'window.MKN_CONFIG=' . wp_json_encode( mkn_js_config() ) . ';', 'before' );
	wp_enqueue_script( 'mkn-main', MKN_URI . '/assets/js/main.js', array(), mkn_asset_ver( 'js/main.js' ), array( 'strategy' => 'defer', 'in_footer' => true ) );

	// Block styles only where editor content is shown.
	if ( ! mkn_shows_editor_content() ) {
		wp_dequeue_style( 'wp-block-library' );
		wp_dequeue_style( 'wp-block-library-theme' );
		wp_dequeue_style( 'global-styles' );
		wp_dequeue_style( 'classic-theme-styles' );
	}
}, 20 );

/** Views that print content written in the editor (articles and ordinary pages). */
function mkn_shows_editor_content() {
	return is_singular( 'post' ) || ( is_page() && '' === mkn_current_slug() );
}

add_action( 'wp', function () {
	if ( is_admin() || mkn_shows_editor_content() ) {
		return;
	}
	remove_action( 'wp_enqueue_scripts', 'wp_enqueue_global_styles' );
	remove_action( 'wp_footer', 'wp_enqueue_global_styles', 1 );
	remove_action( 'wp_enqueue_scripts', 'wp_enqueue_classic_theme_styles' );
	remove_action( 'wp_footer', 'wp_enqueue_stored_styles', 1 );
} );

/** Settings the front-end scripts need (WhatsApp number, email, lead endpoint, tracking IDs). */
function mkn_js_config() {
	return array(
		'wa'       => preg_replace( '/\D+/', '', mkn_opt( 'whatsapp' ) ),
		'email'    => mkn_opt( 'email' ),
		'leadUrl'  => esc_url_raw( rest_url( 'mkn/v1/lead' ) ),
		'tracking' => array(
			'GTM_ID'                    => mkn_opt( 'gtm_id' ),
			'GA4_ID'                    => mkn_opt( 'ga4_id' ),
			'GOOGLE_ADS_ID'             => mkn_opt( 'google_ads_id' ),
			'GOOGLE_ADS_LEAD_LABEL'     => mkn_opt( 'google_ads_lead_label' ),
			'GOOGLE_ADS_WHATSAPP_LABEL' => mkn_opt( 'google_ads_wa_label' ),
			'META_PIXEL_ID'             => mkn_opt( 'meta_pixel_id' ),
			'TIKTOK_PIXEL_ID'           => mkn_opt( 'tiktok_pixel_id' ),
		),
	);
}

/* Preloads that make the first paint use the brand font and hero background. */
add_action( 'wp_head', function () {
	$a = esc_url( MKN_URI . '/assets' );
	echo '<link rel="preload" as="image" href="' . $a . '/img/brand/diffusion-dark.webp" type="image/webp" fetchpriority="high">' . "\n";
	echo '<link rel="preload" href="' . $a . '/fonts/ibm-plex-sans-arabic-400-arabic.woff2" as="font" type="font/woff2" crossorigin>' . "\n";
	echo '<link rel="preload" href="' . $a . '/fonts/ibm-plex-sans-arabic-700-arabic.woff2" as="font" type="font/woff2" crossorigin>' . "\n";
	echo '<meta name="theme-color" content="#0d1114">' . "\n";
	if ( ! has_site_icon() ) {
		echo '<link rel="icon" href="' . $a . '/img/favicon-48.png" type="image/png">' . "\n";
		echo '<link rel="apple-touch-icon" href="' . $a . '/img/apple-touch-icon.png">' . "\n";
	}
	if ( is_admin_bar_showing() ) {
		echo '<style>.admin-bar .header{top:46px}@media (min-width:783px){.admin-bar .header{top:46px}}</style>' . "\n";
	}
}, 1 );

/* Old static-site addresses (services.html, insights/slug.html …) keep working after the move to WordPress. */
add_action( 'template_redirect', function () {
	if ( ! is_404() ) {
		return;
	}
	$path = trim( (string) wp_parse_url( isset( $_SERVER['REQUEST_URI'] ) ? wp_unslash( $_SERVER['REQUEST_URI'] ) : '', PHP_URL_PATH ), '/' );
	if ( 'index.html' === $path ) {
		wp_safe_redirect( home_url( '/' ), 301 );
		exit;
	}
	if ( preg_match( '#^(services|pricing|work|testimonials|insights|about|contact|privacy)\.html$#', $path, $m ) ) {
		wp_safe_redirect( mkn_url( $m[1] ), 301 );
		exit;
	}
	if ( preg_match( '#^insights/([a-z0-9-]+)\.html$#', $path, $m ) ) {
		$post = get_page_by_path( $m[1], OBJECT, 'post' );
		if ( $post ) {
			wp_safe_redirect( get_permalink( $post ), 301 );
			exit;
		}
	}
} );
