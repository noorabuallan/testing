<?php
/* Fallback listing (category, tag, date and search results). */
defined( 'ABSPATH' ) || exit;
get_header();
if ( is_search() ) {
	$mkn_title = 'نتائج البحث: ' . get_search_query();
} elseif ( is_archive() ) {
	$mkn_title = wp_strip_all_tags( get_the_archive_title() );
} else {
	$mkn_title = 'المقالات';
}
echo mkn_page_hero( 'INSIGHTS', $mkn_title, '', '', false ); // phpcs:ignore WordPress.Security.EscapeOutput
?>
<section class="section section--aura">
  <div class="container">
    <?php if ( have_posts() ) : ?>
      <div class="grid g3"><?php echo mkn_insight_cards( $GLOBALS['wp_query']->posts ); // phpcs:ignore WordPress.Security.EscapeOutput ?></div>
      <nav class="pager" aria-label="الصفحات" style="display:flex;gap:10px;justify-content:center;margin-top:32px"><?php echo paginate_links( array( 'prev_text' => 'الأحدث', 'next_text' => 'الأقدم' ) ); // phpcs:ignore WordPress.Security.EscapeOutput ?></nav>
    <?php else : ?>
      <p>لا توجد نتائج. <a href="<?php echo esc_url( mkn_url( 'insights' ) ); ?>">تصفّح كل المقالات</a>.</p>
    <?php endif; ?>
  </div>
</section>
<?php
echo mkn_cta(); // phpcs:ignore WordPress.Security.EscapeOutput
get_footer();
