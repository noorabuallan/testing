<?php
defined( 'ABSPATH' ) || exit;

/* «المقالات» instead of «Posts» everywhere in the dashboard. */
add_filter( 'post_type_labels_post', function ( $l ) {
	$l->name          = 'المقالات';
	$l->singular_name = 'مقال';
	$l->menu_name     = 'المقالات';
	$l->name_admin_bar = 'مقال';
	$l->add_new       = 'إضافة مقال';
	$l->add_new_item  = 'إضافة مقال';
	$l->edit_item     = 'تعديل المقال';
	$l->all_items     = 'كل المقالات';
	return $l;
} );

/** Is this page drawn from a designed layout (so its editor content is not shown)? */
function mkn_is_designed_page( $post ) {
	$post = get_post( $post );
	return $post && 'page' === $post->post_type && in_array( $post->post_name, mkn_page_slugs(), true );
}

/* Designed pages open in the simple editor, with a note on where their content is edited. */
add_filter( 'use_block_editor_for_post', function ( $use, $post ) {
	return mkn_is_designed_page( $post ) ? false : $use;
}, 10, 2 );

add_action( 'edit_form_after_title', function ( $post ) {
	if ( ! mkn_is_designed_page( $post ) ) {
		return;
	}
	$where = array(
		'home'         => 'دراسات الحالة المختارة، آراء العملاء المختارة، شعارات العملاء، أحدث المقالات',
		'work'         => 'دراسات الحالة',
		'testimonials' => 'آراء العملاء وشعارات العملاء',
		'insights'     => 'المقالات',
		'contact'      => 'الأسئلة الشائعة، ورقم واتساب والبريد ورابط الحجز من «إعدادات MKN»',
		'pricing'      => 'آراء العملاء وشعارات العملاء',
		'services'     => 'شعارات العملاء وآراء العملاء',
		'about'        => 'شعارات العملاء',
	);
	echo '<div class="notice notice-info inline" style="margin:16px 0"><p><b>تصميم هذه الصفحة جزء من قالب MKN.</b> ';
	if ( isset( $where[ $post->post_name ] ) ) {
		echo 'الأجزاء المتغيرة فيها تُعدَّل من: ' . esc_html( $where[ $post->post_name ] ) . '. ';
	}
	echo 'عنوانها ووصفها في Google من صندوق «الظهور في Google» أدناه. لا تغيّر الرابط المختصر (slug) لهذه الصفحة.</p></div>';
	echo '<style>#postdivrich{display:none}</style>';
} );

/* ---------- dashboard: one place with everything the owner edits ---------- */
remove_action( 'welcome_panel', 'wp_welcome_panel' );
add_action( 'wp_dashboard_setup', function () {
	wp_add_dashboard_widget( 'mkn_dashboard', 'MKN ARABIA — إدارة الموقع', 'mkn_dashboard_widget' );
	// Show it first.
	global $wp_meta_boxes;
	$normal = isset( $wp_meta_boxes['dashboard']['normal']['core'] ) ? $wp_meta_boxes['dashboard']['normal']['core'] : array();
	if ( isset( $normal['mkn_dashboard'] ) ) {
		$wp_meta_boxes['dashboard']['normal']['core'] = array( 'mkn_dashboard' => $normal['mkn_dashboard'] ) + $normal; // phpcs:ignore WordPress.WP.GlobalVariablesOverride
	}
	remove_meta_box( 'dashboard_primary', 'dashboard', 'side' );
	remove_meta_box( 'dashboard_quick_press', 'dashboard', 'side' );
} );

