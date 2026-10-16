<?php
defined( 'ABSPATH' ) || exit;

/*
 * Contact form briefs: POST /wp-json/mkn/v1/lead
 * Each brief is saved in «طلبات التواصل» and a copy is emailed to the lead address from «إعدادات MKN».
 * The visitor is also sent to WhatsApp by the page script, so a failure here never loses the brief.
 */

add_action( 'rest_api_init', function () {
	register_rest_route( 'mkn/v1', '/lead', array(
		'methods'             => 'POST',
		'callback'            => 'mkn_lead_submit',
		'permission_callback' => '__return_true', // public form; protected by origin check, honeypot and rate limit
	) );
} );

function mkn_lead_reply( $code, $ok ) {
	$res = new WP_REST_Response( array( 'ok' => (bool) $ok ), $code );
	$res->header( 'Cache-Control', 'no-store' );
	$res->header( 'X-Robots-Tag', 'noindex, nofollow' );
	return $res;
}

function mkn_lead_field( WP_REST_Request $req, $key, $max = 300 ) {
	$v = $req->get_param( $key );
	$v = is_scalar( $v ) ? trim( str_replace( array( "\r", "\0" ), '', (string) $v ) ) : '';
	$v = 'message' === $key ? sanitize_textarea_field( $v ) : sanitize_text_field( $v );
	return function_exists( 'mb_substr' ) ? mb_substr( $v, 0, $max ) : substr( $v, 0, $max );
}

function mkn_lead_submit( WP_REST_Request $req ) {
	// Browser requests from this site only.
	$origin = (string) $req->get_header( 'origin' );
	if ( '' !== $origin ) {
		$host = wp_parse_url( home_url(), PHP_URL_HOST );
		$oh   = wp_parse_url( $origin, PHP_URL_HOST );
		$ok   = $oh && ( strtolower( $oh ) === strtolower( $host ) || strtolower( $oh ) === 'www.' . strtolower( $host ) || 'www.' . strtolower( $oh ) === strtolower( $host ) );
		if ( ! $ok ) {
			return mkn_lead_reply( 403, false );
		}
	}
	// Spam trap: real visitors never fill the hidden "website" field.
	if ( '' !== (string) $req->get_param( 'website' ) ) {
		return mkn_lead_reply( 200, true );
	}
	// At most 5 briefs per 10 minutes from one address.
	$ip   = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : '0';
	$key  = 'mkn_lead_' . md5( $ip );
	$hits = get_transient( $key );
	$hits = array_values( array_filter( is_array( $hits ) ? $hits : array(), function ( $t ) {
		return is_int( $t ) && $t > time() - 600;
	} ) );
	if ( count( $hits ) >= 5 ) {
		return mkn_lead_reply( 429, false );
	}
	$hits[] = time();
	set_transient( $key, $hits, 600 );

	$d = array();
	foreach ( array( 'name' => 120, 'company' => 160, 'phone' => 40, 'email' => 160, 'country' => 80, 'service' => 120, 'timing' => 80, 'budget' => 80, 'message' => 3000, 'ref' => 200, 'landing' => 200 ) as $k => $max ) {
		$d[ $k ] = mkn_lead_field( $req, $k, $max );
	}
	$d['phone'] = mkn_ascii_digits( $d['phone'] );
	if ( '' === $d['name'] || '' === $d['phone'] ) {
		return mkn_lead_reply( 422, false );
	}
	$d['email'] = is_email( $d['email'] ) ? $d['email'] : '';

	$labels = mkn_lead_fields();
	$lines  = array( 'طلب جديد من موقع MKN ARABIA', '' );
	foreach ( array( 'name', 'company', 'phone', 'email', 'country', 'service', 'timing', 'budget', 'message' ) as $k ) {
		$lines[] = $labels[ $k ] . ': ' . ( '' !== $d[ $k ] ? $d[ $k ] : '-' );
	}
	$lines[] = '';
	$lines[] = '— رمز المصدر: ' . ( '' !== $d['ref'] ? $d['ref'] : 'زيارة مباشرة' );
	$lines[] = '— صفحة الدخول: ' . ( '' !== $d['landing'] ? $d['landing'] : '-' );
	$lines[] = '— وقت الإرسال: ' . wp_date( 'Y-m-d H:i' );

	$post_id = wp_insert_post( array(
		'post_type'    => 'mkn_lead',
		'post_status'  => 'private',
		'post_title'   => $d['name'] . ( '' !== $d['service'] ? ' — ' . $d['service'] : '' ),
		'post_content' => implode( "\n", $lines ),
	), true );
	if ( ! is_wp_error( $post_id ) ) {
		foreach ( $d as $k => $v ) {
			update_post_meta( $post_id, '_mkn_' . $k, $v );
		}
	}

	$to      = mkn_opt( 'lead_email' ) ? mkn_opt( 'lead_email' ) : mkn_opt( 'email' );
	$headers = array( 'Content-Type: text/plain; charset=UTF-8' );
	$from    = mkn_opt( 'email' );
	$domain  = strtolower( (string) wp_parse_url( home_url(), PHP_URL_HOST ) );
	if ( $from && preg_match( '/@(?:www\.)?' . preg_quote( preg_replace( '/^www\./', '', $domain ), '/' ) . '$/i', $from ) ) {
		$headers[] = 'From: MKN ARABIA Website <' . $from . '>'; // a mailbox on the site's own domain delivers reliably
	}
	if ( $d['email'] ) {
		$headers[] = 'Reply-To: ' . $d['email'];
	}
	$sent = $to ? wp_mail( $to, 'طلب جديد من الموقع — ' . $d['name'], implode( "\n", $lines ), $headers ) : false;
	if ( ! is_wp_error( $post_id ) ) {
		update_post_meta( $post_id, '_mkn_mailed', $sent ? '1' : '' );
	}
	$saved = ! is_wp_error( $post_id );
	return mkn_lead_reply( $saved || $sent ? 200 : 500, $saved || $sent );
}
