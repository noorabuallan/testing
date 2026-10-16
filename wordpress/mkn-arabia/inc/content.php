<?php
defined( 'ABSPATH' ) || exit;

/*
 * Editable content: testimonials, case studies, client logos, FAQ and website leads.
 * Each item is a post of its own type; its details are kept in post meta named _mkn_<field>.
 * Ordering everywhere follows the «الترتيب» (menu order) field, then the publish date.
 */

add_action( 'init', function () {
	$common = array(
		'public'              => false,
		'show_ui'             => true,
		'show_in_rest'        => false,
		'exclude_from_search' => true,
		'publicly_queryable'  => false,
		'has_archive'         => false,
		'rewrite'             => false,
		'query_var'           => false,
		'capability_type'     => 'post',
		'map_meta_cap'        => true,
	);
	register_post_type( 'mkn_testimonial', $common + array(
		'labels'        => mkn_cpt_labels( 'آراء العملاء', 'رأي عميل', 'اسم العلامة التجارية' ),
		'menu_icon'     => 'dashicons-format-quote',
		'menu_position' => 21,
		'supports'      => array( 'title', 'page-attributes' ),
	) );
	register_post_type( 'mkn_case', $common + array(
		'labels'        => mkn_cpt_labels( 'دراسات الحالة', 'دراسة حالة', 'اسم العميل أو المشروع' ),
		'menu_icon'     => 'dashicons-portfolio',
		'menu_position' => 22,
		'supports'      => array( 'title', 'thumbnail', 'page-attributes' ),
	) );
	register_post_type( 'mkn_client', $common + array(
		'labels'        => mkn_cpt_labels( 'شعارات العملاء', 'شعار عميل', 'اسم العلامة (يُقرأ لقارئ الشاشة)' ),
		'menu_icon'     => 'dashicons-awards',
		'menu_position' => 23,
		'supports'      => array( 'title', 'thumbnail', 'page-attributes' ),
	) );
	register_post_type( 'mkn_faq', $common + array(
		'labels'        => mkn_cpt_labels( 'الأسئلة الشائعة', 'سؤال', 'السؤال' ),
		'menu_icon'     => 'dashicons-editor-help',
		'menu_position' => 24,
		'supports'      => array( 'title', 'page-attributes' ),
	) );
	register_post_type( 'mkn_lead', $common + array(
		'labels'        => mkn_cpt_labels( 'طلبات التواصل', 'طلب', 'الاسم' ),
		'menu_icon'     => 'dashicons-email-alt',
		'menu_position' => 25,
		'supports'      => false,
		'capabilities'  => array( 'create_posts' => 'do_not_allow' ),
	) );
} );

function mkn_cpt_labels( $plural, $single, $title_ph ) {
	return array(
		'name'               => $plural,
		'singular_name'      => $single,
		'menu_name'          => $plural,
		'add_new'            => 'إضافة ' . $single,
		'add_new_item'       => 'إضافة ' . $single,
		'edit_item'          => 'تعديل ' . $single,
		'new_item'           => $single . ' جديد',
		'view_item'          => 'عرض ' . $single,
		'search_items'       => 'بحث في ' . $plural,
		'not_found'          => 'لا يوجد شيء بعد.',
		'not_found_in_trash' => 'سلة المهملات فارغة.',
		'all_items'          => 'الكل',
		'featured_image'     => 'الصورة',
		'set_featured_image' => 'اختيار الصورة',
		'remove_featured_image' => 'إزالة الصورة',
		'use_featured_image' => 'استخدام كصورة',
		'mkn_title_ph'       => $title_ph,
	);
}

add_filter( 'enter_title_here', function ( $text, $post ) {
	$obj = get_post_type_object( $post->post_type );
	return ( $obj && isset( $obj->labels->mkn_title_ph ) ) ? $obj->labels->mkn_title_ph : $text;
}, 10, 2 );

/* ---------- field definitions ---------- */

function mkn_country_options() {
	$o = array();
	foreach ( (array) mkn_site( 'countries' ) as $c ) {
		$o[ $c[0] ] = $c[1];
	}
	return $o;
}

