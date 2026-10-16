<?php
defined( 'ABSPATH' ) || exit;

/** Settings fields: key => [label, type, section, help]. */
function mkn_settings_fields() {
	return array(
		'whatsapp'              => array( 'رقم واتساب (للأزرار)', 'digits', 'contact', 'بالصيغة الدولية بدون + أو 00، مثل 201140552627.' ),
		'wa_display'            => array( 'رقم واتساب كما يظهر للزوار', 'text', 'contact', 'مثل +20 114 055 2627' ),
		'email'                 => array( 'البريد الظاهر في الموقع', 'email', 'contact', '' ),
		'lead_email'            => array( 'البريد الذي تصله طلبات النموذج', 'email', 'contact', 'تصلك نسخة من كل طلب، وتُحفظ الطلبات أيضًا في «طلبات التواصل».' ),
		'book'                  => array( 'رابط حجز الاستشارة', 'url', 'contact', 'رابط Google Calendar لصفحة الحجز.' ),
		'book_embed'            => array( 'رابط الحجز المضمَّن (صفحة تواصل)', 'url', 'contact', 'رابط التضمين من Google Calendar ‏(appointments/schedules…?gv=true).' ),
		'instagram'             => array( 'Instagram', 'url', 'social', '' ),
		'facebook'              => array( 'Facebook', 'url', 'social', '' ),
		'linkedin'              => array( 'LinkedIn (الشركة)', 'url', 'social', '' ),
		'linkedin_founder'      => array( 'LinkedIn (المؤسس)', 'url', 'social', '' ),
		'gtm_id'                => array( 'Google Tag Manager', 'id', 'tracking', 'مثل GTM-XXXXXXX. عند وضعه تُدار كل الوسوم من GTM.' ),
		'ga4_id'                => array( 'Google Analytics 4', 'id', 'tracking', 'مثل G-XXXXXXXXXX (يُستخدم فقط إذا كان GTM فارغًا).' ),
		'google_ads_id'         => array( 'Google Ads', 'id', 'tracking', 'مثل AW-123456789' ),
		'google_ads_lead_label' => array( 'Google Ads — تسمية تحويل الطلب', 'id', 'tracking', '' ),
		'google_ads_wa_label'   => array( 'Google Ads — تسمية تحويل واتساب', 'id', 'tracking', '' ),
		'meta_pixel_id'         => array( 'Meta Pixel', 'id', 'tracking', 'أرقام فقط.' ),
		'tiktok_pixel_id'       => array( 'TikTok Pixel', 'id', 'tracking', '' ),
	);
}

function mkn_settings_defaults() {
	$d = array_fill_keys( array_keys( mkn_settings_fields() ), '' );
	foreach ( (array) mkn_seed( 'settings' ) as $k => $v ) {
		if ( array_key_exists( $k, $d ) ) {
			$d[ $k ] = (string) $v;
		}
	}
	return $d;
}

/** One site setting (saved value, or the shipped default when empty). */
function mkn_opt( $key ) {
	static $opts = null;
	if ( null === $opts ) {
		$saved = get_option( 'mkn_settings', array() );
		$opts  = mkn_settings_defaults();
		foreach ( is_array( $saved ) ? $saved : array() as $k => $v ) {
			if ( array_key_exists( $k, $opts ) && '' !== (string) $v ) {
				$opts[ $k ] = (string) $v;
			}
		}
		// Tracking IDs have no defaults, so an emptied field must stay empty.
		foreach ( mkn_settings_fields() as $k => $f ) {
			if ( 'id' === $f[1] ) {
				$opts[ $k ] = isset( $saved[ $k ] ) ? (string) $saved[ $k ] : '';
			}
		}
	}
	return isset( $opts[ $key ] ) ? $opts[ $key ] : '';
}

add_action( 'update_option_mkn_settings', function () {
	if ( function_exists( 'mkn_flush_page_cache' ) ) {
		mkn_flush_page_cache();
	}
} );

