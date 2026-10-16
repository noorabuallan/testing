<?php
/**
 * Site header (same markup as the static site).
 */
defined( 'ABSPATH' ) || exit;
?><!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<?php ob_start(); ?>
<a class="skip-link" href="#main">تخطَّ إلى المحتوى الرئيسي</a>
<?php
$mkn_slug    = mkn_current_slug();
$mkn_section = '';
if ( 'testimonials' === $mkn_slug ) {
	$mkn_section = 'work';
} elseif ( is_singular( 'post' ) || is_archive() || is_search() ) {
	$mkn_section = 'insights';
}
$mkn_links = '';
foreach ( (array) mkn_site( 'nav' ) as $mkn_item ) {
	list( $mkn_s, $mkn_t ) = $mkn_item;
	$mkn_attr = '';
	if ( $mkn_s === $mkn_slug ) {
		$mkn_attr = ' class="active" aria-current="page"';
	} elseif ( $mkn_s === $mkn_section ) {
		$mkn_attr = ' class="active" aria-current="true"';
	}
	$mkn_links .= '<a href="' . esc_url( mkn_url( $mkn_s ) ) . '"' . $mkn_attr . '>' . esc_html( $mkn_t ) . '</a>';
	if ( 'work' === $mkn_s ) { // testimonials live under «أعمالنا»; listed separately in the mobile menu only
		$mkn_cur    = 'testimonials' === $mkn_slug;
		$mkn_links .= '<a href="' . esc_url( mkn_url( 'testimonials' ) ) . '" class="nav__m' . ( $mkn_cur ? ' active' : '' ) . '"' . ( $mkn_cur ? ' aria-current="page"' : '' ) . '>آراء العملاء</a>';
	}
}
?>
<header class="header">
  <div class="container"><div class="header__inner">
    <a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="logo" aria-label="MKN ARABIA — الرئيسية"><img src="<?php echo esc_url( mkn_asset( 'img/logo-white-sm.png' ) ); ?>" alt="MKN ARABIA" width="101" height="34"></a>
    <a <?php echo mkn_book_attrs(); // phpcs:ignore WordPress.Security.EscapeOutput -- escaped inside ?> class="btn btn--blue btn--sm header__book">احجز<span class="hb-x"> استشارة</span></a>
    <button type="button" class="nav-toggle" aria-label="فتح القائمة" aria-expanded="false" aria-controls="site-nav"><span></span><span></span><span></span></button>
    <nav class="nav" id="site-nav" aria-label="القائمة الرئيسية">
      <?php echo $mkn_links; // phpcs:ignore WordPress.Security.EscapeOutput -- escaped above ?>
      <a <?php echo mkn_book_attrs(); // phpcs:ignore WordPress.Security.EscapeOutput ?> class="btn btn--blue btn--sm">احجز استشارة</a>
      <a href="#" data-wa class="btn btn--line btn--sm nav__wa">واتساب</a>
    </nav>
  </div></div>
</header>
<main id="main" tabindex="-1">
