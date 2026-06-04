<?php
declare(strict_types=1);

require_once __DIR__ . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'load_dotenv.php';
require_once __DIR__ . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'telegram_notify.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: index.html', true, 303);
    exit;
}

$name = trim((string) ($_POST['name'] ?? ''));
$email = trim((string) ($_POST['email'] ?? ''));
$phone = trim((string) ($_POST['phone'] ?? ''));
$message = trim((string) ($_POST['message'] ?? ''));
$honeypot = trim((string) ($_POST['website'] ?? ''));

if ($honeypot !== '') {
    header('Location: index.html?sent=1#contact', true, 303);
    exit;
}

$ok =
    $name !== '' &&
    $message !== '' &&
    filter_var($email, FILTER_VALIDATE_EMAIL);

if (!$ok) {
    header('Location: index.html?sent=0#contact', true, 303);
    exit;
}

$dataDir = __DIR__ . DIRECTORY_SEPARATOR . 'data';
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0755, true);
}

$entry = [
    'ts' => gmdate('c'),
    'name' => $name,
    'email' => $email,
    'phone' => $phone,
    'message' => $message,
];

$line = json_encode($entry, JSON_UNESCAPED_UNICODE) . "\n";
$file = $dataDir . DIRECTORY_SEPARATOR . 'submissions.jsonl';
file_put_contents($file, $line, FILE_APPEND | LOCK_EX);

$env = load_dotenv(__DIR__);
$tgToken = trim((string) ($env['TELEGRAM_BOT_TOKEN'] ?? ''));
$tgChat = trim((string) ($env['TELEGRAM_CHAT_ID'] ?? ''));
if ($tgToken !== '' && $tgChat !== '') {
    telegram_notify_contact_submission($tgToken, $tgChat, $entry);
}

header('Location: index.html?sent=1#contact', true, 303);
exit;