function mkn_dashboard_widget() {
	$count = function ( $type, $status = 'publish' ) {
		$c = wp_count_posts( $type );
		return isset( $c->$status ) ? (int) $c->$status : 0;
	};
	$new   = mkn_new_leads();
	$rows  = array(
		array( 'طلبات التواصل', admin_url( 'edit.php?post_type=mkn_lead' ), $count( 'mkn_lead', 'private' ) . ( $new ? ' · ' . $new . ' جديد' : '' ), '' ),
		array( 'المقالات', admin_url( 'edit.php' ), $count( 'post' ), admin_url( 'post-new.php' ) ),
		array( 'دراسات الحالة', admin_url( 'edit.php?post_type=mkn_case' ), $count( 'mkn_case' ), admin_url( 'post-new.php?post_type=mkn_case' ) ),
		array( 'آراء العملاء', admin_url( 'edit.php?post_type=mkn_testimonial' ), $count( 'mkn_testimonial' ), admin_url( 'post-new.php?post_type=mkn_testimonial' ) ),
		array( 'شعارات العملاء', admin_url( 'edit.php?post_type=mkn_client' ), $count( 'mkn_client' ), admin_url( 'post-new.php?post_type=mkn_client' ) ),
		array( 'الأسئلة الشائعة', admin_url( 'edit.php?post_type=mkn_faq' ), $count( 'mkn_faq' ), admin_url( 'post-new.php?post_type=mkn_faq' ) ),
	);
	echo '<table class="widefat striped"><tbody>';
	foreach ( $rows as $r ) {
		echo '<tr><td><a href="' . esc_url( $r[1] ) . '"><b>' . esc_html( $r[0] ) . '</b></a></td><td>' . esc_html( (string) $r[2] ) . '</td><td style="text-align:left">' . ( $r[3] ? '<a class="button button-small" href="' . esc_url( $r[3] ) . '">إضافة</a>' : '' ) . '</td></tr>';
	}
	echo '</tbody></table>';
	echo '<p style="margin-top:12px"><a class="button button-primary" href="' . esc_url( admin_url( 'admin.php?page=mkn-settings' ) ) . '">إعدادات MKN (واتساب، البريد، الحجز، القياس)</a> <a class="button" href="' . esc_url( home_url( '/' ) ) . '" target="_blank" rel="noopener">عرض الموقع</a></p>';
	echo '<p class="description">الترتيب في كل قائمة يتبع حقل «الترتيب» داخل العنصر (الأصغر أولًا). أي تعديل يظهر في الموقع فورًا.</p>';
}

/* ---------- re-run the import (adds anything missing, never overwrites) ---------- */
add_action( 'admin_menu', function () {
	add_submenu_page( 'mkn-settings', 'إعدادات MKN', 'الإعدادات', 'manage_options', 'mkn-settings', 'mkn_settings_page' );
	add_submenu_page( 'mkn-settings', 'استيراد المحتوى', 'استيراد المحتوى', 'manage_options', 'mkn-import', 'mkn_import_page' );
}, 20 );

function mkn_import_page() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$ran = false;
	if ( isset( $_POST['mkn_import'] ) && check_admin_referer( 'mkn_import' ) ) {
		mkn_import_run( true );
		$ran = true;
	}
	$done = (int) get_option( 'mkn_seed_done' );
	$log  = (array) get_option( 'mkn_seed_log', array() );
	echo '<div class="wrap"><h1>استيراد المحتوى</h1>';
	if ( $ran ) {
		echo '<div class="notice notice-success"><p>تم. أُضيف كل عنصر ناقص من محتوى الموقع الأصلي.</p></div>';
	}
	echo '<p>يضيف المقالات وآراء العملاء ودراسات الحالة وشعارات العملاء والأسئلة الشائعة والصفحات كما كانت في الموقع الأصلي، إن لم تكن موجودة. لا يعدّل ولا يكرر أي عنصر موجود.</p>';
	echo '<p>آخر تشغيل: ' . ( $done ? esc_html( wp_date( 'Y-m-d H:i', $done ) ) : 'لم يتم بعد' ) . '</p>';
	if ( $log ) {
		echo '<ul style="list-style:disc;padding-inline-start:20px">';
		foreach ( $log as $l ) {
			echo '<li>' . esc_html( $l ) . '</li>';
		}
		echo '</ul>';
	}
	echo '<form method="post">';
	wp_nonce_field( 'mkn_import' );
	submit_button( 'إضافة المحتوى الناقص', 'secondary', 'mkn_import' );
	echo '</form></div>';
}

/* Small admin touches: left-to-right inputs for links and IDs, colour swatches. */
add_action( 'admin_head', function () {
	echo '<style>.mkn-fields th{width:220px}.mkn-color{width:120px}input.ltr{direction:ltr;text-align:left}</style>';
} );

add_action( 'admin_enqueue_scripts', function ( $hook ) {
	$screen = get_current_screen();
	if ( in_array( $hook, array( 'post.php', 'post-new.php' ), true ) && $screen && in_array( $screen->post_type, array( 'mkn_case', 'mkn_client' ), true ) ) {
		wp_enqueue_style( 'wp-color-picker' );
		wp_enqueue_script( 'wp-color-picker' );
		wp_add_inline_script( 'wp-color-picker', 'jQuery(function($){$(".mkn-color").wpColorPicker();});' );
	}
} );
