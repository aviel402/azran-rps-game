<?php
// הגדרת סוג התוכן שיוחזר - תמיד JSON
header('Content-Type: application/json');

// קבלת גוף הבקשה שנשלח ב-POST
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// בודקים אם קיימים נתונים והם תקינים
if (!$data || !isset($data['target'])) {
    // אם לא, מחזירים JSON ריק עם סטטוס 200 כדי לא להשעות את השירות
    echo json_encode([]);
    exit;
}

// קבלת הכתובת הדינמית מ-Render
$baseUrl = $_SERVER['RENDER_EXTERNAL_URL'] ?? 'https://your-service-name.onrender.com';
$connectionUrl = $baseUrl . '/api.php';


// --- פונקציה לטיפול ברישום ---
function handle_registration($connectionUrl) {
    $registrationData = [
        // פרטי מנהל
        'manager_phone' => '0500000000', // <<< החלף במספר שלך
        'email' => 'manager@example.com', // <<< החלף באימייל שלך
        
        // פרטי השירות
        'connection_url' => $connectionUrl,
        'service_name' => 'משחק אבן, נייר ומספריים (PHP)',
        'brief_description' => 'שחקו אבן, נייר ומספריים נגד המחשב.',
        'message' => 'שָׁלוֹם! בְּרוּכִים הַבָּאִים לְמִשְׂחַק אֶבֶן, נְיָר וּמִסְפָּרַיִם בגרסת הפי-אייץ-פי.',
        
        // דרישת נתונים וניהול מצב
        'required_data_schema' => ['user_choice' => 'str'],
        'returned_data' => [
            'stage' => 'game_started',
            'player_score' => 0,
            'computer_score' => 0
        ],

        // פרמטרים נוספים חובה
        'audio_url' => '', 'long_explanation' => '', 'number_of_digits' => 0,
        'phone_number_required' => false, 'email_required' => false, 'credit_card_required' => false,
        'system_payments' => false, 'external_payments' => false, 'entry_amount_to_be_paid' => 0,
        'referral_phone' => '', 'analysis_delay' => false, 'tracking_fields' => []
    ];
    return $registrationData;
}


// --- פונקציה לטיפול בתור במשחק ---
function handle_game_turn($data) {
    $validChoices = ["אבן", "נייר", "מספריים"];
    
    // קבלת מצב מהקריאה הקודמת
    $state = $data['returned_data'] ?? ['player_score' => 0, 'computer_score' => 0];
    $player_score = $state['player_score'];
    $computer_score = $state['computer_score'];
    
    // קבלת בחירת המשתמש
    $user_choice = $data['required_data']['user_choice'] ?? '';
    
    if (!in_array($user_choice, $validChoices)) {
        $response_message = "לֹא הֵבַנְתִּי. אָנָא אִמְרוּ שׁוּב: אבן, נייר, או מספריים.";
        $next_state = $state;
    } else {
        $computer_choice = $validChoices[array_rand($validChoices)];
        
        if ($user_choice == $computer_choice) {
            $result_text = "תֵּיקוּ!";
        } elseif (($user_choice == "אבן" && $computer_choice == "מספריים") || 
                  ($user_choice == "נייר" && $computer_choice == "אבן") || 
                  ($user_choice == "מספריים" && $computer_choice == "נייר")) {
            $result_text = "נִיצַחְתֶּם!";
            $player_score++;
        } else {
            $result_text = "הִפְסַדְתֶּם.";
            $computer_score++;
        }
        
        $score_text = "הַתּוֹצָאָה הִיא {$player_score} לָכֶם, וְ-{$computer_score} לִי.";
        $prompt_text = "מָה הַבְּחִירָה הַבָּאָה שֶׁלָכֶם?";
        $response_message = "אֲנִי בָּחַרְתִּי {$computer_choice}. {$result_text} {$score_text} {$prompt_text}";
        
        $next_state = [
            'stage' => 'in_game',
            'player_score' => $player_score,
            'computer_score' => $computer_score
        ];
    }
    
    return [
        'message' => $response_message,
        'required_data_schema' => ['user_choice' => 'str'],
        'returned_data' => $next_state
    ];
}


// --- ניתוב הבקשה הראשי ---
$response = [];
switch ($data['target']) {
    case 'registration':
        $response = handle_registration($connectionUrl);
        break;
    case 'service_processing':
        $response = handle_game_turn($data);
        break;
}

// החזרת התגובה כ-JSON
echo json_encode($response, JSON_UNESCAPED_UNICODE);

?>
