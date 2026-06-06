<?php
declare(strict_types=1);

require_once __DIR__ . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'load_dotenv.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['error' => 'method_not_allowed']);
    exit;
}

$env = load_dotenv(__DIR__);
$secret = trim((string) ($env['CONTACT_CSRF_SECRET'] ?? ''));

if ($secret === '') {
    http_response_code(503);
    echo json_encode(['error' => 'unavailable']);
    exit;
}

$ts = time();
$token = hash_hmac('sha256', (string) $ts, $secret);

echo json_encode(['ts' => $ts, 'token' => $token], JSON_UNESCAPED_UNICODE);
