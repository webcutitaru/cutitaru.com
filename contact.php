<?php
declare(strict_types=1);

require_once __DIR__ . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'load_dotenv.php';
require_once __DIR__ . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'telegram_notify.php';

function contact_redirect(string $returnTo, int $sent): void
{
    $path = parse_url($returnTo, PHP_URL_PATH);
    if ($path === null || $path === '' || !str_starts_with($path, '/')) {
        $path = '/';
    }
    $fragment = parse_url($returnTo, PHP_URL_FRAGMENT);
    $hash = $fragment !== null && $fragment !== '' ? '#' . $fragment : '#contact';
    header('Location: ' . $path . '?sent=' . $sent . $hash, true, 303);
    exit;
}

function contact_client_ip(): string
{
    if (!empty($_SERVER['HTTP_CF_CONNECTING_IP'])) {
        return trim((string) $_SERVER['HTTP_CF_CONNECTING_IP']);
    }
    return trim((string) ($_SERVER['REMOTE_ADDR'] ?? ''));
}

/**
 * @param array<string, list<int>> $state
 * @return array<string, list<int>>
 */
function contact_rate_prune(array $state, int $now): array
{
    foreach ($state as $ip => $times) {
        $filtered = [];
        foreach ($times as $t) {
            if ($now - $t <= 3600) {
                $filtered[] = $t;
            }
        }
        if ($filtered === []) {
            unset($state[$ip]);
        } else {
            $state[$ip] = $filtered;
        }
    }
    return $state;
}

function contact_rate_allowed(string $ip, int $now, string $rateFile): bool
{
    if ($ip === '') {
        return true;
    }

    $state = [];
    if (is_readable($rateFile)) {
        $raw = @file_get_contents($rateFile);
        if ($raw !== false) {
            $decoded = json_decode($raw, true);
            if (is_array($decoded)) {
                foreach ($decoded as $k => $v) {
                    if (!is_string($k) || !is_array($v)) {
                        continue;
                    }
                    $times = [];
                    foreach ($v as $t) {
                        if (is_int($t)) {
                            $times[] = $t;
                        }
                    }
                    if ($times !== []) {
                        $state[$k] = $times;
                    }
                }
            }
        }
    }

    $state = contact_rate_prune($state, $now);
    $times = $state[$ip] ?? [];
    if (count($times) >= 5) {
        return false;
    }

    $times[] = $now;
    $state[$ip] = $times;
    @file_put_contents($rateFile, json_encode($state, JSON_UNESCAPED_UNICODE), LOCK_EX);
    return true;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /', true, 303);
    exit;
}

$name = trim((string) ($_POST['name'] ?? ''));
$email = trim((string) ($_POST['email'] ?? ''));
$phone = trim((string) ($_POST['phone'] ?? ''));
$city = trim((string) ($_POST['city'] ?? ''));
$message = trim((string) ($_POST['message'] ?? ''));
$honeypot = trim((string) ($_POST['website'] ?? ''));
$returnTo = trim((string) ($_POST['return_to'] ?? '/'));
$csrfTs = (int) ($_POST['csrf_ts'] ?? 0);
$csrfToken = trim((string) ($_POST['csrf_token'] ?? ''));

if ($honeypot !== '') {
    contact_redirect($returnTo, 1);
}

$env = load_dotenv(__DIR__);
$csrfSecret = trim((string) ($env['CONTACT_CSRF_SECRET'] ?? ''));
$now = time();

if ($csrfSecret === '') {
    contact_redirect($returnTo, 0);
}

if ($csrfTs <= 0 || $now - $csrfTs > 3600 || $csrfTs - $now > 60) {
    contact_redirect($returnTo, 0);
}

$expectedToken = hash_hmac('sha256', (string) $csrfTs, $csrfSecret);
if (!hash_equals($expectedToken, $csrfToken)) {
    contact_redirect($returnTo, 0);
}

$dataDir = __DIR__ . DIRECTORY_SEPARATOR . 'data';
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0755, true);
}

$rateFile = $dataDir . DIRECTORY_SEPARATOR . 'contact_rate.json';
if (!contact_rate_allowed(contact_client_ip(), $now, $rateFile)) {
    contact_redirect($returnTo, 0);
}

if (mb_strlen($name, 'UTF-8') > 200 || mb_strlen($message, 'UTF-8') > 5000) {
    contact_redirect($returnTo, 0);
}

$ok =
    $name !== '' &&
    $message !== '' &&
    filter_var($email, FILTER_VALIDATE_EMAIL);

if (!$ok) {
    contact_redirect($returnTo, 0);
}

$entry = [
    'ts' => gmdate('c'),
    'name' => $name,
    'email' => $email,
    'phone' => $phone,
    'city' => $city,
    'message' => $message,
];

$line = json_encode($entry, JSON_UNESCAPED_UNICODE) . "\n";
$file = $dataDir . DIRECTORY_SEPARATOR . 'submissions.jsonl';
file_put_contents($file, $line, FILE_APPEND | LOCK_EX);

$tgToken = trim((string) ($env['TELEGRAM_BOT_TOKEN'] ?? ''));
$tgChat = trim((string) ($env['TELEGRAM_CHAT_ID'] ?? ''));
if ($tgToken !== '' && $tgChat !== '') {
    telegram_notify_contact_submission($tgToken, $tgChat, $entry);
}

contact_redirect($returnTo, 1);
