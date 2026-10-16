<?php
defined( 'ABSPATH' ) || exit;

/* The designed markup is used as-is: no curly-quote or dash rewriting of Arabic text. */
add_filter( 'run_wptexturize', '__return_false' );

/** URL of a designed page by its slug (home, services, …, insights). */
function mkn_url( $slug ) {
	static $cache = array();
	if ( isset( $cache[ $slug ] ) ) {
		return $cache[ $slug ];
	}
	$url = '';
	if ( 'home' === $slug ) {
		$url = home_url( '/' );
	} elseif ( 'insights' === $slug && get_option( 'page_for_posts' ) ) {
		$url = get_permalink( (int) get_option( 'page_for_posts' ) );
	} else {
		$page = get_page_by_path( $slug, OBJECT, 'page' );
		if ( $page && in_array( $page->post_status, array( 'publish', 'private' ), true ) ) {
			$url = get_permalink( $page );
		}
	}
	if ( ! $url ) {
		$url = home_url( '/' . $slug . '/' );
	}
	$cache[ $slug ] = $url;
	return $url;
}

/** Permalink of an article by slug (falls back to the articles page). */
function mkn_post_url( $slug ) {
	$p = get_page_by_path( $slug, OBJECT, 'post' );
	return ( $p && 'publish' === $p->post_status ) ? get_permalink( $p ) : mkn_url( 'insights' );
}

function mkn_asset( $rel ) {
	return MKN_URI . '/assets/' . ltrim( $rel, '/' );
}

/** BOOK_A from the generator: the attributes of every «احجز» link. */
function mkn_book_attrs() {
	return 'href="' . esc_url( mkn_opt( 'book' ) ) . '" target="_blank" rel="noopener" data-book';
}

/** «@name» shown next to a social link, or '' when the address has no simple handle (profile.php?id=…). */
function mkn_social_handle( $url ) {
	$path = trim( (string) wp_parse_url( $url, PHP_URL_PATH ), '/' );
	return ( '' !== $path && false === strpos( $path, '/' ) && false === strpos( $path, '.' ) ) ? '@' . $path : '';
}

/** WhatsApp number as shown to visitors (falls back to the dialling number). */
function mkn_wa_display() {
	return '' !== mkn_opt( 'wa_display' ) ? mkn_opt( 'wa_display' ) : '+' . mkn_opt( 'whatsapp' );
}

/** Replace {{…}} placeholders in generated markup. Links whose setting was emptied are left out. */
function mkn_fill_placeholders( $html ) {
	foreach ( array( 'instagram', 'facebook', 'linkedin' ) as $k ) {
		$pattern = '/<a href="\{\{' . $k . '\}\}"[^>]*>.*?<\/a>/su';
		if ( '' === mkn_opt( $k ) ) {
			$html = preg_replace( $pattern, '', $html );
		} elseif ( 'linkedin' !== $k ) {
			$handle = mkn_social_handle( mkn_opt( $k ) );
			$handle = $handle ? $handle : ucfirst( $k );
			$html   = preg_replace_callback( $pattern, function ( $m ) use ( $handle ) {
				return preg_replace( '/<b>@[^<]*<\/b>/u', '<b>' . esc_html( $handle ) . '</b>', $m[0] );
			}, $html );
		}
	}
	if ( '' === mkn_opt( 'linkedin_founder' ) ) {
		$html = preg_replace( '/ · <a href="\{\{linkedin_founder\}\}"[^>]*>.*?<\/a>/su', '', $html );
	}
	if ( '' === mkn_opt( 'book_embed' ) ) {
		$html = preg_replace( '/<iframe src="\{\{book_embed\}\}"[^>]*><\/iframe>\s*(<div class="booking__alt">)<p class="form-note">[^<]*<\/p>/su', '$1', $html );
	}
	$map = array(
		'{{a}}'                => esc_url( MKN_URI . '/assets' ),
		'{{book}}'             => esc_url( mkn_opt( 'book' ) ),
		'{{book_embed}}'       => esc_url( mkn_opt( 'book_embed' ) ),
		'{{email}}'            => esc_html( mkn_opt( 'email' ) ),
		'{{wa_display}}'       => esc_html( mkn_wa_display() ),
		'{{instagram}}'        => esc_url( mkn_opt( 'instagram' ) ),
		'{{facebook}}'         => esc_url( mkn_opt( 'facebook' ) ),
		'{{linkedin}}'         => esc_url( mkn_opt( 'linkedin' ) ),
		'{{linkedin_founder}}' => esc_url( mkn_opt( 'linkedin_founder' ) ),
	);
	$html = strtr( $html, $map );
	$html = preg_replace_callback( '/\{\{u:([a-z0-9-]+)\}\}/', function ( $m ) {
		return esc_url( mkn_url( $m[1] ) );
	}, $html );
	return preg_replace_callback( '/\{\{post:([a-z0-9-]+)\}\}/', function ( $m ) {
		return esc_url( mkn_post_url( $m[1] ) );
	}, $html );
}

