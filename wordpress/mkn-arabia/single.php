<?php
/* An article (same layout as the static site's insights/*.html). */
defined( 'ABSPATH' ) || exit;
get_header();
while ( have_posts() ) :
	the_post();
	$mkn_post = get_post();
	$mkn_byline = '<p class="byline"><span>فريق MKN ARABIA</span> · <span>قراءة ' . esc_html( mkn_read_minutes( $mkn_post ) ) . '</span></p>';
	echo mkn_page_hero( 'INSIGHTS · ' . mkn_post_topic( $mkn_post ), get_the_title(), mkn_post_desc( $mkn_post ), $mkn_byline, false ); // phpcs:ignore WordPress.Security.EscapeOutput

	$mkn_related = array();
	foreach ( preg_split( '/\R/u', (string) mkn_meta( $mkn_post->ID, 'related' ) ) as $mkn_line ) {
		$mkn_bits = array_map( 'trim', explode( '|', $mkn_line ) );
		if ( 2 === count( $mkn_bits ) && '' !== $mkn_bits[0] && '' !== $mkn_bits[1] ) {
			$mkn_href      = 0 === strpos( $mkn_bits[1], '/' ) ? home_url( $mkn_bits[1] ) : $mkn_bits[1];
			$mkn_related[] = '<a href="' . esc_url( $mkn_href ) . '">' . esc_html( $mkn_bits[0] ) . '</a>';
		}
	}
	$mkn_cta    = mkn_meta( $mkn_post->ID, 'cta' );
	$mkn_others = get_posts( array( 'posts_per_page' => 2, 'post__not_in' => array( $mkn_post->ID ), 'post_status' => 'publish', 'ignore_sticky_posts' => true ) );
	?>
<section class="section section--aura">
  <div class="container">
    <article class="prose glass glass--light reveal">
      <?php the_content(); ?>
      <?php if ( $mkn_related ) : ?><div class="related"><b>اقرأ أيضًا في خدماتنا وأعمالنا:</b> <?php echo implode( ' · ', $mkn_related ); // phpcs:ignore WordPress.Security.EscapeOutput -- escaped above ?></div><?php endif; ?>
      <div class="prose-cta">
        <p><?php echo esc_html( '' !== $mkn_cta ? $mkn_cta : 'احجز استشارة مجانية لمناقشة أولويات نمو نشاطك.' ); ?></p>
        <div class="hero__actions">
          <a <?php echo mkn_book_attrs(); // phpcs:ignore WordPress.Security.EscapeOutput ?> class="btn btn--dark">احجز استشارة مجانية</a>
          <a href="#" data-wa="<?php echo esc_attr( 'مرحباً MKN ARABIA، قرأت مقال: ' . get_the_title() ); ?>" class="btn btn--ghost">تحدث معنا عبر واتساب</a>
        </div>
      </div>
    </article>
    <?php if ( $mkn_others ) : ?>
    <div class="heading" style="margin:56px 0 24px"><span class="label">READ NEXT</span><h2>مقالات أخرى.</h2></div>
    <div class="grid g2"><?php echo mkn_insight_cards( $mkn_others ); // phpcs:ignore WordPress.Security.EscapeOutput ?></div>
    <?php endif; ?>
  </div>
</section>
	<?php
endwhile;
get_footer();
