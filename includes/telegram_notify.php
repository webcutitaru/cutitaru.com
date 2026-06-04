<?php
declare(strict_types=1);

/**
 * Sends plain text via Telegram Bot API. Failures are logged only.
 */
function telegram_send_text(string $botToken, string $chatId, string $text): void
{
    if (mb_strlen($text, 'UTF-8') > 4096) {
        $text = mb_substr($text, 0, 4090, 'UTF-8') . "\n…";
    }

    $url = 'https://api.telegram.org/bot' . $botToken . '/sendMessage';
    $payload = http_build_query(
        [
            'chat_id' => $chatId,
            'text' => $text,
            'disable_web_page_preview' => '1',
        ],
        '',
        '&',
        PHP_QUERY_RFC3986
    );

    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        if ($ch === false) {
            error_log('telegram_notify: curl_init failed');
            return;
        }
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $payload,
            CURLOPT_HTTPHEADER => ['Content-Type: application/x-www-form-urlencoded'],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 8,
        ]);
        $raw = curl_exec($ch);
        $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($raw === false || $code !== 200) {
            error_log('telegram_notify: HTTP ' . $code);
        }
        return;
    }

    $ctx = stream_context_create(
        [
            'http' => [
                'method' => 'POST',
                'header' => "Content-Type: application/x-www-form-urlencoded\r\n",
                'content' => $payload,
                'timeout' => 8,
            ],
        ]
    );
    $raw = @file_get_contents($url, false, $ctx);
    if ($raw === false) {
        error_log('telegram_notify: file_get_contents failed');
    }
}

/**
 * Sends a plain-text notification via Telegram Bot API. Failures are logged only.
 */
function telegram_notify_contact_submission(string $botToken, string $chatId, array $entry): void
{
    $name = (string) ($entry['name'] ?? '');
    $email = (string) ($entry['email'] ?? '');
    $phone = (string) ($entry['phone'] ?? '');
    $message = (string) ($entry['message'] ?? '');
    $ts = (string) ($entry['ts'] ?? '');

    $phoneLine = $phone !== '' ? $phone : '—';
    $body = $message;
    if (mb_strlen($body, 'UTF-8') > 3500) {
        $body = mb_substr($body, 0, 3500, 'UTF-8') . "\n…(truncated)";
    }

    $text = "New contact — {$ts}\n\n"
        . "Name: {$name}\n"
        . "Email: {$email}\n"
        . "Phone: {$phoneLine}\n\n"
        . "Message:\n{$body}";

    telegram_send_text($botToken, $chatId, $text);
}