/** A designed page with its dynamic parts filled in. */
function mkn_fragment( $slug ) {
	$file = MKN_DIR . '/fragments/' . $slug . '.html';
	if ( ! preg_match( '/^[a-z0-9-]+$/', $slug ) || ! is_readable( $file ) ) {
		return '';
	}
	$html = (string) file_get_contents( $file );
	$html = preg_replace_callback( '/\[\[([a-z_]+)(?:\|([^\]]*))?\]\]/u', function ( $m ) {
		return mkn_slot( $m[1], isset( $m[2] ) ? $m[2] : '' );
	}, $html );
	return mkn_fill_placeholders( $html );
}

/** Dynamic parts of the designed pages. */
function mkn_slot( $name, $arg ) {
	switch ( $name ) {
		case 'logos_rail':
			return mkn_logos_rail( $arg );
		case 'logo_wall':
			return '<div class="logo-wall">' . implode( '', array_map( 'mkn_logo_tile', mkn_items( 'mkn_client' ) ) ) . '</div>';
		case 'proof_quotes':
			$want = array_filter( array_map( 'trim', explode( ',', $arg ) ) );
			$used = array();
			foreach ( $want as $brand ) {
				$t = mkn_testimonial_by_brand( $brand );
				if ( $t ) {
					$used[ $t->ID ] = $t;
				}
			}
			foreach ( mkn_featured( 'mkn_testimonial' ) as $t ) { // keep the strip full if a quote was removed
				if ( count( $used ) >= count( $want ) ) {
					break;
				}
				$used[ $t->ID ] = $t;
			}
			return implode( '', array_map( 'mkn_tcard', array_values( $used ) ) );
		case 'brands_count':
			$brands = array();
			foreach ( mkn_items( 'mkn_testimonial' ) as $t ) {
				$brands[ preg_replace( '/\s*—.*$/u', '', $t->post_title ) ] = 1;
			}
			return (string) count( $brands );
		case 'testimonials_featured':
			return implode( '', array_map( 'mkn_tcard', mkn_featured( 'mkn_testimonial' ) ) );
		case 'testimonials_count':
			return (string) count( mkn_items( 'mkn_testimonial' ) );
		case 'testimonial_groups':
			return mkn_testimonial_groups();
		case 'testimonial_jump':
			return mkn_testimonial_jump();
		case 'countries_phrase':
			return mkn_countries_phrase( count( mkn_testimonial_countries() ) );
		case 'feature_cases':
			return mkn_feature_cases();
		case 'case_index':
			return mkn_case_index();
		case 'cases_count':
			return (string) count( mkn_items( 'mkn_case' ) );
		case 'cases_full':
			return mkn_cases_full();
		case 'insights_latest':
			return mkn_insight_cards( get_posts( array( 'posts_per_page' => max( 1, (int) $arg ), 'post_status' => 'publish', 'ignore_sticky_posts' => true ) ) );
		case 'insights_all':
			return mkn_insights_all();
		case 'faq':
			return mkn_faq();
		case 'faq_count':
			return sprintf( '%02d', count( mkn_items( 'mkn_faq' ) ) );
	}
	return '';
}

