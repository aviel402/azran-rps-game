<?php
// virtual_friend_gemini.php (חינמי לחלוטין)
require __DIR__ . '/vendor/autoload.php';

use Gemini\Laravel\Facades\Gemini;

// --- הגדרות ---
$geminiApiKey = getenv('GOOGLE_API_KEY'); // קריאה ממשתנה סביבה ב-Render
$sessionDir = '/var/data/sessions/'; // דיסק קשיח ב-Render

// וידוא שהתיקייה קיימת
if (!is_dir($sessionDir)) {
    mkdir($sessionDir, 0777, true);
}

// "אישיות" ה-AI. אתה יכול לערוך אותה כרצונך.
$system_prompt = "
    אתה חבר וירטואלי קולי בשם 'אבי'. המטרה שלך היא להיות חבר טוב, אמפתי, סקרן ומעניין.
    אתה מדבר עם אנשים דרך הטלפון. כללי התנהגות:
    1. אל תזכיר שאתה מודל שפה או בינה מלאכותית. אתה 'אבי'.
    2. תשובותיך צריכות להיות קצרות וקולחות, באורך של 2-3 משפטים, כדי להתאים לשיחה קולית.
    3. תמיד תנסה לשאול שאלה בסוף התשובה שלך כדי להמשיך את השיחה.
    4. השתמש בשפה יומיומית וידידותית בעברית.
";

// --- קבלת נתונים מימות המשיח ---
$callId = $_REQUEST['ApiCallId'] ?? 'test_id';
$userText = $_REQUEST['text'] ?? ''; // הטקסט מגיע ישירות ממודול ה-STT
$sessionFile = $sessionDir . $callId . '.json';

if (!$geminiApiKey) {
    echo 'read=t-שגיאה, מפתח גוגל אי פי איי לא הוגדר בשרת.=,hangup';
    exit;
}

// התחברות ל-Gemini
$client = Gemini::client($geminiApiKey);

// --- ניהול היסטוריית שיחה ---
$history = [];
if (file_exists($sessionFile)) {
    $history = json_decode(file_get_contents($sessionFile), true) ?: [];
}

// הוספת ההודעה החדשה של המשתמש
$history[] = ['role' => 'user', 'parts' => [['text' => $userText]]];

// --- בניית הבקשה ל-Gemini ושליחתה ---
try {
    $chat = $client->geminiPro()->startChat($history);
    $response = $chat->sendMessage($userText); // Gemini זוכר את ההיסטוריה בעצמו
    $aiTextResponse = $response->text();

} catch (Exception $e) {
    echo 'read=t-אני צריך רגע לחשוב, תן לי שניה.=,hangup';
    exit;
}

// הוספת תשובת ה-AI להיסטוריה ושמירתה בקובץ
$history[] = ['role' => 'model', 'parts' => [['text' => $aiTextResponse]]];
file_put_contents($sessionFile, json_encode($history));

// --- החזרת פקודה לימות המשיח כדי ליצור לופ של שיחה ---
$sanitizedResponse = str_replace(['"', "'", '`'], '', $aiTextResponse);

// **זה החלק החשוב:** אחרי שהמערכת מקריאה את התשובה, היא חוזרת לאותה שלוחה
// כדי להפעיל מחדש את ההאזנה וה-STT, ובכך ליצור שיחה מתמשכת.
// שנה את "10" למספר השלוחה שלך.
$ivr_command = "read=t-{$sanitizedResponse}=,go_to_folder,/10"; 

echo $ivr_command;
?>
