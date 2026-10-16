<?php
defined( 'ABSPATH' ) || exit;

/*
 * Titles, descriptions, social cards, canonical URLs and structured data — the same tags the static
 * site had. Switched off automatically when an SEO plugin (Yoast or Rank Math) is active.
 */

function mkn_seo_plugin_active() {
	return defined( 'WPSEO_VERSION' ) || class_exists( 'RankMath' ) || defined( 'AIOSEO_VERSION' ) || defined( 'SEOPRESS_VERSION' );
}

/** Title and description for the current view. */
function mkn_seo_meta() {
	static $m = null;
	if ( null !== $m ) {
		return $m;
	}
	$m     = array( 'title' => '', 'desc' => '', 'type' => 'website', 'url' => '', 'robots' => '' );
	$pages = (array) mkn_site( 'pages' );
	$slug  = mkn_current_slug();
	$id    = is_singular() ? get_queried_object_id() : ( is_home() ? (int) get_option( 'page_for_posts' ) : 0 );
	if ( $slug && isset( $pages[ $slug ] ) ) {
		$m['title'] = $pages[ $slug ]['title'];
		$m['desc']  = $pages[ $slug ]['desc'];
	}
	if ( is_singular() ) {
		$post = get_queried_object();
		if ( ! $m['title'] ) {
			$m['title'] = $post->post_title . ' | MKN ARABIA';
			$m['desc']  = mkn_post_desc( $post );
		}
		if ( is_singular( 'post' ) ) {
			$m['type'] = 'article';
		}
	} elseif ( is_search() ) {
		$m['title']  = 'نتائج البحث | MKN ARABIA';
		$m['robots'] = 'noindex';
	} elseif ( is_archive() ) {
		$m['title'] = wp_strip_all_tags( get_the_archive_title() ) . ' | MKN ARABIA';
		$m['robots'] = 'noindex, follow';
	}
	// Per-page overrides from the «SEO» box.
	if ( $id ) {
		$t = mkn_meta( $id, 'seo_title' );
		$d = mkn_meta( $id, 'seo_desc' );
		if ( '' !== $t ) {
			$m['title'] = $t;
		}
		if ( '' !== $d ) {
			$m['desc'] = $d;
		}
	}
	if ( 'utm' === $slug ) {
		$m['robots'] = 'noindex, nofollow';
	} elseif ( is_404() ) {
		$m['robots'] = 'noindex';
	}
	if ( ! is_404() && 'utm' !== $slug && ! is_search() ) {
		if ( is_front_page() ) {
			$m['url'] = home_url( '/' );
		} elseif ( is_home() ) {
			$m['url'] = get_pagenum_link( max( 1, (int) get_query_var( 'paged' ) ) );
		} elseif ( is_singular() ) {
			$m['url'] = get_permalink();
		}
	}
	return $m;
}

add_filter( 'pre_get_document_title', function ( $title ) {
	if ( mkn_seo_plugin_active() ) {
		return $title;
	}
	$m = mkn_seo_meta();
	return $m['title'] ? $m['title'] : $title;
}, 20 );

add_filter( 'document_title_separator', function () {
	return '|';
} );

add_filter( 'wp_robots', function ( $robots ) {
	if ( mkn_seo_plugin_active() ) {
		return $robots;
	}
	$m = mkn_seo_meta();
	if ( false !== strpos( $m['robots'], 'noindex' ) ) {
		$robots['noindex'] = true;
	}
	if ( false !== strpos( $m['robots'], 'nofollow' ) ) {
		$robots['nofollow'] = true;
	}
	return $robots;
} );

add_action( 'wp', function () {
	if ( ! mkn_seo_plugin_active() ) {
		remove_action( 'wp_head', 'rel_canonical' );
	}
} );

