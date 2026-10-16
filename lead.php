<?php
/* MKN ARABIA — email copy of every website brief (the visitor is also sent to WhatsApp).
   Hostinger: the mailbox below must exist (hPanel → Emails). Nothing is stored on the server. */
declare(strict_types=1);

$TO   = 'contact@mknarabia.com';   // where briefs arrive
$FROM = 'contact@mknarabia.com';   // must be a mailbox on mknarabia.com for delivery

header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex, nofollow');
header('Cache-Control: no-store');

function out(int $code, bool $ok): void { http_response_code($code); echo json_encode(['ok' => $ok]); exit; }

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') out(405, false);

// accept browser requests from this site only
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin !== '' && !preg_match('#^https://(www\.)?mknarabia\.com$|^https?://(localhost|127\.0\.0\.1)(:\d+)?$#', $origin)) out(403, false);

// spam trap: real visitors never fill the hidden "website" field
if (!empty($_POST['website'])) out(200, true);

// at most 5 briefs per 10 minutes from one address
$ip   = $_SERVER['REMOTE_ADDR'] ?? '0';
$file = sys_get_temp_dir() . '/mkn_lead_' . md5($ip);
$hits = json_decode((string) @file_get_contents($file), true);
$hits = array_values(array_filter(is_array($hits) ? $hits : [], fn($t) => is_int($t) && $t > time() - 600));
if (count($hits) >= 5) out(429, false);
$hits[] = time();
@file_put_contents($file, json_encode($hits), LOCK_EX);

function field(string $k, int $max = 300): string {
    $v = trim(str_replace(["\r", "\0"], '', (string) ($_POST[$k] ?? '')));
    return function_exists('mb_substr') ? mb_substr($v, 0, $max) : substr($v, 0, $max);
}
$name  = field('name', 120);
$phone = field('phone', 40);
if ($name === '' || $phone === '') out(422, false);
$email = field('email', 160);
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) $email = '';

$lines = [
    'طلب جديد من موقع MKN ARABIA',
    '',
    'الاسم: ' . $name,
    'الشركة: ' . (field('company', 160) ?: '-'),
    'الهاتف: ' . $phone,
    'البريد: ' . ($email ?: '-'),
    'الدولة: ' . field('country', 80),
    'الخدمة المطلوبة: ' . field('service', 120),
    'الموعد المتوقع: ' . (field('timing', 80) ?: '-'),
    'الميزانية: ' . (field('budget', 80) ?: '-'),
    'الهدف والأصول المتاحة: ' . (field('message', 3000) ?: '-'),
    '',
    '— رمز المصدر: ' . (field('ref', 200) ?: 'زيارة مباشرة'),
    '— صفحة الدخول: ' . (field('landing', 200) ?: '-'),
    '— وقت الإرسال: ' . gmdate('Y-m-d H:i') . ' UTC',
];
$subject = '=?UTF-8?B?' . base64_encode('طلب جديد من الموقع — ' . $name) . '?=';
$headers = [
    'From: MKN ARABIA Website <' . $FROM . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
];
if ($email !== '') $headers[] = 'Reply-To: ' . $email;

$sent = @mail($TO, $subject, implode("\n", $lines), implode("\r\n", $headers), '-f' . $FROM);
out($sent ? 200 : 500, $sent);