function mkn_case_options() {
	$o = array( '' => '— بدون —' );
	foreach ( mkn_items( 'mkn_case' ) as $p ) {
		$o[ $p->post_name ] = $p->post_title;
	}
	return $o;
}

function mkn_client_options() {
	$o = array( '' => 'بدون شعار (يظهر الحرف الأول من الاسم)' );
	foreach ( mkn_items( 'mkn_client' ) as $p ) {
		$o[ (string) $p->ID ] = $p->post_title;
	}
	return $o;
}

function mkn_dept_options() {
	$o = array();
	foreach ( (array) mkn_site( 'depts' ) as $d ) {
		$o[ $d['key'] ] = $d['code'] . ' · ' . $d['short'];
	}
	return $o;
}

function mkn_bundle_options() {
	$o = array( '' => '— بدون —' );
	foreach ( (array) mkn_site( 'bundles' ) as $k => $t ) {
		$o[ $k ] = strtoupper( $k ) . ' · ' . $t;
	}
	return $o;
}

/** Field schema per post type: key => [label, type, options|null, help]. */
function mkn_fields( $type ) {
	switch ( $type ) {
		case 'mkn_testimonial':
			return array(
				'text'     => array( 'نص الرأي', 'textarea', null, 'كما وافق عليه العميل. يظهر بالإنجليزية تلقائيًا من اليسار إن لم يحتوِ على حروف عربية.' ),
				'place'    => array( 'المدينة', 'text', null, 'اتركه فارغًا لإظهار اسم الدولة.' ),
				'country'  => array( 'الدولة', 'select', 'mkn_country_options', 'تحدد مجموعة الرأي في صفحة آراء العملاء.' ),
				'logo'     => array( 'شعار العميل', 'select', 'mkn_client_options', 'من قائمة «شعارات العملاء».' ),
				'case'     => array( 'دراسة الحالة المرتبطة', 'select', 'mkn_case_options', 'يظهر رابط «دراسة الحالة»، ويظهر الرأي داخل الحالة في صفحة أعمالنا.' ),
				'featured' => array( 'يظهر في الصفحة الرئيسية', 'checkbox', null, '' ),
			);
		case 'mkn_case':
			return array(
				'sub'        => array( 'سطر التعريف', 'text', null, 'القطاع · الدولة · الفترة. مثال: الجمال والعافية · شراكة مستمرة منذ نوفمبر 2023' ),
				'challenge'  => array( 'التحدي', 'textarea', null, '' ),
				'role'       => array( 'دورنا', 'textarea', null, '' ),
				'done'       => array( 'ما نفذناه', 'textarea', null, '' ),
				'outputs'    => array( 'المخرجات', 'textarea', null, '' ),
				'reading'    => array( 'ملاحظة النتائج (اختياري)', 'textarea', null, 'مثال: «طبيعة النتائج: …». لا تُنشر أرقام إيرادات.' ),
				'depts'      => array( 'الخدمات المرتبطة', 'checkboxes', 'mkn_dept_options', '' ),
				'bundle'     => array( 'الحل المتكامل المرتبط', 'select', 'mkn_bundle_options', '' ),
				'index_name' => array( 'الاسم المختصر في فهرس الحالات', 'text', null, 'اتركه فارغًا لاستخدام العنوان.' ),
				'index_sub'  => array( 'السطر المختصر في فهرس الحالات', 'text', null, 'اتركه فارغًا لاستخدام سطر التعريف.' ),
				'featured'   => array( 'تظهر في «أعمال مختارة» بالصفحة الرئيسية', 'checkbox', null, 'يُفضّل 3 حالات بصور عمودية.' ),
				'teaser'     => array( 'جملة البطاقة في الرئيسية', 'text', null, '' ),
				'tile'       => array( 'لون خلفية الشعار', 'color', null, 'للحالات التي صورتها شعار بدل صورة عمل: يظهر الشعار على هذا اللون. اتركه فارغًا لصورة عمل عادية.' ),
				'wide'       => array( 'صورة أفقية عريضة', 'checkbox', null, 'للصور الأفقية (لقطات شاشة أو تصورات معمارية).' ),
			);
		case 'mkn_client':
			return array(
				'tone' => array( 'خلفية البطاقة', 'select', array( 'light' => 'فاتحة', 'dark' => 'داكنة', 'custom' => 'لون مخصص' ), 'اختر ما يُظهر الشعار بوضوح.' ),
				'bg'   => array( 'اللون المخصص', 'color', null, 'عند اختيار «لون مخصص».' ),
				'fit'  => array( 'ملء البطاقة', 'select', array( '' => 'لا — الشعار داخل هامش', 'fill' => 'نعم — الصورة تملأ البطاقة' ), '' ),
				'clip' => array( 'قص العرض (متقدم)', 'text', null, 'قيمة CSS clip-path لإخفاء حواف الصورة عند العرض فقط، مثل circle(64% at 50% 50%). لا يغيّر الملف.' ),
			);
		case 'mkn_faq':
			return array(
				'answer' => array( 'الإجابة', 'textarea', null, '' ),
			);
		case 'post':
			return array(
				'topic'     => array( 'تصنيف قصير يظهر على البطاقة', 'text', null, 'بالإنجليزية وبأحرف كبيرة، مثل MEASUREMENT أو LOCAL DISCOVERY.' ),
				'cta'       => array( 'جملة الدعوة في نهاية المقال', 'text', null, 'مثال: احجز جلسة استراتيجية لمناقشة أولويات نمو نشاطك.' ),
				'related'   => array( 'روابط «اقرأ أيضًا»', 'lines', null, 'سطر لكل رابط بالشكل: النص | الرابط — مثل: مجال الإعلانات المدفوعة | /services/#d04' ),
			);
	}
	return array();
}

