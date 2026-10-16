<?php
defined( 'ABSPATH' ) || exit;

/*
 * First-run setup: creates the pages, imports the current site content (articles, testimonials,
 * case studies, client logos with their images, FAQ) and sets permalinks and reading options.
 * Runs once, on the first request after the theme is activated. «إعدادات MKN ← استيراد المحتوى»
 * adds anything missing later: items that exist (or were deleted on purpose) are never touched,
 * and site options are only set on the first run, so edits made in the dashboard are kept.
 */

add_action( 'init', function () {
	if ( 'done' !== get_option( 'mkn_seed_state' ) && ! wp_doing_ajax() && ! wp_installing() ) {
		mkn_import_run();
	}
}, 20 );

/* Items the owner deletes for good are remembered, so a later import does not bring them back. */
add_action( 'before_delete_post', function ( $post_id ) {
	$key = get_post_meta( $post_id, '_mkn_seed_key', true );
	if ( $key ) {
		$gone         = (array) get_option( 'mkn_seed_deleted', array() );
		$gone[ $key ] = 1;
		update_option( 'mkn_seed_deleted', $gone, false );
	}
} );

/* Designed pages are found by their address, so their slug stays fixed. */
add_filter( 'wp_insert_post_data', function ( $data, $postarr ) {
	if ( ! empty( $postarr['ID'] ) && 'page' === $data['post_type'] ) {
		$key = get_post_meta( (int) $postarr['ID'], '_mkn_seed_key', true );
		if ( is_string( $key ) && 0 === strpos( $key, 'page:' ) ) {
			$data['post_name'] = substr( $key, 5 );
		}
	}
	return $data;
}, 10, 2 );

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

/** Find an item created by a previous import (also in the trash). */
function mkn_seeded( $seed_key, $type ) {
	$q = get_posts( array(
		'post_type'        => $type,
		'post_status'      => array( 'any', 'trash' ),
		'posts_per_page'   => 1,
		'fields'           => 'ids',
		'meta_key'         => '_mkn_seed_key', // phpcs:ignore WordPress.DB.SlowDBQuery -- import only
		'meta_value'       => $seed_key,       // phpcs:ignore WordPress.DB.SlowDBQuery
		'suppress_filters' => true,
	) );
	return $q ? (int) $q[0] : 0;
}

/** Was this seed item imported before (it exists, is in the trash, or was deleted on purpose)? */
function mkn_seed_skip( $seed_key, $type ) {
	$gone = (array) get_option( 'mkn_seed_deleted', array() );
	return isset( $gone[ $seed_key ] ) || mkn_seeded( $seed_key, $type );
}