add_action( 'wp_head', function () {
	if ( mkn_seo_plugin_active() ) {
		return;
	}
	$m     = mkn_seo_meta();
	$title = wp_get_document_title();
	$img   = mkn_asset( 'img/og-image.jpg' );
	if ( is_singular( 'post' ) && has_post_thumbnail() ) {
		$src = wp_get_attachment_image_src( get_post_thumbnail_id(), 'large' );
		$img = $src ? $src[0] : $img;
	}
	$tags = array(
		'<meta name="description" content="' . esc_attr( $m['desc'] ) . '">',
		'<meta property="og:site_name" content="MKN ARABIA">',
		'<meta property="og:title" content="' . esc_attr( $title ) . '">',
		'<meta property="og:description" content="' . esc_attr( $m['desc'] ) . '">',
		'<meta property="og:type" content="' . esc_attr( $m['type'] ) . '">',
		'<meta property="og:locale" content="ar_AR">',
		'<meta property="og:image" content="' . esc_url( $img ) . '">',
		'<meta property="og:image:alt" content="MKN ARABIA — سوّق بالعربي، سوّق صح">',
		'<meta name="twitter:card" content="summary_large_image">',
		'<meta name="twitter:image" content="' . esc_url( $img ) . '">',
	);
	if ( $img === mkn_asset( 'img/og-image.jpg' ) ) {
		array_splice( $tags, 7, 0, array( '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">' ) );
	}
	if ( '' === $m['desc'] ) {
		array_shift( $tags );
	}
	if ( $m['url'] ) {
		$tags[] = '<meta property="og:url" content="' . esc_url( $m['url'] ) . '">';
		$tags[] = '<link rel="canonical" href="' . esc_url( $m['url'] ) . '">';
	}
	foreach ( mkn_json_ld() as $ld ) {
		$tags[] = '<script type="application/ld+json">' . wp_json_encode( $ld, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>';
	}
	echo implode( "\n", $tags ) . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput -- escaped above
}, 2 );

/** Structured data: organisation and website on the home page, article and breadcrumbs on articles. */
function mkn_json_ld() {
	$home = home_url( '/' );
	$org  = $home . '#org';
	$out  = array();
	if ( is_front_page() ) {
		$same = array_values( array_filter( array( mkn_opt( 'instagram' ), mkn_opt( 'facebook' ), mkn_opt( 'linkedin' ) ) ) );
		$out[] = array(
			'@context'     => 'https://schema.org',
			'@type'        => 'Organization',
			'@id'          => $org,
			'name'         => 'MKN ARABIA',
			'url'          => $home,
			'logo'         => mkn_asset( 'img/logo-dark.png' ),
			'slogan'       => 'سوّق بالعربي، سوّق صح',
			'email'        => mkn_opt( 'email' ),
			'founder'      => array(
				'@type'           => 'Person',
				'@id'             => $home . '#founder',
				'name'            => 'Noureddin Abuallan',
				'alternateName'   => 'د. نور الدين أبو علّان',
				'honorificPrefix' => 'Dr.',
				'jobTitle'        => 'CEO & Founder',
				'image'           => mkn_asset( 'img/brand/founder-sq.jpg' ),
				'url'             => mkn_url( 'about' ) . '#founder',
				'sameAs'          => array_values( array_filter( array( mkn_opt( 'linkedin_founder' ) ) ) ),
			),
			'address'      => array( '@type' => 'PostalAddress', 'addressCountry' => 'JO' ),
			'areaServed'   => array( 'SA', 'AE', 'JO', 'PS', 'EG' ),
			'sameAs'       => $same,
			'contactPoint' => array(
				'@type'             => 'ContactPoint',
				'contactType'       => 'sales',
				'telephone'         => '+' . preg_replace( '/\D+/', '', mkn_opt( 'whatsapp' ) ),
				'email'             => mkn_opt( 'email' ),
				'availableLanguage' => array( 'ar', 'en' ),
				'hoursAvailable'    => array(
					'@type'     => 'OpeningHoursSpecification',
					'dayOfWeek' => array( 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday' ),
					'opens'     => '00:00',
					'closes'    => '23:59',
				),
			),
		);
		$out[] = array(
			'@context'   => 'https://schema.org',
			'@type'      => 'WebSite',
			'@id'        => $home . '#website',
			'name'       => 'MKN ARABIA',
			'url'        => $home,
			'inLanguage' => 'ar',
			'publisher'  => array( '@id' => $org ),
		);
	} elseif ( is_singular( 'post' ) ) {
		$post  = get_queried_object();
		$publ  = array( '@type' => 'Organization', '@id' => $org, 'name' => 'MKN ARABIA', 'url' => $home );
		$out[] = array(
			'@context'         => 'https://schema.org',
			'@type'            => 'Article',
			'headline'         => $post->post_title,
			'description'      => mkn_post_desc( $post ),
			'inLanguage'       => 'ar',
			'image'            => has_post_thumbnail( $post ) ? get_the_post_thumbnail_url( $post, 'large' ) : mkn_asset( 'img/og-image.jpg' ),
			'datePublished'    => get_post_time( 'c', true, $post ),
			'dateModified'     => get_post_modified_time( 'c', true, $post ),
			'author'           => $publ,
			'publisher'        => $publ + array( 'logo' => array( '@type' => 'ImageObject', 'url' => mkn_asset( 'img/logo-dark.png' ) ) ),
			'mainEntityOfPage' => get_permalink( $post ),
		);
		$out[] = array(
			'@context'        => 'https://schema.org',
			'@type'           => 'BreadcrumbList',
			'itemListElement' => array(
				array( '@type' => 'ListItem', 'position' => 1, 'name' => 'الرئيسية', 'item' => $home ),
				array( '@type' => 'ListItem', 'position' => 2, 'name' => 'المقالات', 'item' => mkn_url( 'insights' ) ),
				array( '@type' => 'ListItem', 'position' => 3, 'name' => $post->post_title ),
			),
		);
	}
	return $out;
}

/* ---------- sitemap (wp-sitemap.xml): pages and articles only, without the internal tool ---------- */
add_filter( 'wp_sitemaps_add_provider', function ( $provider, $name ) {
	return in_array( $name, array( 'users', 'taxonomies' ), true ) ? false : $provider;
}, 10, 2 );

add_filter( 'wp_sitemaps_posts_query_args', function ( $args, $post_type ) {
	if ( 'page' === $post_type ) {
		$utm = get_page_by_path( 'utm' );
		if ( $utm ) {
			$args['post__not_in'] = array_merge( isset( $args['post__not_in'] ) ? (array) $args['post__not_in'] : array(), array( $utm->ID ) );
		}
	}
	return $args;
}, 10, 2 );

/* Author archives would only repeat the articles page. */
add_action( 'template_redirect', function () {
	if ( is_author() || is_attachment() ) {
		wp_safe_redirect( is_attachment() ? home_url( '/' ) : mkn_url( 'insights' ), 301 );
		exit;
	}
}, 5 );

/* ---------- «SEO» box on pages and articles ---------- */
add_action( 'add_meta_boxes', function ( $post_type ) {
	if ( in_array( $post_type, array( 'page', 'post' ), true ) && ! mkn_seo_plugin_active() ) {
		add_meta_box( 'mkn_seo', 'الظهور في Google', 'mkn_seo_box', $post_type, 'normal', 'default' );
	}
} );

function mkn_seo_box( $post ) {
	wp_nonce_field( 'mkn_seo', 'mkn_seo_nonce' );
	$slug  = 'page' === $post->post_type ? $post->post_name : '';
	$pages = (array) mkn_site( 'pages' );
	$ph_t  = isset( $pages[ $slug ] ) ? $pages[ $slug ]['title'] : $post->post_title . ' | MKN ARABIA';
	$ph_d  = isset( $pages[ $slug ] ) ? $pages[ $slug ]['desc'] : 'يُستخدم الملخص (Excerpt) عند ترك هذا الحقل فارغًا.';
	echo '<p><label for="mkn-seo-title"><b>عنوان الصفحة في نتائج البحث</b></label><br><input type="text" class="large-text" id="mkn-seo-title" name="mkn_seo[title]" value="' . esc_attr( mkn_meta( $post->ID, 'seo_title' ) ) . '" placeholder="' . esc_attr( $ph_t ) . '"></p>';
	echo '<p><label for="mkn-seo-desc"><b>الوصف في نتائج البحث</b></label><br><textarea class="large-text" rows="2" id="mkn-seo-desc" name="mkn_seo[desc]" placeholder="' . esc_attr( $ph_d ) . '">' . esc_textarea( mkn_meta( $post->ID, 'seo_desc' ) ) . '</textarea></p>';
	echo '<p class="description">اتركهما فارغين لاستخدام العنوان والوصف الافتراضيين (الظاهرين بخط باهت).</p>';
}

add_action( 'save_post', function ( $post_id ) {
	if ( ! isset( $_POST['mkn_seo_nonce'] ) || ! wp_verify_nonce( sanitize_key( wp_unslash( $_POST['mkn_seo_nonce'] ) ), 'mkn_seo' ) ) {
		return;
	}
	if ( ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) || wp_is_post_revision( $post_id ) || ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}
	$in = isset( $_POST['mkn_seo'] ) && is_array( $_POST['mkn_seo'] ) ? wp_unslash( $_POST['mkn_seo'] ) : array(); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput -- sanitized below
	update_post_meta( $post_id, '_mkn_seo_title', sanitize_text_field( isset( $in['title'] ) ? (string) $in['title'] : '' ) );
	update_post_meta( $post_id, '_mkn_seo_desc', sanitize_textarea_field( isset( $in['desc'] ) ? (string) $in['desc'] : '' ) );
} );