/** Read one field. */
function mkn_meta( $post_id, $key ) {
	$v = get_post_meta( $post_id, '_mkn_' . $key, true );
	return is_array( $v ) ? $v : (string) $v;
}

/** Published items of a type in display order (cached per request). */
function mkn_items( $type, $extra = array() ) {
	static $cache = array();
	$k = $type . md5( wp_json_encode( $extra ) );
	if ( ! isset( $cache[ $k ] ) ) {
		$cache[ $k ] = get_posts( array_merge( array(
			'post_type'        => $type,
			'post_status'      => 'publish',
			'posts_per_page'   => 200,
			'orderby'          => array( 'menu_order' => 'ASC', 'date' => 'ASC' ),
			'suppress_filters' => false,
			'no_found_rows'    => true,
		), $extra ) );
	}
	return $cache[ $k ];
}

/* ---------- meta boxes ---------- */

add_action( 'add_meta_boxes', function ( $post_type ) {
	$titles = array(
		'mkn_testimonial' => 'تفاصيل الرأي',
		'mkn_case'        => 'تفاصيل دراسة الحالة',
		'mkn_client'      => 'طريقة عرض الشعار',
		'mkn_faq'         => 'الإجابة',
		'post'            => 'إعدادات المقال في تصميم الموقع',
	);
	if ( isset( $titles[ $post_type ] ) ) {
		add_meta_box( 'mkn_fields', $titles[ $post_type ], 'mkn_fields_box', $post_type, 'normal', 'high' );
	}
	if ( 'mkn_case' === $post_type ) {
		add_meta_box( 'postimagediv', 'صورة الحالة', 'post_thumbnail_meta_box', $post_type, 'side', 'default' );
	}
	if ( 'mkn_client' === $post_type ) {
		add_meta_box( 'postimagediv', 'ملف الشعار (WebP أو PNG)', 'post_thumbnail_meta_box', $post_type, 'side', 'high' );
	}
	if ( 'mkn_lead' === $post_type ) {
		add_meta_box( 'mkn_lead_box', 'تفاصيل الطلب', 'mkn_lead_box', $post_type, 'normal', 'high' );
	}
} );

