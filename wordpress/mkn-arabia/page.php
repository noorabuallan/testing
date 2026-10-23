<?php
/* Designed pages use their layout from fragments/; any other page uses a simple article layout. */
defined( 'ABSPATH' ) || exit;
get_header();
$mkn_slug = mkn_current_slug();
if ( $mkn_slug ) {
	echo mkn_fragment( $mkn_slug ); // phpcs:ignore WordPress.Security.EscapeOutput -- theme layout with escaped dynamic parts
} else {
	while ( have_posts() ) :
		the_post();
		echo mkn_page_hero( 'MKN ARABIA', get_the_title(), has_excerpt() ? get_the_excerpt() : '' ); // phpcs:ignore WordPress.Security.EscapeOutput
		?>
<section class="section section--aura">
  <div class="container">
    <article class="prose glass glass--light reveal">
      <?php the_content(); ?>
    </article>
  </div>
</section>
		<?php
		echo mkn_cta(); // phpcs:ignore WordPress.Security.EscapeOutput
	endwhile;
}
get_footer();