function mkn_sanitize_settings( $in ) {
	$out = array();
	$in  = is_array( $in ) ? $in : array();
	foreach ( mkn_settings_fields() as $k => $f ) {
		$v = isset( $in[ $k ] ) ? trim( (string) wp_unslash( $in[ $k ] ) ) : '';
		switch ( $f[1] ) {
			case 'digits':
				$v = preg_replace( '/\D+/', '', $v );
				break;
			case 'email':
				$v = sanitize_email( $v );
				break;
			case 'url':
				$v = esc_url_raw( $v, array( 'https', 'http' ) );
				break;
			case 'id':
				$v = preg_replace( '/[^A-Za-z0-9_\-\/]/', '', $v );
				break;
			default:
				$v = sanitize_text_field( $v );
		}
		$out[ $k ] = $v;
	}
	return $out;
}

add_action( 'admin_init', function () {
	register_setting( 'mkn_settings_group', 'mkn_settings', array(
		'type'              => 'array',
		'sanitize_callback' => 'mkn_sanitize_settings',
		'default'           => array(),
	) );
} );

add_action( 'admin_menu', function () {
	add_menu_page( 'إعدادات MKN', 'إعدادات MKN', 'manage_options', 'mkn-settings', 'mkn_settings_page', 'dashicons-admin-generic', 59 );
} );

function mkn_settings_page() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$saved    = get_option( 'mkn_settings', array() );
	$saved    = is_array( $saved ) ? $saved : array();
	$defaults = mkn_settings_defaults();
	$sections = array(
		'contact'  => array( 'التواصل والحجز', 'تظهر هذه البيانات في كل صفحات الموقع (الأزرار، التذييل، صفحة التواصل).' ),
		'social'   => array( 'الحسابات', '' ),
		'tracking' => array( 'أدوات القياس', 'اترك أي حقل فارغًا لتعطيله. التفاصيل في ملف TRACKING.md.' ),
	);
	?>
	<div class="wrap">
		<h1>إعدادات MKN</h1>
		<?php settings_errors(); ?>
		<form method="post" action="options.php">
			<?php settings_fields( 'mkn_settings_group' ); ?>
			<?php foreach ( $sections as $sid => $s ) : ?>
				<h2 class="title"><?php echo esc_html( $s[0] ); ?></h2>
				<?php if ( $s[1] ) : ?><p><?php echo esc_html( $s[1] ); ?></p><?php endif; ?>
				<table class="form-table" role="presentation">
				<?php
				foreach ( mkn_settings_fields() as $k => $f ) :
					if ( $f[2] !== $sid ) {
						continue;
					}
					$val  = isset( $saved[ $k ] ) && '' !== $saved[ $k ] ? $saved[ $k ] : ( 'id' === $f[1] ? '' : $defaults[ $k ] );
					$type = 'email' === $f[1] ? 'email' : ( 'url' === $f[1] ? 'url' : 'text' );
					$ltr  = 'text' !== $f[1] || 'wa_display' === $k;
					?>
					<tr>
						<th scope="row"><label for="mkn-<?php echo esc_attr( $k ); ?>"><?php echo esc_html( $f[0] ); ?></label></th>
						<td>
							<input name="mkn_settings[<?php echo esc_attr( $k ); ?>]" id="mkn-<?php echo esc_attr( $k ); ?>" type="<?php echo esc_attr( $type ); ?>" value="<?php echo esc_attr( $val ); ?>" class="regular-text<?php echo $ltr ? ' ltr' : ''; ?>"<?php echo $ltr ? ' dir="ltr"' : ''; ?>>
							<?php if ( $f[3] ) : ?><p class="description"><?php echo esc_html( $f[3] ); ?></p><?php endif; ?>
						</td>
					</tr>
				<?php endforeach; ?>
				</table>
			<?php endforeach; ?>
			<?php submit_button( 'حفظ الإعدادات' ); ?>
		</form>
	</div>
	<?php
}
