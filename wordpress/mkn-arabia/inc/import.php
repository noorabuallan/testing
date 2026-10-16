<?php
defined( 'ABSPATH' ) || exit;

/*
 * First-run setup: creates the pages, imports the current site content (articles, testimonials,
 * case studies, client logos with their images, FAQ) and sets permalinks and reading options.
 * Runs once after the theme is activated; safe to run again from «إعدادات MKN ← استيراد المحتوى»
 * — items that already exist are never overwritten, so edits made in the dashboard are kept.
 */

add_action( 'after_switch_theme', function () {
	update_option( 'mkn_seed_state', 'pending', true );
} );

add_action( 'init', function () {
	if ( 'done' !== get_option( 'mkn_seed_state' ) && ! wp_doing_ajax() && ! wp_installing() ) {
		mkn_import_run();
	}
}, 20 );

/** Page slug => title for the designed pages. */
function mkn_seed_pages() {
	return array(
		'home'         => 'الرئيسية',
		'services'     => 'الخدمات',
		'pricing'      => 'الباقات',
		'work'         => 'أعمالنا',
		'testimonials' => 'آراء العملاء',
		'insights'     => 'المقالات',
		'about'        => 'من نحن',
		'contact'      => 'تواصل',
		'privacy'      => 'سياسة الخصوصية',
		'utm'          => 'منشئ روابط الحملات',
	);
}

/** Find an item created by a previous import. */
function mkn_seeded( $seed_key, $type ) {
	$q = get_posts( array(
		'post_type'        => $type,
		'post_status'      => 'any',
		'posts_per_page'   => 1,
		'fields'           => 'ids',
		'meta_key'         => '_mkn_seed_key', // phpcs:ignore WordPress.DB.SlowDBQuery -- one-time import
		'meta_value'       => $seed_key,       // phpcs:ignore WordPress.DB.SlowDBQuery
		'suppress_filters' => true,
	) );
	return $q ? (int) $q[0] : 0;
}

/** Copy an image shipped with the theme into the media library (once). */
function mkn_import_image( $rel, $alt, $parent = 0 ) {
	$key  = 'img:' . $rel;
	$have = mkn_seeded( $key, 'attachment' );
	if ( $have ) {
		return $have;
	}
	$src = MKN_DIR . '/assets/img/' . $rel;
	if ( ! is_readable( $src ) ) {
		return 0;
	}
	require_once ABSPATH . 'wp-admin/includes/file.php';
	require_once ABSPATH . 'wp-admin/includes/media.php';
	require_once ABSPATH . 'wp-admin/includes/image.php';
	$tmp = wp_tempnam( basename( $src ) );
	if ( ! $tmp || ! copy( $src, $tmp ) ) {
		return 0;
	}
	$id = media_handle_sideload( array( 'name' => basename( $src ), 'tmp_name' => $tmp ), $parent, $alt );
	if ( is_wp_error( $id ) ) {
		wp_delete_file( $tmp );
		mkn_import_log( 'تعذر رفع الصورة ' . $rel . ': ' . $id->get_error_message() );
		return 0;
	}
	update_post_meta( $id, '_wp_attachment_image_alt', $alt );
	update_post_meta( $id, '_mkn_seed_key', $key );
	return (int) $id;
}

function mkn_import_log( $msg ) {
	$log   = (array) get_option( 'mkn_seed_log', array() );
	$log[] = $msg;
	update_option( 'mkn_seed_log', array_slice( $log, -50 ), false );
}

/** Simple HTML (p, h2, ul) to editor blocks, so articles open as normal blocks in the editor. */
function mkn_to_blocks( $html ) {
	preg_match_all( '/<(p|h2|h3|ul|ol)\b([^>]*)>.*?<\/\1>/su', $html, $m, PREG_SET_ORDER );
	$out = array();
	foreach ( $m as $el ) {
		list( $full, $tag, $attrs ) = $el;
		$class = preg_match( '/class="([^"]+)"/', $attrs, $c ) ? $c[1] : '';
		if ( 'p' === $tag ) {
			$out[] = '<!-- wp:paragraph' . ( $class ? ' {"className":"' . $class . '"}' : '' ) . " -->\n" . $full . "\n<!-- /wp:paragraph -->";
		} elseif ( 'h2' === $tag || 'h3' === $tag ) {
			$inner = preg_replace( '/^<h[23][^>]*>|<\/h[23]>$/', '', $full );
			$attr  = 'h3' === $tag ? ' {"level":3}' : '';
			$out[] = '<!-- wp:heading' . $attr . " -->\n<" . $tag . ' class="wp-block-heading">' . $inner . '</' . $tag . ">\n<!-- /wp:heading -->";
		} else {
			$out[] = "<!-- wp:html -->\n" . $full . "\n<!-- /wp:html -->";
		}
	}
	return implode( "\n\n", $out );
}