function mkn_featured( $type ) {
	return array_values( array_filter( mkn_items( $type ), function ( $p ) {
		return '1' === mkn_meta( $p->ID, 'featured' );
	} ) );
}

/* ---------- client logos ---------- */

/**
 * [url, width, height, attachment id] of an item's image. Full size is used so approved logo files are
 * shown exactly as supplied; only an oversized upload (wider than 1200px) is swapped for its large copy.
 */
function mkn_image( $post_id ) {
	$id = get_post_thumbnail_id( $post_id );
	if ( ! $id ) {
		return null;
	}
	$src = wp_get_attachment_image_src( $id, 'full' );
	if ( $src && (int) $src[1] > 1200 ) {
		$large = wp_get_attachment_image_src( $id, 'large' );
		$src   = $large ? $large : $src;
	}
	return $src ? array( $src[0], (int) $src[1], (int) $src[2], $id ) : null;
}

/** srcset/sizes attributes for a photo, when WordPress has smaller copies of it. */
function mkn_srcset( $attachment_id, $sizes ) {
	$set = wp_get_attachment_image_srcset( $attachment_id, 'full' );
	return $set ? ' srcset="' . esc_attr( $set ) . '" sizes="' . esc_attr( $sizes ) . '"' : '';
}

function mkn_logo_tile( $client, $eager = false ) {
	$img = mkn_image( $client->ID );
	if ( ! $img ) {
		return '';
	}
	$tone  = mkn_meta( $client->ID, 'tone' );
	$style = 'custom' === $tone && mkn_meta( $client->ID, 'bg' ) ? ' style="background:' . esc_attr( mkn_meta( $client->ID, 'bg' ) ) . '"' : '';
	$cls   = 'dark' === $tone ? ' ltile--dark' : ( 'custom' === $tone ? ' ltile--custom' : '' );
	$cls  .= 'fill' === mkn_meta( $client->ID, 'fit' ) ? ' ltile--fill' : '';
	$clip  = mkn_meta( $client->ID, 'clip' ) ? ' style="clip-path:' . esc_attr( mkn_meta( $client->ID, 'clip' ) ) . '"' : '';
	$load  = $eager ? ' loading="eager" fetchpriority="low" decoding="async"' : ' loading="lazy"';
	return '<span class="ltile' . $cls . '"' . $style . '><img src="' . esc_url( $img[0] ) . '" alt="' . esc_attr( $client->post_title ) . '" width="' . $img[1] . '" height="' . $img[2] . '"' . $load . $clip . '></span>';
}

/** Visual clones for the seamless loop: hidden from assistive tech and from reduced motion. */
function mkn_dup( $r ) {
	$r = str_replace( ' loading="eager" fetchpriority="low" decoding="async"', ' loading="lazy"', $r );
	$r = str_replace( '<span class="ltile', '<span aria-hidden="true" class="dup ltile', $r );
	return preg_replace( '/ alt="[^"]*"/', ' alt=""', $r );
}

function mkn_logos_rail( $sub ) {
	$items = mkn_items( 'mkn_client' );
	if ( ! $items ) {
		return '';
	}
	$half = (int) ceil( count( $items ) / 2 );
	$r1   = '';
	$r2   = '';
	foreach ( $items as $i => $c ) {
		$tile = mkn_logo_tile( $c, true ); // clipped by the rail, so lazy-loading would leave blank tiles
		if ( $i < $half ) {
			$r1 .= $tile;
		} else {
			$r2 .= $tile;
		}
	}
	return '<section class="logos" aria-labelledby="h-logos">
  <div class="container logos__head"><span class="label">TRUSTED BY</span><h2 id="h-logos">علامات تجارية عملنا معها</h2><p class="muted">' . esc_html( $sub ) . '</p>
    <button type="button" class="motion-toggle">إيقاف الحركة</button></div>
  <div class="logo-rail"><div class="logo-track">' . $r1 . mkn_dup( $r1 ) . mkn_dup( $r1 ) . '</div></div>
  <div class="logo-rail logo-rail--rev"><div class="logo-track">' . $r2 . mkn_dup( $r2 ) . mkn_dup( $r2 ) . '</div></div>
</section>';
}

