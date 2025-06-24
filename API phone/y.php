<?php
$digit = $_GET["digit"] ?? "";

if ($digit == "1") {
    header("Location: 1/code.php");
    exit;
}
if ($digit == "2") {
    header("Location: 2/code.php");
    exit;
}
if ($digit == "3") {
    header("Location: 3/code.php");
    exit;
}
if ($digit == "4") {
    header("Location: 4/code.php");
    exit;
}

// תפריט ראשי - מוצג כשהמאזין נכנס לשלוחה
echo "ברוך הבא למערכת API PHONE.#";
echo "הקש 1 לתוכנות טקסטואליות.#";
echo "הקש 2 למשחקים קוליים.#";
echo "הקש 3 לאודות היוצר.#";
echo "הקש 4 להפתעה היומית.#";
?>
