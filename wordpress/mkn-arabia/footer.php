<?php
/**
 * Site footer (same markup as the static site).
 */
defined( 'ABSPATH' ) || exit;

$mkn_depts = '';
foreach ( (array) mkn_site( 'depts' ) as $mkn_d ) {
	$mkn_href   = ! empty( $mkn_d['slug'] ) && get_page_by_path( 'services/' . $mkn_d['slug'], OBJECT, array( 'page' ) ) ? mkn_url( 'services/' . $mkn_d['slug'] ) : mkn_url( 'services' ) . '#' . $mkn_d['key'];
	$mkn_depts .= '<li><a href="' . esc_url( $mkn_href ) . '"><span class="ltr">' . esc_html( $mkn_d['code'] ) . '</span> · ' . esc_html( $mkn_d['short'] ) . '</a></li>';
}
?>
</main>
<footer class="footer">
  <img class="footer__mark" src="<?php echo esc_url( mkn_asset( 'img/logo-white.png' ) ); ?>" alt="" width="620" height="210" loading="lazy">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        <a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="logo"><img src="<?php echo esc_url( mkn_asset( 'img/logo-white-sm.png' ) ); ?>" alt="MKN ARABIA" width="101" height="34"></a>
        <p>شريك استراتيجي لنمو الأعمال. نربط الاستراتيجية والإبداع والأداء والتقنية حول هدف تجاري واحد.</p>
        <p class="slogan">سوّق بالعربي، سوّق صح</p>
        <?php echo mkn_fill_placeholders( (string) mkn_site( 'badge' ) ); // phpcs:ignore WordPress.Security.EscapeOutput -- theme markup ?>
      </div>
      <div><details class="fdepts"><summary class="fh">الخدمات</summary><ul><?php echo $mkn_depts; // phpcs:ignore WordPress.Security.EscapeOutput ?></ul></details></div>
      <div>
        <h2 class="fh">استكشف</h2>
        <ul>
          <li><a href="<?php echo esc_url( mkn_url( 'pricing' ) ); ?>">الباقات وعرض السعر</a></li>
          <li><a href="<?php echo esc_url( mkn_url( 'pricing' ) . '#bundles' ); ?>">الحلول المتكاملة</a></li>
          <li><a href="<?php echo esc_url( mkn_url( 'work' ) ); ?>">أعمالنا</a></li>
          <li><a href="<?php echo esc_url( mkn_url( 'testimonials' ) ); ?>">آراء العملاء</a></li>
          <li><a href="<?php echo esc_url( mkn_url( 'insights' ) ); ?>">المقالات</a></li>
          <?php if ( get_page_by_path( 'markets', OBJECT, array( 'page' ) ) ) : ?><li><a href="<?php echo esc_url( mkn_url( 'markets' ) ); ?>">الأسواق: الخليج</a></li><?php endif; ?>
        </ul>
      </div>
      <div>
        <h2 class="fh">الشركة</h2>
        <ul>
          <li><a href="<?php echo esc_url( mkn_url( 'about' ) ); ?>">من نحن</a></li>
          <li><a href="<?php echo esc_url( mkn_url( 'about' ) . '#method' ); ?>">منهجية العمل</a></li>
          <li><a href="<?php echo esc_url( mkn_url( 'contact' ) ); ?>">تواصل</a></li>
          <li><a href="<?php echo esc_url( mkn_url( 'privacy' ) ); ?>">سياسة الخصوصية</a></li>
        </ul>
      </div>
      <div>
        <h2 class="fh">تواصل</h2>
        <ul>
          <li><a <?php echo mkn_book_attrs(); // phpcs:ignore WordPress.Security.EscapeOutput ?>>احجز استشارة مجانية</a></li>
          <li><a href="#" data-wa>واتساب · <span class="ltr"><?php echo esc_html( mkn_wa_display() ); ?></span></a></li>
          <li><a data-email href="<?php echo esc_url( 'mailto:' . mkn_opt( 'email' ) ); ?>"><?php echo esc_html( mkn_opt( 'email' ) ); ?></a></li>
          <?php if ( mkn_opt( 'instagram' ) ) : ?><li><a href="<?php echo esc_url( mkn_opt( 'instagram' ) ); ?>" target="_blank" rel="noopener">Instagram<?php if ( mkn_social_handle( mkn_opt( 'instagram' ) ) ) : ?> · <span class="ltr"><?php echo esc_html( mkn_social_handle( mkn_opt( 'instagram' ) ) ); ?></span><?php endif; ?></a></li><?php endif; ?>
          <?php if ( mkn_opt( 'facebook' ) ) : ?><li><a href="<?php echo esc_url( mkn_opt( 'facebook' ) ); ?>" target="_blank" rel="noopener">Facebook<?php if ( mkn_social_handle( mkn_opt( 'facebook' ) ) ) : ?> · <span class="ltr"><?php echo esc_html( mkn_social_handle( mkn_opt( 'facebook' ) ) ); ?></span><?php endif; ?></a></li><?php endif; ?>
          <?php if ( mkn_opt( 'linkedin' ) ) : ?><li><a href="<?php echo esc_url( mkn_opt( 'linkedin' ) ); ?>" target="_blank" rel="noopener">LinkedIn · MKN ARABIA</a></li><?php endif; ?>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© <span data-year><?php echo esc_html( wp_date( 'Y' ) ); ?></span> MKN ARABIA · الأردن. جميع الحقوق محفوظة.</span>
      <span class="label">STRATEGY · CREATIVE · PERFORMANCE · TECHNOLOGY</span>
    </div>
  </div>
</footer>
<aside aria-label="تواصل سريع"><a class="wa-float" data-wa href="#" aria-label="تواصل عبر واتساب"><?php echo mkn_site( 'wa_svg' ); // phpcs:ignore WordPress.Security.EscapeOutput -- static svg ?></a></aside>
<?php echo mkn_polish( (string) ob_get_clean() ); // phpcs:ignore WordPress.Security.EscapeOutput -- page markup assembled from escaped parts ?>
<?php wp_footer(); ?>
</body>
</html>