function mkn_fields_box( $post ) {
	wp_nonce_field( 'mkn_save_fields', 'mkn_fields_nonce' );
	echo '<table class="form-table mkn-fields" role="presentation">';
	foreach ( mkn_fields( $post->post_type ) as $key => $f ) {
		list( $label, $type, $opts, $help ) = $f;
		$name = 'mkn[' . $key . ']';
		$id   = 'mkn-' . $key;
		$val  = mkn_meta( $post->ID, $key );
		if ( is_string( $opts ) && is_callable( $opts ) ) {
			$opts = call_user_func( $opts );
		}
		echo '<tr><th scope="row"><label for="' . esc_attr( $id ) . '">' . esc_html( $label ) . '</label></th><td>';
		switch ( $type ) {
			case 'textarea':
				echo '<textarea name="' . esc_attr( $name ) . '" id="' . esc_attr( $id ) . '" rows="4" class="large-text">' . esc_textarea( $val ) . '</textarea>';
				break;
			case 'lines':
				echo '<textarea name="' . esc_attr( $name ) . '" id="' . esc_attr( $id ) . '" rows="4" class="large-text">' . esc_textarea( $val ) . '</textarea>';
				break;
			case 'select':
				echo '<select name="' . esc_attr( $name ) . '" id="' . esc_attr( $id ) . '">';
				foreach ( (array) $opts as $k => $t ) {
					echo '<option value="' . esc_attr( $k ) . '"' . selected( (string) $val, (string) $k, false ) . '>' . esc_html( $t ) . '</option>';
				}
				echo '</select>';
				break;
			case 'checkbox':
				echo '<label><input type="checkbox" name="' . esc_attr( $name ) . '" id="' . esc_attr( $id ) . '" value="1"' . checked( '1', $val, false ) . '> نعم</label>';
				break;
			case 'checkboxes':
				$val = is_array( $val ) ? $val : array_filter( explode( ',', (string) $val ) );
				echo '<fieldset id="' . esc_attr( $id ) . '">';
				foreach ( (array) $opts as $k => $t ) {
					echo '<label style="display:block;margin:2px 0"><input type="checkbox" name="' . esc_attr( $name ) . '[]" value="' . esc_attr( $k ) . '"' . checked( in_array( (string) $k, $val, true ), true, false ) . '> ' . esc_html( $t ) . '</label>';
				}
				echo '</fieldset>';
				break;
			case 'color':
				echo '<input type="text" name="' . esc_attr( $name ) . '" id="' . esc_attr( $id ) . '" value="' . esc_attr( $val ) . '" class="mkn-color" dir="ltr" placeholder="#000000">';
				break;
			default:
				echo '<input type="text" name="' . esc_attr( $name ) . '" id="' . esc_attr( $id ) . '" value="' . esc_attr( $val ) . '" class="large-text">';
		}
		if ( $help ) {
			echo '<p class="description">' . esc_html( $help ) . '</p>';
		}
		echo '</td></tr>';
	}
	echo '</table>';
}

/** Tags allowed inside multi-line text fields (quotes, case text, FAQ answers). */
function mkn_inline_kses() {
	return array(
		'a'      => array( 'href' => true, 'target' => true, 'rel' => true ),
		'b'      => array(),
		'strong' => array(),
		'em'     => array(),
		'br'     => array(),
		'span'   => array( 'class' => true, 'dir' => true, 'lang' => true ),
	);
}