/* ---------- testimonials ---------- */

function mkn_testimonial_by_brand( $brand ) {
	$brand = html_entity_decode( $brand, ENT_QUOTES, 'UTF-8' );
	foreach ( mkn_items( 'mkn_testimonial' ) as $t ) {
		if ( html_entity_decode( $t->post_title, ENT_QUOTES, 'UTF-8' ) === $brand || mkn_meta( $t->ID, 'seed_brand' ) === $brand ) {
			return $t;
		}
	}
	return null;
}

/** Country codes (in display order) that have at least one published testimonial. */
function mkn_testimonial_countries() {
	$have = array();
	foreach ( mkn_items( 'mkn_testimonial' ) as $t ) {
		$have[ mkn_meta( $t->ID, 'country' ) ] = 1;
	}
	$out = array();
	foreach ( (array) mkn_site( 'countries' ) as $c ) {
		if ( isset( $have[ $c[0] ] ) ) {
			$out[] = $c;
		}
	}
	return $out;
}

/** «ست دول», «دولتين» … for the testimonials intro. */
function mkn_countries_phrase( $n ) {
	$words = array( 1 => 'دولة واحدة', 2 => 'دولتين', 3 => 'ثلاث دول', 4 => 'أربع دول', 5 => 'خمس دول', 6 => 'ست دول', 7 => 'سبع دول', 8 => 'ثماني دول', 9 => 'تسع دول', 10 => 'عشر دول' );
	return isset( $words[ $n ] ) ? $words[ $n ] : $n . ' دولة';
}

/** Country jump links on the testimonials page (only countries that have testimonials). */
function mkn_testimonial_jump() {
	$out = '';
	foreach ( mkn_testimonial_countries() as $c ) {
		$out .= '<a href="#' . esc_attr( $c[0] ) . '"><span class="label">' . esc_html( $c[2] ) . '</span>' . esc_html( $c[1] ) . '</a>';
	}
	return $out;
}

/** Owner-entered multi-line text: allowed inline tags, line breaks kept. */
function mkn_text( $v ) {
	return nl2br( wp_kses( $v, mkn_inline_kses() ), false );
}

/** Slugs of published case studies. */
function mkn_case_slugs() {
	return array_flip( wp_list_pluck( mkn_items( 'mkn_case' ), 'post_name' ) );
}

function mkn_is_english( $text ) {
	return ! preg_match( '/\p{Arabic}/u', wp_strip_all_tags( $text ) );
}

function mkn_country_name( $code ) {
	$c = mkn_country_options();
	return isset( $c[ $code ] ) ? $c[ $code ] : '';
}

function mkn_tavatar( $t ) {
	$client = (int) mkn_meta( $t->ID, 'logo' );
	$img    = $client && 'publish' === get_post_status( $client ) ? mkn_image( $client ) : null;
	if ( $img ) {
		$tone = mkn_meta( $client, 'tone' );
		$cls  = 'dark' === $tone ? ' tlogo--dark' : '';
		$cls .= 'fill' === mkn_meta( $client, 'fit' ) ? ' tlogo--fill' : '';
		$bg   = 'custom' === $tone && mkn_meta( $client, 'bg' ) ? ' style="background:' . esc_attr( mkn_meta( $client, 'bg' ) ) . '"' : '';
		$clip = mkn_meta( $client, 'clip' ) ? ' style="clip-path:' . esc_attr( mkn_meta( $client, 'clip' ) ) . '"' : '';
		return '<span class="tlogo' . $cls . '"' . $bg . '><img src="' . esc_url( $img[0] ) . '" alt="" loading="lazy" width="' . $img[1] . '" height="' . $img[2] . '"' . $clip . '></span>';
	}
	$letter = function_exists( 'mb_substr' ) ? mb_substr( trim( html_entity_decode( $t->post_title, ENT_QUOTES, 'UTF-8' ) ), 0, 1 ) : substr( trim( $t->post_title ), 0, 1 );
	return '<span class="tlogo tlogo--mono" aria-hidden="true">' . esc_html( $letter ) . '</span>';
}