/** Copy an image shipped with the theme into the media library (once per seed key). */
function mkn_import_image( $rel, $alt, $parent = 0, $key = '' ) {
	$key  = $key ? $key : 'img:' . $rel;
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

/**
 * Give an imported item its image. The pending marker is set when the item is created and removed
 * once the image is in place, so an image that failed (or an interrupted run) is retried later,
 * while an image the owner removed on purpose is not added back.
 */
function mkn_import_item_image( $id, $rel, $alt, $key = '' ) {
	if ( ! get_post_meta( $id, '_mkn_seed_image', true ) ) {
		return;
	}
	if ( ! has_post_thumbnail( $id ) ) {
		$img = mkn_import_image( $rel, $alt, $id, $key );
		if ( ! $img || ! set_post_thumbnail( $id, $img ) ) {
			return;
		}
	}
	delete_post_meta( $id, '_mkn_seed_image' );
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

/** Remove the sample post, sample page and draft privacy page WordPress creates (any language), if untouched. */
function mkn_remove_sample_content() {
	$ids = array( 1, 2 );
	$pp  = (int) get_option( 'wp_page_for_privacy_policy' );
	if ( $pp ) {
		$ids[] = $pp;
	}
	foreach ( $ids as $id ) {
		$p = get_post( $id );
		if ( ! $p || get_post_meta( $id, '_mkn_seed_key', true ) || $p->post_modified_gmt !== $p->post_date_gmt ) {
			continue;
		}
		$sample = ( 1 === $id && 'post' === $p->post_type ) || ( 2 === $id && 'page' === $p->post_type && 'publish' === $p->post_status ) || ( $pp === $id && 'page' === $p->post_type && 'draft' === $p->post_status );
		if ( $sample ) {
			wp_delete_post( $id, true );
		}
	}
}

/** Insert one seed item with its meta in a single call. */
function mkn_seed_insert( $args, $key, $meta ) {
	$meta['_mkn_seed_key'] = $key;
	$id                    = wp_insert_post( $args + array( 'post_status' => 'publish', 'meta_input' => $meta ), true );
	if ( is_wp_error( $id ) ) {
		mkn_import_log( 'تعذر إنشاء ' . ( isset( $args['post_title'] ) ? $args['post_title'] : $key ) . ': ' . $id->get_error_message() );
		return 0;
	}
	return (int) $id;
}

function mkn_import_run( $force = false ) {
	// One run at a time: add_option is atomic, a lock older than 10 minutes is stale.
	$lock = (int) get_option( 'mkn_seed_lock' );
	if ( $lock ) {
		if ( time() - $lock < 10 * MINUTE_IN_SECONDS && ! $force ) {
			return;
		}
		delete_option( 'mkn_seed_lock' );
	}
	if ( ! add_option( 'mkn_seed_lock', time(), '', 'no' ) && ! $force ) {
		return;
	}
	if ( function_exists( 'set_time_limit' ) ) {
		@set_time_limit( 300 ); // phpcs:ignore WordPress.PHP.NoSilencedErrors -- not allowed on some hosts
	}
	$first = ! get_option( 'mkn_seed_done' );
	delete_option( 'mkn_seed_log' );
	$seed = mkn_seed();

	/* Site identity and reading options: first run only, so later runs never undo the owner's choices. */
	if ( $first ) {
		if ( in_array( get_option( 'blogdescription' ), array( '', 'Just another WordPress site' ), true ) || false !== strpos( (string) get_option( 'blogdescription' ), 'WordPress' ) ) {
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
		mkn_remove_sample_content();
	}

	/* Pages. */
	$ids = array();
	foreach ( mkn_seed_pages() as $slug => $title ) {
		$p = get_page_by_path( $slug, OBJECT, 'page' );
		if ( $p ) {
			$ids[ $slug ] = $p->ID;
			if ( ! get_post_meta( $p->ID, '_mkn_seed_key', true ) ) {
				update_post_meta( $p->ID, '_mkn_seed_key', 'page:' . $slug );
			}
			continue;
		}
		if ( mkn_seed_skip( 'page:' . $slug, 'page' ) ) {
			continue;
		}
		$id = mkn_seed_insert( array( 'post_type' => 'page', 'post_title' => $title, 'post_name' => $slug, 'post_content' => '', 'comment_status' => 'closed', 'ping_status' => 'closed', 'menu_order' => count( $ids ) ), 'page:' . $slug, array() );
		if ( $id ) {
			$ids[ $slug ] = $id;
		}
	}
	if ( $first ) {
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
	}

	/* Client logos. */
	$client_ids = array();
	foreach ( (array) $seed['clients'] as $i => $c ) {
		$key = 'client:' . $c['key'];
		$id  = mkn_seeded( $key, 'mkn_client' );
		if ( ! $id && ! mkn_seed_skip( $key, 'mkn_client' ) ) {
			$id = mkn_seed_insert( array( 'post_type' => 'mkn_client', 'post_title' => $c['label'], 'menu_order' => $i ), $key, array(
				'_mkn_tone'       => (string) $c['tone'],
				'_mkn_bg'         => (string) $c['bg'],
				'_mkn_fit'        => (string) $c['fit'],
				'_mkn_clip'       => (string) $c['clip'],
				'_mkn_seed_image' => '1',
			) );
		}
		if ( $id ) {
			mkn_import_item_image( $id, 'clients/' . $c['file'], $c['label'] );
			$client_ids[ $c['key'] ] = $id;
		}
	}

	/* Case studies (each with its own copy of its image, so removing a client logo never empties a case). */
	foreach ( (array) $seed['cases'] as $i => $c ) {
		$key = 'case:' . $c['slug'];
		$id  = mkn_seeded( $key, 'mkn_case' );
		if ( ! $id && ! mkn_seed_skip( $key, 'mkn_case' ) ) {
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
				'seed_image' => '1',
			);
			$in = array();
			foreach ( $meta as $f => $v ) {
				$in[ '_mkn_' . $f ] = (string) $v;
			}
			$id = mkn_seed_insert( array( 'post_type' => 'mkn_case', 'post_title' => $c['name'], 'post_name' => $c['slug'], 'menu_order' => $i ), $key, $in );
		}
		if ( $id ) {
			mkn_import_item_image( $id, $c['image'], ! empty( $c['image_alt'] ) ? $c['image_alt'] : $c['name'], 'img:case:' . $c['image'] );
		}
	}

	/* Testimonials. */
	foreach ( (array) $seed['testimonials'] as $i => $t ) {
		$key = 'testimonial:' . md5( $t['brand'] . '|' . $t['country'] );
		if ( mkn_seed_skip( $key, 'mkn_testimonial' ) ) {
			continue;
		}
		mkn_seed_insert( array( 'post_type' => 'mkn_testimonial', 'post_title' => $t['brand'], 'menu_order' => $i ), $key, array(
			'_mkn_text'       => $t['text'],
			'_mkn_place'      => $t['place'],
			'_mkn_country'    => $t['country'],
			'_mkn_case'       => $t['case'],
			'_mkn_featured'   => $t['featured'] ? '1' : '',
			'_mkn_logo'       => $t['logo'] && isset( $client_ids[ $t['logo'] ] ) ? (string) $client_ids[ $t['logo'] ] : '',
			'_mkn_seed_brand' => $t['brand'],
		) );
	}

	/* FAQ. */
	foreach ( (array) $seed['faq'] as $i => $f ) {
		$key = 'faq:' . md5( $f['q'] );
		if ( ! mkn_seed_skip( $key, 'mkn_faq' ) ) {
			mkn_seed_insert( array( 'post_type' => 'mkn_faq', 'post_title' => $f['q'], 'menu_order' => $i ), $key, array( '_mkn_answer' => $f['a'] ) );
		}
	}

	/* Articles: newest first, in the same order as the static site. */
	foreach ( (array) $seed['articles'] as $i => $a ) {
		$key = 'article:' . $a['slug'];
		if ( mkn_seed_skip( $key, 'post' ) || get_page_by_path( $a['slug'], OBJECT, 'post' ) ) {
			continue;
		}
		$related = array();
		foreach ( (array) $a['related'] as $r ) {
			$related[] = $r[1] . ' | ' . mkn_seed_link( $r[0] );
		}
		$date = gmdate( 'Y-m-d H:i:s', strtotime( '2026-10-11 09:00:00' ) - ( $i * DAY_IN_SECONDS ) );
		mkn_seed_insert( array(
			'post_type'      => 'post',
			'post_title'     => $a['title'],
			'post_name'      => $a['slug'],
			'post_excerpt'   => $a['desc'],
			'post_content'   => mkn_to_blocks( $a['content'] ),
			'post_date_gmt'  => $date,
			'post_date'      => get_date_from_gmt( $date ),
			'comment_status' => 'closed',
			'ping_status'    => 'closed',
		), $key, array(
			'_mkn_topic'     => $a['topic'],
			'_mkn_cta'       => $a['cta'],
			'_mkn_seo_title' => $a['seo'],
			'_mkn_related'   => implode( "\n", $related ),
		) );
	}

	if ( $first ) {
		mkn_write_htaccess();
	}

	update_option( 'mkn_seed_version', MKN_VERSION, false );
	update_option( 'mkn_seed_done', time(), false );
	update_option( 'mkn_seed_state', 'done', true );
	delete_option( 'mkn_seed_lock' );
	mkn_flush_page_cache();
}

/* /insights/page/2/ belongs to the articles page, not to an article called "page". */
function mkn_rewrite_rules() {
	add_rewrite_rule( '^insights/page/?([0-9]{1,})/?$', 'index.php?pagename=insights&paged=$matches[1]', 'top' );
}
add_action( 'init', 'mkn_rewrite_rules' );

/*
 * Server rules that WordPress itself does not add (data/htaccess.txt): old static addresses, browser
 * caching for the theme files and security headers. Written once, before the WordPress block.
 */
function mkn_write_htaccess() {
	require_once ABSPATH . 'wp-admin/includes/file.php';
	$file = trailingslashit( get_home_path() ) . '.htaccess';
	if ( ! file_exists( $file ) || ! is_writable( $file ) ) {
		mkn_import_log( 'لم يُعدَّل ملف ‎.htaccess (غير موجود أو غير قابل للكتابة).' );
		return;
	}
	// HTTPS is forced by Hostinger itself (hPanel ← SSL, switched on by the deploy script). The block is
	// shared with tools/deploy/hostinger_deploy.py, which writes the same lines.
	$rules = file_get_contents( MKN_DIR . '/data/htaccess.txt' );
	if ( ! $rules || false === strpos( $rules, '# END MKN ARABIA' ) ) {
		return;
	}
	$current = file_get_contents( $file );
	$current = false === $current ? null : preg_replace( '/# BEGIN MKN ARABIA.*?# END MKN ARABIA\R*/s', '', $current );
	if ( null === $current ) {
		mkn_import_log( 'لم يُعدَّل ملف ‎.htaccess (تعذرت قراءته).' );
		return;
	}
	if ( ! file_exists( $file . '.mkn-backup' ) ) {
		@copy( $file, $file . '.mkn-backup' ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
	}
	file_put_contents( $file, trim( $rules ) . "\n\n" . ltrim( $current ), LOCK_EX ); // phpcs:ignore WordPress.WP.AlternativeFunctions
}
