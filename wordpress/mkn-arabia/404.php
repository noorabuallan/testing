<?php
defined( 'ABSPATH' ) || exit;
get_header();
echo mkn_fragment( '404' ); // phpcs:ignore WordPress.Security.EscapeOutput -- theme layout
get_footer();