/** Turn {{u:slug}}#hash placeholders into site-relative links (/services/#d04). */
function mkn_seed_link( $href ) {
	if ( preg_match( '/^\{\{u:([a-z0-9-]+)\}\}(#.*)?$/', $href, $m ) ) {
		return wp_make_link_relative( mkn_url( $m[1] ) ) . ( isset( $m[2] ) ? $m[2] : '' );
	}
	return $href;
}

function mkn_import_run( $force = false ) {
	if ( ! $force && get_transient( 'mkn_seed_lock' ) ) {
		return;
	}
	set_transient( 'mkn_seed_lock', 1, 5 * MINUTE_IN_SECONDS );
	if ( function_exists( 'set_time_limit' ) ) {
		@set_time_limit( 300 ); // phpcs:ignore WordPress.PHP.NoSilencedErrors -- not allowed on some hosts
	}
	delete_option( 'mkn_seed_log' );
	$seed = mkn_seed();

	/* Site identity and reading options. */
	if ( 'Just another WordPress site' === get_option( 'blogdescription' ) || '' === get_option( 'blogdescription' ) ) {
		update_option( 'blogdescription', 'سوّق بالعربي، سوّق صح' );
	}
	if ( in_array( get_option( 'blogname' ), array( '', 'My WordPress Website', 'My Blog', 'My WordPress Blog', 'WordPress' ), true ) ) {
		update_option( 'blogname', 'MKN ARABIA' );
	}
	update_option( 'default_comment_status', 'closed' );
	update_option( 'default_ping_status', 'closed' );
	update_option( 'timezone_string', 'Asia/Amman' );
	if ( (int) get_option( 'posts_per_page' ) < 12 ) {
		update_option( 'posts_per_page', 12 );
	}

	/* Remove WordPress sample content (only if it was never edited). */
	foreach ( array( array( 'hello-world', 'post' ), array( 'sample-page', 'page' ), array( 'privacy-policy', 'page' ) ) as $s ) {
		$p = get_page_by_path( $s[0], OBJECT, $s[1] );
		if ( $p && $p->post_modified_gmt === $p->post_date_gmt && ( 'privacy-policy' !== $s[0] || 'draft' === $p->post_status ) ) {
			wp_delete_post( $p->ID, true );
		}
	}

	/* Pages. */
	$ids = array();
	foreach ( mkn_seed_pages() as $slug => $title ) {
		$p = get_page_by_path( $slug, OBJECT, 'page' );
		if ( $p ) {
			$ids[ $slug ] = $p->ID;
			continue;
		}
		$id = wp_insert_post( array(
			'post_type'      => 'page',
			'post_status'    => 'publish',
			'post_title'     => $title,
			'post_name'      => $slug,
			'post_content'   => '',
			'comment_status' => 'closed',
			'ping_status'    => 'closed',
			'menu_order'     => count( $ids ),
		), true );
		if ( is_wp_error( $id ) ) {
			mkn_import_log( 'تعذر إنشاء صفحة ' . $title );
			continue;
		}
		update_post_meta( $id, '_mkn_seed_key', 'page:' . $slug );
		$ids[ $slug ] = $id;
	}
	if ( ! empty( $ids['home'] ) && ! empty( $ids['insights'] ) ) {
		update_option( 'show_on_front', 'page' );
		update_option( 'page_on_front', $ids['home'] );
		update_option( 'page_for_posts', $ids['insights'] );
	}
	if ( ! empty( $ids['privacy'] ) ) {
		update_option( 'wp_page_for_privacy_policy', $ids['privacy'] );
	}

	/* Articles live under /insights/. */
	if ( '/insights/%postname%/' !== get_option( 'permalink_structure' ) ) {
		global $wp_rewrite;
		$wp_rewrite->set_permalink_structure( '/insights/%postname%/' );
	}
	mkn_rewrite_rules();
	require_once ABSPATH . 'wp-admin/includes/misc.php';
	require_once ABSPATH . 'wp-admin/includes/file.php';
	flush_rewrite_rules( true );

	/* Client logos. */
	$client_ids = array();
	foreach ( (array) $seed['clients'] as $i => $c ) {
		$key = 'client:' . $c['key'];
		$id  = mkn_seeded( $key, 'mkn_client' );
		if ( ! $id ) {
			$id = wp_insert_post( array( 'post_type' => 'mkn_client', 'post_status' => 'publish', 'post_title' => $c['label'], 'menu_order' => $i ), true );
			if ( is_wp_error( $id ) ) {
				continue;
			}
			update_post_meta( $id, '_mkn_seed_key', $key );
			foreach ( array( 'tone', 'bg', 'fit', 'clip' ) as $f ) {
				update_post_meta( $id, '_mkn_' . $f, (string) $c[ $f ] );
			}
			$img = mkn_import_image( 'clients/' . $c['file'], $c['label'], $id );
			if ( $img ) {
				set_post_thumbnail( $id, $img );
			}
		}
		$client_ids[ $c['key'] ] = $id;
	}

	/* Case studies. */
	foreach ( (array) $seed['cases'] as $i => $c ) {
		$key = 'case:' . $c['slug'];
		if ( mkn_seeded( $key, 'mkn_case' ) ) {
			continue;
		}
		$id = wp_insert_post( array( 'post_type' => 'mkn_case', 'post_status' => 'publish', 'post_title' => $c['name'], 'post_name' => $c['slug'], 'menu_order' => $i ), true );
		if ( is_wp_error( $id ) ) {
			continue;
		}
		update_post_meta( $id, '_mkn_seed_key', $key );
		$meta = array(
			'sub'        => $c['sub'],
			'challenge'  => $c['challenge'],
			'role'       => $c['role'],
			'done'       => $c['done'],
			'outputs'    => $c['outputs'],
			'reading'    => $c['reading'],
			'depts'      => implode( ',', (array) $c['depts'] ),
			'bundle'     => $c['bundle'],
			'index_name' => isset( $c['index_name'] ) && $c['index_name'] !== $c['name'] ? $c['index_name'] : '',
			'index_sub'  => $c['index_sub'] !== $c['sub'] ? $c['index_sub'] : '',
			'featured'   => $c['featured'] ? '1' : '',
			'teaser'     => $c['teaser'],
			'tile'       => $c['tile'],
			'wide'       => $c['wide'] ? '1' : '',
		);
		foreach ( $meta as $f => $v ) {
			update_post_meta( $id, '_mkn_' . $f, (string) $v );
		}
		$img = mkn_import_image( $c['image'], ! empty( $c['image_alt'] ) ? $c['image_alt'] : $c['name'], $id );
		if ( $img ) {
			set_post_thumbnail( $id, $img );
		}
	}

	/* Testimonials. */
	foreach ( (array) $seed['testimonials'] as $i => $t ) {
		$key = 'testimonial:' . md5( $t['brand'] . '|' . $t['country'] );
		if ( mkn_seeded( $key, 'mkn_testimonial' ) ) {
			continue;
		}
		$id = wp_insert_post( array( 'post_type' => 'mkn_testimonial', 'post_status' => 'publish', 'post_title' => $t['brand'], 'menu_order' => $i ), true );
		if ( is_wp_error( $id ) ) {
			continue;
		}
		update_post_meta( $id, '_mkn_seed_key', $key );
		update_post_meta( $id, '_mkn_text', $t['text'] );
		update_post_meta( $id, '_mkn_place', $t['place'] );
		update_post_meta( $id, '_mkn_country', $t['country'] );
		update_post_meta( $id, '_mkn_case', $t['case'] );
		update_post_meta( $id, '_mkn_featured', $t['featured'] ? '1' : '' );
		update_post_meta( $id, '_mkn_logo', $t['logo'] && isset( $client_ids[ $t['logo'] ] ) ? (string) $client_ids[ $t['logo'] ] : '' );
	}

	/* FAQ. */
	foreach ( (array) $seed['faq'] as $i => $f ) {
		$key = 'faq:' . md5( $f['q'] );
		if ( mkn_seeded( $key, 'mkn_faq' ) ) {
			continue;
		}
		$id = wp_insert_post( array( 'post_type' => 'mkn_faq', 'post_status' => 'publish', 'post_title' => $f['q'], 'menu_order' => $i ), true );
		if ( ! is_wp_error( $id ) ) {
			update_post_meta( $id, '_mkn_seed_key', $key );
			update_post_meta( $id, '_mkn_answer', $f['a'] );
		}
	}

	/* Articles: newest first, in the same order as the static site. */
	$n = count( (array) $seed['articles'] );
	foreach ( (array) $seed['articles'] as $i => $a ) {
		$key = 'article:' . $a['slug'];
		if ( mkn_seeded( $key, 'post' ) || get_page_by_path( $a['slug'], OBJECT, 'post' ) ) {
			continue;
		}
		$date = gmdate( 'Y-m-d H:i:s', strtotime( '2026-10-11 09:00:00' ) - ( $i * DAY_IN_SECONDS ) );
		$id   = wp_insert_post( array(
			'post_type'      => 'post',
			'post_status'    => 'publish',
			'post_title'     => $a['title'],
			'post_name'      => $a['slug'],
			'post_excerpt'   => $a['desc'],
			'post_content'   => mkn_to_blocks( $a['content'] ),
			'post_date_gmt'  => $date,
			'post_date'      => get_date_from_gmt( $date ),
			'comment_status' => 'closed',
			'ping_status'    => 'closed',
		), true );
		if ( is_wp_error( $id ) ) {
			mkn_import_log( 'تعذر إنشاء المقال ' . $a['title'] );
			continue;
		}
		$related = array();
		foreach ( (array) $a['related'] as $r ) {
			$related[] = $r[1] . ' | ' . mkn_seed_link( $r[0] );
		}
		update_post_meta( $id, '_mkn_seed_key', $key );
		update_post_meta( $id, '_mkn_topic', $a['topic'] );
		update_post_meta( $id, '_mkn_cta', $a['cta'] );
		update_post_meta( $id, '_mkn_seo_title', $a['seo'] );
		update_post_meta( $id, '_mkn_related', implode( "\n", $related ) );
	}
	unset( $n );

	mkn_write_htaccess();

	update_option( 'mkn_seed_version', MKN_VERSION, false );
	update_option( 'mkn_seed_done', time(), false );
	update_option( 'mkn_seed_state', 'done', true );
	delete_transient( 'mkn_seed_lock' );
	mkn_flush_page_cache();
}