function mkn_tcard( $t, $extra = '' ) {
	$text  = mkn_meta( $t->ID, 'text' );
	$en    = mkn_is_english( $text );
	$ltr   = $en ? ' dir="ltr"' : '';
	$place = mkn_meta( $t->ID, 'place' );
	$place = '' !== $place ? $place : mkn_country_name( mkn_meta( $t->ID, 'country' ) );
	$case  = mkn_meta( $t->ID, 'case' );
	$case  = isset( mkn_case_slugs()[ $case ] ) ? $case : '';
	$link  = $case ? '<a href="' . esc_url( mkn_url( 'work' ) . '#' . $case ) . '" class="tlink">دراسة الحالة</a>' : '';
	$tag   = $en ? '<span class="tlang">بالإنجليزية</span>' : '';
	return '<figure class="cell tcard reveal' . esc_attr( $extra ) . '"><span class="tmark" aria-hidden="true">”</span><blockquote' . $ltr . '>' . mkn_text( $text ) . '</blockquote><figcaption>' . mkn_tavatar( $t ) . '<span class="tby"><b>' . esc_html( $t->post_title ) . '</b><span>' . esc_html( $place ) . '</span></span>' . $tag . $link . '</figcaption></figure>';
}

function mkn_testimonial_groups() {
	$out = '';
	foreach ( (array) mkn_site( 'countries' ) as $c ) {
		list( $code, $cname, $en ) = $c;
		$items = array_values( array_filter( mkn_items( 'mkn_testimonial' ), function ( $t ) use ( $code ) {
			return mkn_meta( $t->ID, 'country' ) === $code;
		} ) );
		$n = count( $items );
		if ( ! $n ) {
			continue;
		}
		$feat  = 0 === ( $n + 1 ) % 3 && $n > 3; // one wide card keeps the last row full
		$cards = '';
		foreach ( $items as $i => $t ) {
			$extra  = ( $feat && 0 === $i ) ? ' tcard--feature' : '';
			$extra .= ( $n > 4 && $i >= 3 ) ? ' tcard--more' : '';
			$cards .= mkn_tcard( $t, $extra );
		}
		$more = $n > 4 ? '<button type="button" class="btn btn--ghost btn--sm tmore" data-more>عرض كل آراء ' . esc_html( $cname ) . ' (' . $n . ')</button>' : '';
		$out .= '<div class="tgroup" id="' . esc_attr( $code ) . '">
  <div class="heading" style="margin-bottom:22px"><span class="label">' . esc_html( $en ) . ' · ' . $n . '</span><h2>' . esc_html( $cname ) . '</h2></div>
  <div class="grid g3">' . $cards . '</div>' . $more . '
</div>';
		if ( 'sa' === $code ) {
			$out .= (string) mkn_site( 'testi_mid_cta' );
		}
	}
	return $out;
}

/* ---------- case studies ---------- */

function mkn_feature_cases() {
	$out = '';
	foreach ( mkn_featured( 'mkn_case' ) as $i => $c ) {
		$img = mkn_image( $c->ID );
		$alt = $img ? get_post_meta( $img[3], '_wp_attachment_image_alt', true ) : '';
		$out .= '<a href="' . esc_url( mkn_url( 'work' ) . '#' . $c->post_name ) . '" class="fcase reveal">'
			. ( $img ? '<img src="' . esc_url( $img[0] ) . '"' . mkn_srcset( $img[3], '(max-width: 640px) 80vw, 400px' ) . ' alt="' . esc_attr( $alt ? $alt : $c->post_title ) . '" loading="lazy" width="' . $img[1] . '" height="' . $img[2] . '">' : '' )
			. '<div class="glass"><span class="label">CASE ' . sprintf( '%02d', $i + 1 ) . '</span><h3>' . esc_html( $c->post_title ) . '</h3><p>' . esc_html( mkn_meta( $c->ID, 'teaser' ) ) . '</p></div></a>' . "\n";
	}
	return $out;
}

