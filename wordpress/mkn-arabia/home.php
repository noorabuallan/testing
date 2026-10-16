<?php
/* The articles page («المقالات»). */
defined( 'ABSPATH' ) || exit;
get_header();
echo mkn_fragment( 'insights' ); // phpcs:ignore WordPress.Security.EscapeOutput -- theme layout with escaped dynamic parts
get_footer();
