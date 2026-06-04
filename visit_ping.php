<?php
declare(strict_types=1);

require_once __DIR__ . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'load_dotenv.php';
require_once __DIR__ . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'telegram_notify.php';

header('Cache-Control: no-store');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit;
}

function visit_ping_client_ip(): string
{
    if (!empty($_SERVER['HTTP_CF_CONNECTING_IP'])) {
        return trim((string) $_SERVER['HTTP_CF_CONNECTING_IP']);
    }
    return trim((string) ($_SERVER['REMOTE_ADDR'] ?? ''));
}

function visit_ping_is_private_ip(string $ip): bool
{
    if ($ip === '' || $ip === '::1') {
        return true;
    }
    if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
        return !filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE);
    }
    if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) {
        return !filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE);
    }
    return true;
}

function visit_ping_likely_bot(string $ua): bool
{
    $l = strtolower($ua);
    $needles = [
        'googlebot',
        'bingbot',
        'slurp',
        'duckduckbot',
        'baiduspider',
        'yandexbot',
        'facebookexternalhit',
        'twitterbot',
        'linkedinbot',
        'embedly',
        'applebot',
        'petalbot',
        'semrush',
        'ahrefs',
        'mj12bot',
        'dotbot',
        'headless',
    ];
    foreach ($needles as $n) {
        if ($n !== '' && str_contains($l, $n)) {
            return true;
        }
    }
    return false;
}

/**
 * @return array{country: string, region: string, city: string}
 */
function visit_ping_geo_lookup(string $ip): array
{
    $empty = ['country' => '', 'region' => '', 'city' => ''];
    if ($ip === '' || visit_ping_is_private_ip($ip)) {
        return $empty;
    }

    $url = 'https://ipwho.is/' . rawurlencode($ip);
    $json = visit_ping_http_get($url, 3);
    if ($json === null) {
        return $empty;
    }
    $data = json_decode($json, true);
    if (!is_array($data) || empty($data['success'])) {
        return $empty;
    }

    return [
        'country' => trim((string) ($data['country'] ?? '')),
        'region' => trim((string) ($data['region'] ?? '')),
        'city' => trim((string) ($data['city'] ?? '')),
    ];
}

function visit_ping_http_get(string $url, int $timeoutSec): ?string
{
    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        if ($ch === false) {
            return null;
        }
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $timeoutSec,
            CURLOPT_HTTPHEADER => ['Accept: application/json'],
        ]);
        $raw = curl_exec($ch);
        $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($raw === false || $code !== 200) {
            return null;
        }
        return (string) $raw;
    }

    $ctx = stream_context_create(
        [
            'http' => [
                'method' => 'GET',
                'header' => "Accept: application/json\r\n",
                'timeout' => $timeoutSec,
            ],
        ]
    );
    $raw = @file_get_contents($url, false, $ctx);
    return $raw === false ? null : (string) $raw;
}

/**
 * @param array<string, int> $state
 * @return array<string, int>
 */
function visit_ping_rate_prune(array $state, int $now): array
{
    foreach ($state as $k => $t) {
        if ($now - $t > 86400) {
            unset($state[$k]);
        }
    }
    return $state;
}

/**
 * @return list<string>
 */
function visit_ping_env_csv_list(string $raw): array
{
    if ($raw === '') {
        return [];
    }
    $parts = explode(',', $raw);
    $out = [];
    foreach ($parts as $p) {
        $s = trim((string) $p);
        if ($s !== '') {
            $out[] = $s;
        }
    }
    return $out;
}

$env = load_dotenv(__DIR__);
$tgToken = trim((string) ($env['TELEGRAM_BOT_TOKEN'] ?? ''));
$tgChat = trim((string) ($env['TELEGRAM_CHAT_ID'] ?? ''));

http_response_code(204);

if ($tgToken === '' || $tgChat === '') {
    exit;
}

$ua = (string) ($_SERVER['HTTP_USER_AGENT'] ?? '');
if (visit_ping_likely_bot($ua)) {
    exit;
}

$ip = visit_ping_client_ip();

$ignoreIps = visit_ping_env_csv_list(trim((string) ($env['VISIT_PING_IGNORE_IPS'] ?? '')));
if ($ip !== '' && $ignoreIps !== [] && in_array($ip, $ignoreIps, true)) {
    exit;
}

foreach (visit_ping_env_csv_list(trim((string) ($env['VISIT_PING_IGNORE_UA_SUBSTRINGS'] ?? ''))) as $frag) {
    if ($frag !== '' && stripos($ua, $frag) !== false) {
        exit;
    }
}

$dataDir = __DIR__ . DIRECTORY_SEPARATOR . 'data';
if (!is_dir($dataDir)) {
    @mkdir($dataDir, 0755, true);
}

$rateFile = $dataDir . DIRECTORY_SEPARATOR . 'visit_notify_rate.json';
$now = time();
$state = [];
if (is_readable($rateFile)) {
    $rawState = @file_get_contents($rateFile);
    if ($rawState !== false) {
        $decoded = json_decode($rawState, true);
        if (is_array($decoded)) {
            foreach ($decoded as $k => $v) {
                if (is_string($k) && is_int($v)) {
                    $state[$k] = $v;
                }
            }
        }
    }
}
$state = visit_ping_rate_prune($state, $now);
if ($ip !== '' && isset($state[$ip]) && $now - $state[$ip] < 3600) {
    exit;
}

$input = file_get_contents('php://input');
$payload = [];
if ($input !== false && $input !== '') {
    $decoded = json_decode($input, true);
    if (is_array($decoded)) {
        $payload = $decoded;
    }
}

$path = trim((string) ($payload['path'] ?? ''));
if (mb_strlen($path, 'UTF-8') > 500) {
    $path = mb_substr($path, 0, 500, 'UTF-8') . '…';
}
$referrer = trim((string) ($payload['referrer'] ?? ''));
if (mb_strlen($referrer, 'UTF-8') > 500) {
    $referrer = mb_substr($referrer, 0, 500, 'UTF-8') . '…';
}
$lang = trim((string) ($payload['lang'] ?? ''));
$tz = trim((string) ($payload['tz'] ?? ''));
$screen = trim((string) ($payload['screen'] ?? ''));

$geo = visit_ping_geo_lookup($ip);
$locParts = array_filter([$geo['city'], $geo['region'], $geo['country']], static fn (string $s): bool => $s !== '');
$location = $locParts !== [] ? implode(', ', $locParts) : '(unknown)';

$uaShow = $ua;
if (mb_strlen($uaShow, 'UTF-8') > 500) {
    $uaShow = mb_substr($uaShow, 0, 500, 'UTF-8') . '…';
}

$ts = gmdate('c');
$text = "New site visit — {$ts}\n\n"
    . "Location (IP-based, approximate): {$location}\n"
    . "Path: " . ($path !== '' ? $path : '—') . "\n"
    . "Referrer: " . ($referrer !== '' ? $referrer : '—') . "\n"
    . "Lang: " . ($lang !== '' ? $lang : '—') . "\n"
    . "TZ: " . ($tz !== '' ? $tz : '—') . "\n"
    . "Screen: " . ($screen !== '' ? $screen : '—') . "\n\n"
    . "User-Agent:\n{$uaShow}";

telegram_send_text($tgToken, $tgChat, $text);

if ($ip !== '') {
    $state[$ip] = $now;
    $state = visit_ping_rate_prune($state, $now);
    @file_put_contents($rateFile, json_encode($state, JSON_UNESCAPED_UNICODE), LOCK_EX);
}

exit;