function mkn_case_index() {
	$out = '';
	foreach ( mkn_items( 'mkn_case' ) as $i => $c ) {
		$name = mkn_meta( $c->ID, 'index_name' );
		$sub  = mkn_meta( $c->ID, 'index_sub' );
		$out .= '<a href="' . esc_url( mkn_url( 'work' ) . '#' . $c->post_name ) . '"><span class="n">' . sprintf( '%02d', $i + 1 ) . '</span><strong>' . esc_html( '' !== $name ? $name : $c->post_title ) . '</strong><span class="s">' . esc_html( '' !== $sub ? $sub : mkn_meta( $c->ID, 'sub' ) ) . '</span></a>';
	}
	return $out;
}

function mkn_case_quote( $slug ) {
	foreach ( mkn_items( 'mkn_testimonial' ) as $t ) {
		if ( mkn_meta( $t->ID, 'case' ) === $slug ) {
			$text  = mkn_meta( $t->ID, 'text' );
			$ltr   = mkn_is_english( $text ) ? ' dir="ltr"' : '';
			$place = mkn_meta( $t->ID, 'place' );
			return '<figure class="tquote"><blockquote' . $ltr . '>' . mkn_text( $text ) . '</blockquote><figcaption><b>' . esc_html( $t->post_title ) . '</b>' . ( '' !== $place ? '<span>' . esc_html( $place ) . '</span>' : '' ) . '</figcaption></figure>';
		}
	}
	return '';
}

function mkn_full_case( $c, $idx ) {
	$k     = mkn_inline_kses();
	$name  = esc_html( $c->post_title );
	$img   = mkn_image( $c->ID );
	$tile  = mkn_meta( $c->ID, 'tile' );
	$wide  = '1' === mkn_meta( $c->ID, 'wide' );
	$media = '';
	if ( $img && $tile ) { // logo shown on its brand colour until a real application image exists
		$media = '<div class="case__img case__img--tile" style="background:' . esc_attr( $tile ) . '"><img src="' . esc_url( $img[0] ) . '" alt="' . esc_attr( $c->post_title ) . '" loading="lazy"></div>';
	} elseif ( $img ) {
		$media = '<div class="case__img' . ( $wide ? ' case__img--wide' : '' ) . '"><img src="' . esc_url( $img[0] ) . '"' . mkn_srcset( $img[3], $wide ? '(max-width: 640px) 92vw, 480px' : '(max-width: 640px) 92vw, 360px' ) . ' alt="' . esc_attr( $c->post_title ) . '" loading="lazy"></div>';
	}
	$depts = array();
	foreach ( (array) mkn_site( 'depts' ) as $d ) {
		$depts[ $d['key'] ] = $d['short'];
	}
	$rel = array();
	foreach ( array_filter( explode( ',', (string) mkn_meta( $c->ID, 'depts' ) ) ) as $key ) {
		if ( isset( $depts[ $key ] ) ) {
			$rel[] = '<a href="' . esc_url( mkn_url( 'services' ) . '#' . $key ) . '">' . esc_html( $depts[ $key ] ) . '</a>';
		}
	}
	$bundles = (array) mkn_site( 'bundles' );
	$bundle  = mkn_meta( $c->ID, 'bundle' );
	if ( $bundle && isset( $bundles[ $bundle ] ) ) {
		$rel[] = '<a href="' . esc_url( mkn_url( 'pricing' ) . '#' . $bundle ) . '">الحل المتكامل: ' . esc_html( $bundles[ $bundle ] ) . '</a>';
	}
	$wa      = 'مرحباً MKN ARABIA، شاهدت حالة ' . $c->post_title . ' وأرغب بمناقشة مشروع مشابه لنشاطي';
	$nxt     = '<div class="case__next">
      ' . ( $rel ? '<p><b>خدمات مرتبطة:</b> ' . implode( ' · ', $rel ) . '</p>' : '' ) . '
      <div class="hero__actions"><a href="#" data-wa="' . esc_attr( $wa ) . '" class="btn btn--dark btn--sm">ناقش مشروعًا مشابهًا</a><a ' . mkn_book_attrs() . ' class="btn btn--ghost btn--sm">احجز استشارة مجانية</a></div>
    </div>';
	$reading = mkn_meta( $c->ID, 'reading' );
	$rows    = '';
	foreach ( array( 'challenge' => 'التحدي', 'role' => 'دورنا', 'done' => 'ما نفذناه', 'outputs' => 'المخرجات' ) as $key => $label ) {
		$v = mkn_meta( $c->ID, $key );
		if ( '' !== $v ) {
			$rows .= '
      <div><dt>' . $label . '</dt><dd>' . mkn_text( $v ) . '</dd></div>';
		}
	}
	return '<article class="case glass glass--light reveal' . ( $wide ? ' case--wide' : '' ) . '" id="' . esc_attr( $c->post_name ) . '"' . ( '' === $media ? ' style="grid-template-columns:1fr"' : '' ) . '>
  ' . $media . '
  <div>
    <span class="label">SELECTED WORK · CASE ' . sprintf( '%02d', $idx ) . '</span>
    <h2>' . $name . '</h2>
    <p class="sub">' . esc_html( mkn_meta( $c->ID, 'sub' ) ) . '</p>
    <dl>' . $rows . '
    </dl>
    ' . ( '' !== $reading ? '<p class="reading">' . mkn_text( $reading ) . '</p>' : '' ) . '
    ' . mkn_case_quote( $c->post_name ) . '
    ' . $nxt . '
  </div>
</article>';
}