/* /insights/page/2/ belongs to the articles page, not to an article called "page". */
function mkn_rewrite_rules() {
	add_rewrite_rule( '^insights/page/?([0-9]{1,})/?$', 'index.php?pagename=insights&paged=$matches[1]', 'top' );
}
add_action( 'init', 'mkn_rewrite_rules' );

/*
 * Server rules that WordPress itself does not add: HTTPS and the non-www domain, browser caching for
 * the theme files, security headers. Written once, before the WordPress block, between markers.
 */
function mkn_write_htaccess() {
	require_once ABSPATH . 'wp-admin/includes/file.php';
	$file = trailingslashit( get_home_path() ) . '.htaccess';
	if ( ! file_exists( $file ) || ! is_writable( $file ) ) {
		mkn_import_log( 'لم يُعدَّل ملف ‎.htaccess (غير موجود أو غير قابل للكتابة).' );
		return;
	}
	$host  = (string) wp_parse_url( home_url(), PHP_URL_HOST );
	$https = 0 === strpos( home_url(), 'https://' );
	$bare  = preg_replace( '/^www\./', '', $host );
	$rules = array( '# BEGIN MKN ARABIA' );
	if ( $https && $host === $bare && false === strpos( $host, 'localhost' ) ) {
		$rules = array_merge( $rules, array(
			'<IfModule mod_rewrite.c>',
			'RewriteEngine On',
			'RewriteCond %{HTTPS} !=on',
			'RewriteRule ^ https://' . $host . '%{REQUEST_URI} [L,R=301]',
			'RewriteCond %{HTTP_HOST} ^www\.' . preg_quote( $host, '' ) . '$ [NC]',
			'RewriteRule ^ https://' . $host . '%{REQUEST_URI} [L,R=301]',
			'</IfModule>',
		) );
	}
	$rules = array_merge( $rules, array(
		'<IfModule mod_expires.c>',
		'  ExpiresActive On',
		'  ExpiresByType text/css "access plus 1 year"',
		'  ExpiresByType application/javascript "access plus 1 year"',
		'  ExpiresByType font/woff2 "access plus 1 year"',
		'  ExpiresByType image/webp "access plus 6 months"',
		'  ExpiresByType image/png "access plus 6 months"',
		'  ExpiresByType image/jpeg "access plus 6 months"',
		'</IfModule>',
		'AddType font/woff2 .woff2',
		'<IfModule mod_headers.c>',
		'  Header always set X-Content-Type-Options "nosniff"',
		'  Header always set Referrer-Policy "strict-origin-when-cross-origin"',
		'  Header always set X-Frame-Options "SAMEORIGIN"',
		'  Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"',
		'</IfModule>',
		'# END MKN ARABIA',
	) );
	$current = (string) file_get_contents( $file );
	$current = preg_replace( '/# BEGIN MKN ARABIA.*?# END MKN ARABIA\R*/su', '', $current );
	if ( ! file_exists( $file . '.mkn-backup' ) ) {
		@copy( $file, $file . '.mkn-backup' ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
	}
	file_put_contents( $file, implode( "\n", $rules ) . "\n\n" . ltrim( $current ), LOCK_EX ); // phpcs:ignore WordPress.WP.AlternativeFunctions
}