add_action( 'save_post', function ( $post_id, $post ) {
	if ( ! isset( $_POST['mkn_fields_nonce'] ) || ! wp_verify_nonce( sanitize_key( wp_unslash( $_POST['mkn_fields_nonce'] ) ), 'mkn_save_fields' ) ) {
		return;
	}
	if ( ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) || wp_is_post_revision( $post_id ) || ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}
	$in = isset( $_POST['mkn'] ) && is_array( $_POST['mkn'] ) ? wp_unslash( $_POST['mkn'] ) : array(); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput -- sanitized per field below
	foreach ( mkn_fields( $post->post_type ) as $key => $f ) {
		list( , $type, $opts ) = $f;
		if ( is_string( $opts ) && is_callable( $opts ) ) {
			$opts = call_user_func( $opts );
		}
		$raw = isset( $in[ $key ] ) ? $in[ $key ] : '';
		switch ( $type ) {
			case 'textarea':
				$v = trim( wp_kses( (string) $raw, mkn_inline_kses() ) );
				break;
			case 'lines':
				$v = trim( sanitize_textarea_field( (string) $raw ) );
				break;
			case 'select':
				$v = array_key_exists( (string) $raw, (array) $opts ) ? (string) $raw : '';
				break;
			case 'checkbox':
				$v = '1' === (string) $raw ? '1' : '';
				break;
			case 'checkboxes':
				$v = implode( ',', array_values( array_intersect( array_map( 'strval', (array) $raw ), array_map( 'strval', array_keys( (array) $opts ) ) ) ) );
				break;
			case 'color':
				$v = (string) sanitize_hex_color( trim( (string) $raw ) );
				break;
			default:
				$v = sanitize_text_field( (string) $raw );
				if ( 'clip' === $key ) {
					$v = preg_match( '/^(circle|ellipse|inset|polygon)\([0-9a-z%.,\s-]*\)$/i', $v ) ? $v : '';
				}
		}
		update_post_meta( $post_id, '_mkn_' . $key, $v );
	}
	mkn_flush_page_cache();
}, 10, 2 );

/* Clear page caches whenever site content changes. */
foreach ( array( 'mkn_testimonial', 'mkn_case', 'mkn_client', 'mkn_faq' ) as $mkn_type ) {
	add_action( 'save_post_' . $mkn_type, 'mkn_flush_page_cache' );
}
add_action( 'trashed_post', 'mkn_flush_page_cache' );
add_action( 'untrashed_post', 'mkn_flush_page_cache' );

/** Purge the LiteSpeed (Hostinger) page cache, when present. */
function mkn_flush_page_cache() {
	static $done = false;
	if ( $done ) {
		return;
	}
	$done = true;
	do_action( 'litespeed_purge_all' );
	if ( function_exists( 'wp_cache_flush' ) ) {
		wp_cache_flush();
	}
}

/* ---------- list screens ---------- */

add_filter( 'manage_mkn_testimonial_posts_columns', function ( $c ) {
	return array( 'cb' => $c['cb'], 'title' => 'العلامة', 'mkn_country' => 'الدولة', 'mkn_featured' => 'في الرئيسية', 'mkn_order' => 'الترتيب' );
} );
add_filter( 'manage_mkn_case_posts_columns', function ( $c ) {
	return array( 'cb' => $c['cb'], 'mkn_thumb' => 'الصورة', 'title' => 'الحالة', 'mkn_sub' => 'سطر التعريف', 'mkn_featured' => 'في الرئيسية', 'mkn_order' => 'الترتيب' );
} );
add_filter( 'manage_mkn_client_posts_columns', function ( $c ) {
	return array( 'cb' => $c['cb'], 'mkn_thumb' => 'الشعار', 'title' => 'العلامة', 'mkn_order' => 'الترتيب' );
} );
add_filter( 'manage_mkn_faq_posts_columns', function ( $c ) {
	return array( 'cb' => $c['cb'], 'title' => 'السؤال', 'mkn_order' => 'الترتيب' );
} );
add_filter( 'manage_mkn_lead_posts_columns', function ( $c ) {
	return array( 'cb' => $c['cb'], 'mkn_name' => 'الاسم', 'mkn_phone' => 'الهاتف', 'mkn_service' => 'الخدمة', 'mkn_country' => 'الدولة', 'mkn_ref' => 'المصدر', 'date' => 'التاريخ' );
} );

foreach ( array( 'mkn_testimonial', 'mkn_case', 'mkn_client', 'mkn_faq', 'mkn_lead' ) as $mkn_type ) {
	add_action( 'manage_' . $mkn_type . '_posts_custom_column', 'mkn_list_column', 10, 2 );
}