function mkn_cases_full() {
	$out = '';
	foreach ( mkn_items( 'mkn_case' ) as $i => $c ) {
		$out .= mkn_full_case( $c, $i + 1 );
		if ( 4 === $i ) {
			$out .= (string) mkn_site( 'case_mid_cta' );
		}
	}
	return $out;
}

/* ---------- articles ---------- */

function mkn_read_minutes( $post ) {
	$text  = preg_replace( '/<h[1-6]\b.*?<\/h[1-6]>/s', ' ', strip_shortcodes( $post->post_content ) ); // headings are skimmed, not read
	$words = count( preg_split( '/\s+/u', trim( wp_strip_all_tags( $text ) ), -1, PREG_SPLIT_NO_EMPTY ) );
	$n     = max( 1, (int) round( $words / 200, 0, PHP_ROUND_HALF_EVEN ) );
	if ( 1 === $n ) {
		return 'دقيقة واحدة';
	}
	if ( 2 === $n ) {
		return 'دقيقتان';
	}
	return $n <= 10 ? $n . ' دقائق' : $n . ' دقيقة';
}

function mkn_post_desc( $post ) {
	if ( '' !== $post->post_password ) {
		return '';
	}
	return has_excerpt( $post ) ? $post->post_excerpt : wp_trim_words( wp_strip_all_tags( strip_shortcodes( $post->post_content ) ), 30, '…' );
}

function mkn_post_topic( $post ) {
	$t = mkn_meta( $post->ID, 'topic' );
	if ( '' === $t ) {
		$cats = get_the_category( $post->ID );
		$t    = ( $cats && (int) $cats[0]->term_id !== (int) get_option( 'default_category' ) ) ? $cats[0]->name : 'INSIGHTS';
	}
	return $t;
}

