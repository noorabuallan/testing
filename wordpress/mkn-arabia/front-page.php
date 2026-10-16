<?php
defined( 'ABSPATH' ) || exit;
get_header();
echo mkn_fragment( 'home' ); // phpcs:ignore WordPress.Security.EscapeOutput -- theme layout with escaped dynamic parts
get_footer();