function mkn_list_column( $col, $post_id ) {
	switch ( $col ) {
		case 'mkn_country':
			$c = mkn_country_options();
			$k = mkn_meta( $post_id, 'country' );
			echo esc_html( isset( $c[ $k ] ) ? $c[ $k ] : $k );
			break;
		case 'mkn_featured':
			echo mkn_meta( $post_id, 'featured' ) ? '✓' : '—';
			break;
		case 'mkn_order':
			echo (int) get_post_field( 'menu_order', $post_id );
			break;
		case 'mkn_sub':
			echo esc_html( mkn_meta( $post_id, 'sub' ) );
			break;
		case 'mkn_thumb':
			$bg = 'mkn_client' === get_post_type( $post_id ) ? mkn_client_bg( $post_id ) : mkn_meta( $post_id, 'tile' );
			echo '<span style="display:inline-block;background:' . esc_attr( $bg ? $bg : '#f3f3f3' ) . ';padding:4px;border-radius:4px">' . get_the_post_thumbnail( $post_id, array( 80, 80 ), array( 'style' => 'max-width:80px;height:auto;display:block' ) ) . '</span>';
			break;
		case 'mkn_name':
			$new = '' === mkn_meta( $post_id, 'seen' ) ? ' <span class="awaiting-mod" style="margin-inline-start:4px">جديد</span>' : '';
			echo '<a href="' . esc_url( get_edit_post_link( $post_id ) ) . '"><b>' . esc_html( mkn_meta( $post_id, 'name' ) ) . '</b></a>' . $new; // phpcs:ignore WordPress.Security.EscapeOutput -- static markup
			break;
		case 'mkn_phone':
			echo '<span dir="ltr">' . esc_html( mkn_meta( $post_id, 'phone' ) ) . '</span>';
			break;
		case 'mkn_service':
		case 'mkn_ref':
			echo esc_html( mkn_meta( $post_id, substr( $col, 4 ) ) );
			break;
	}
}

/** Card background for a client logo tile in the admin list. */
function mkn_client_bg( $post_id ) {
	$tone = mkn_meta( $post_id, 'tone' );
	if ( 'custom' === $tone ) {
		return mkn_meta( $post_id, 'bg' );
	}
	return 'dark' === $tone ? '#0d1114' : '#ffffff';
}

/* Sort the list screens by the display order. */
add_action( 'pre_get_posts', function ( $q ) {
	if ( ! is_admin() || ! $q->is_main_query() ) {
		return;
	}
	$type = $q->get( 'post_type' );
	if ( in_array( $type, array( 'mkn_testimonial', 'mkn_case', 'mkn_client', 'mkn_faq' ), true ) && ! $q->get( 'orderby' ) ) {
		$q->set( 'orderby', array( 'menu_order' => 'ASC', 'date' => 'ASC' ) );
	}
} );

/* ---------- leads ---------- */

function mkn_lead_fields() {
	return array(
		'name'    => 'الاسم',
		'company' => 'الشركة',
		'phone'   => 'الهاتف',
		'email'   => 'البريد',
		'country' => 'الدولة',
		'service' => 'الخدمة المطلوبة',
		'timing'  => 'الموعد المتوقع',
		'budget'  => 'الميزانية',
		'message' => 'الهدف والأصول المتاحة',
		'ref'     => 'رمز المصدر',
		'landing' => 'صفحة الدخول',
		'mailed'  => 'وصلت نسخة على البريد',
	);
}

function mkn_lead_box( $post ) {
	echo '<table class="widefat striped" role="presentation"><tbody>';
	foreach ( mkn_lead_fields() as $k => $label ) {
		$v = mkn_meta( $post->ID, $k );
		if ( 'mailed' === $k ) {
			$v = '1' === $v ? 'نعم' : 'لا — راجع إعدادات البريد في Hostinger';
		}
		$ltr = in_array( $k, array( 'phone', 'email', 'ref', 'landing' ), true ) ? ' dir="ltr" style="text-align:right"' : '';
		echo '<tr><th style="width:180px">' . esc_html( $label ) . '</th><td' . $ltr . '>' . nl2br( esc_html( '' !== $v ? $v : '—' ) ) . '</td></tr>';
	}
	echo '</tbody></table>';
	$phone = preg_replace( '/\D+/', '', mkn_meta( $post->ID, 'phone' ) );
	$email = mkn_meta( $post->ID, 'email' );
	echo '<p style="margin-top:14px">';
	if ( $phone ) {
		echo '<a class="button button-primary" target="_blank" rel="noopener" href="' . esc_url( 'https://wa.me/' . $phone ) . '">مراسلة على واتساب</a> ';
	}
	if ( $email ) {
		echo '<a class="button" href="' . esc_url( 'mailto:' . $email ) . '">رد بالبريد</a>';
	}
	echo '</p>';
}