function mkn_insight_cards( $posts ) {
	$out = '';
	foreach ( $posts as $p ) {
		$out .= '<a href="' . esc_url( get_permalink( $p ) ) . '" class="cell spot reveal icard"><span class="label" aria-hidden="true">' . esc_html( mkn_post_topic( $p ) ) . '</span><span class="go" aria-hidden="true">←</span><h3>' . esc_html( $p->post_title ) . '</h3><p>' . esc_html( mkn_post_desc( $p ) ) . '</p><span class="more">اقرأ المقال · ' . esc_html( mkn_read_minutes( $p ) ) . '</span></a>';
	}
	return $out;
}

/** All articles on the articles page (main query, with pages when there are many). */
function mkn_insights_all() {
	global $wp_query;
	$posts = ( is_home() && $wp_query ) ? $wp_query->posts : get_posts( array( 'posts_per_page' => 12, 'post_status' => 'publish' ) );
	$out   = mkn_insight_cards( $posts );
	if ( is_home() && $wp_query && $wp_query->max_num_pages > 1 ) {
		$links = paginate_links( array( 'total' => $wp_query->max_num_pages, 'current' => max( 1, get_query_var( 'paged' ) ), 'prev_text' => 'الأحدث', 'next_text' => 'الأقدم', 'type' => 'plain' ) );
		$out  .= '</div><nav class="pager" aria-label="صفحات المقالات" style="display:flex;gap:10px;justify-content:center;margin-top:32px">' . $links . '</nav><div>';
	}
	return $out;
}

/* ---------- FAQ ---------- */

function mkn_faq() {
	$out = '';
	foreach ( mkn_items( 'mkn_faq' ) as $i => $f ) {
		$out .= '<details' . ( 0 === $i ? ' open' : '' ) . '><summary><span class="label">Q' . sprintf( '%02d', $i + 1 ) . '</span>' . esc_html( $f->post_title ) . '</summary><p>' . mkn_text( mkn_meta( $f->ID, 'answer' ) ) . '</p></details>';
	}
	return $out;
}

/* ---------- shared page parts ---------- */

/** The inner-page hero (page_hero in the generator). */
function mkn_page_hero( $label, $h1, $p, $extra = '', $chip = true ) {
	$tail = $chip ? '<span class="chip"><span class="dot"></span>سوّق بالعربي، سوّق صح</span>' : '';
	return '<section class="page-hero grain">
  ' . mkn_site( 'grid_lines_b' ) . '
  <div class="container">
    <span class="label">' . esc_html( $label ) . '</span>
    <h1>' . esc_html( $h1 ) . '</h1>
    ' . ( '' !== $p ? '<p>' . esc_html( $p ) . '</p>' : '' ) . '
    ' . $extra . $tail . '
  </div>
</section>';
}

function mkn_cta() {
	return mkn_fill_placeholders( (string) mkn_site( 'cta' ) );
}

/*
 * Typography fixes on visible text only (never attributes or scripts), as in the generator:
 * keep «MKN ARABIA» on one line, attach «و» to a following Latin word, and announce English-only
 * labels with an English voice.
 */
function mkn_polish( $html ) {
	$parts = preg_split( '/(<script\b.*?<\/script>|<style\b.*?<\/style>|<textarea\b.*?<\/textarea>|<[^>]+>)/s', $html, -1, PREG_SPLIT_DELIM_CAPTURE );
	if ( ! is_array( $parts ) ) {
		return $html;
	}
	for ( $i = 0, $n = count( $parts ); $i < $n; $i += 2 ) {
		$t = str_replace( 'MKN ARABIA', 'MKN&nbsp;ARABIA', $parts[ $i ] );
		$t = preg_replace( '/ و (?=[A-Za-z])/u', ' و', $t );
		$parts[ $i ] = $t;
	}
	$html = implode( '', $parts );
	return preg_replace_callback( '/<span class="(label[^"]*)">([^<]*)<\/span>/u', function ( $m ) {
		$en = ! preg_match( '/[\x{0600}-\x{06FF}]/u', $m[2] );
		return '<span class="' . $m[1] . '"' . ( $en ? ' lang="en"' : '' ) . '>' . $m[2] . '</span>';
	}, $html );
}