/* Opening a lead marks it as seen. */
add_action( 'load-post.php', function () {
	$id = isset( $_GET['post'] ) ? absint( $_GET['post'] ) : 0; // phpcs:ignore WordPress.Security.NonceVerification -- read-only flag
	if ( $id && 'mkn_lead' === get_post_type( $id ) && current_user_can( 'edit_post', $id ) ) {
		update_post_meta( $id, '_mkn_seen', '1' );
	}
} );

/** Number of leads not opened yet. */
function mkn_new_leads() {
	$q = new WP_Query( array(
		'post_type'      => 'mkn_lead',
		'post_status'    => 'private',
		'posts_per_page' => 1,
		'fields'         => 'ids',
		'meta_query'     => array( array( 'key' => '_mkn_seen', 'compare' => 'NOT EXISTS' ) ),
	) );
	return (int) $q->found_posts;
}

add_action( 'admin_menu', function () {
	global $menu;
	$n = mkn_new_leads();
	if ( ! $n || ! is_array( $menu ) ) {
		return;
	}
	foreach ( $menu as $i => $m ) {
		if ( isset( $m[2] ) && 'edit.php?post_type=mkn_lead' === $m[2] ) {
			$menu[ $i ][0] .= ' <span class="awaiting-mod count-' . $n . '"><span class="pending-count">' . number_format_i18n( $n ) . '</span></span>'; // phpcs:ignore WordPress.WP.GlobalVariablesOverride -- menu badge
		}
	}
}, 99 );

/* Leads list: show private posts by default and offer a CSV export. */
add_action( 'restrict_manage_posts', function ( $type ) {
	if ( 'mkn_lead' === $type ) {
		$url = wp_nonce_url( admin_url( 'admin-post.php?action=mkn_leads_csv' ), 'mkn_leads_csv' );
		echo '<a class="button" href="' . esc_url( $url ) . '">تصدير CSV</a>';
	}
} );

add_action( 'admin_post_mkn_leads_csv', function () {
	if ( ! current_user_can( 'edit_posts' ) || ! check_admin_referer( 'mkn_leads_csv' ) ) {
		wp_die( 'غير مسموح.' );
	}
	$leads = get_posts( array( 'post_type' => 'mkn_lead', 'post_status' => 'private', 'posts_per_page' => -1, 'orderby' => 'date', 'order' => 'DESC' ) );
	nocache_headers();
	header( 'Content-Type: text/csv; charset=utf-8' );
	header( 'Content-Disposition: attachment; filename=mkn-leads-' . gmdate( 'Y-m-d' ) . '.csv' );
	$out    = fopen( 'php://output', 'w' );
	$fields = mkn_lead_fields();
	fwrite( $out, "\xEF\xBB\xBF" ); // Excel opens UTF-8 Arabic correctly with a BOM
	fputcsv( $out, array_merge( array( 'التاريخ' ), array_values( $fields ) ) );
	foreach ( $leads as $l ) {
		$row = array( get_date_from_gmt( $l->post_date_gmt, 'Y-m-d H:i' ) );
		foreach ( array_keys( $fields ) as $k ) {
			$v = mkn_meta( $l->ID, $k );
			// Spreadsheet formula injection guard.
			$row[] = preg_match( '/^[=+\-@\t\r]/', $v ) ? "'" . $v : $v;
		}
		fputcsv( $out, $row );
	}
	fclose( $out );
	exit;
} );
