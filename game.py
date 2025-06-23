import os
import random
from flask import Flask, request, jsonify

# יצירת אפליקציית Flask
app = Flask(__name__)

# הגדרת הכתובת המלאה של השרת. 
# חשוב מאוד: החלף את 'your-service-name' בשם השירות שלך ב-Render.
# לדוגמה: 'https://rock-paper-scissors-my-name.onrender.com'
# אם לא תעדכן את זה, הקישורים לקבצי שמע לא יעבדו.
# השארתי כאן ערך דמה כדי שהקוד ירוץ, אבל חובה לעדכן.
BASE_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://your-service-name.onrender.com')
API_PATH = '/rock-paper-scissors'
CONNECTION_URL = f"{BASE_URL}{API_PATH}"

# אפשרויות חוקיות למשחק
VALID_CHOICES = ["אבן", "נייר", "מספריים"]

# ------------------------------------------------------------------------------------
# פונקציה המטפלת בבקשת הרישום (target: "registration")
# ------------------------------------------------------------------------------------
def handle_registration():
    """
    יוצרת ומחזירה את אובייקט ה-JSON הנדרש לרישום השירות.
    """
    registration_data = {
        # פרטי מנהל
        "manager_phone": "0583289789",  # החלף במספר שלך
        "email": "x0583289789@gmail.com", # החלף באימייל שלך

        # פרטי השירות
        "connection_url": CONNECTION_URL,
        "service_name": "משחק אבן, נייר ומספריים",
        "brief_description": "שחקו אבן, נייר ומספריים נגד המחשב.",
        "long_explanation": "זהו שירות המאפשר לכם לשחק את המשחק המוכר אבן, נייר ומספריים נגד בינה מלאכותית. בכל תור, אמרו את בחירתכם, והמערכת תגיד לכם אם ניצחתם, הפסדתם או שיש תיקו. בהצלחה!",
        
        # הגדרות הודעת פתיחה
        "audio_url": "", # ניתן להוסיף קובץ שמע של ברכה
        "message": "שָׁלוֹם! בְּרוּכִים הַבָּאִים לְמִשְׂחַק אֶבֶן, נְיָר וּמִסְפָּרַיִם. אִמְרוּ אֶת הַבְּחִירָה שֶׁלָכֶם כְּדֵי לְהַתְחִיל.",

        # דרישת נתונים ראשונית מהמשתמש
        "required_data_schema": {
            "user_choice": "str" # אנחנו מצפים לקבל את בחירת המשתמש כמחרוזת
        },
        
        # הגדרת נתונים לניהול מצב שיחה (State)
        "returned_data": {
            "stage": "game_started",
            "player_score": 0,
            "computer_score": 0
        },

        # פרמטרים נוספים (חובה לשלוח עם ערכי ברירת מחדל)
        "number_of_digits": 0,
        "phone_number_required": False,
        "email_required": False,
        "credit_card_required": False,
        "system_payments": False,
        "external_payments": False,
        "entry_amount_to_be_paid": 0,
        "referral_phone": "",
        "analysis_delay": False,
        "tracking_fields": ["player_score", "computer_score"], # שדות שיוצגו בממשק הניהול
    }
    return jsonify(registration_data)

# ------------------------------------------------------------------------------------
# פונקציה המטפלת בתור במשחק (target: "service_processing")
# ------------------------------------------------------------------------------------
def handle_game_turn(data):
    """
    מבצעת את לוגיקת המשחק עבור תור בודד.
    """
    # קבלת הנתונים מהקריאה הקודמת
    state = data.get('returned_data', {})
    player_score = state.get('player_score', 0)
    computer_score = state.get('computer_score', 0)

    # קבלת בחירת המשתמש מהמידע שהמערכת ניתחה
    required_data = data.get('required_data', {})
    user_choice = required_data.get('user_choice', '').strip()

    # בדיקה אם המשתמש אמר משהו חוקי
    if user_choice not in VALID_CHOICES:
        response_message = f"לֹא הֵבַנְתִּי. אָנָא אִמְרוּ שׁוּב: {', '.join(VALID_CHOICES)}."
        
        # מחזירים את אותו המצב, כי המשחק לא התקדם
        next_state = state

    else:
        # הלוגיקה של המשחק
        computer_choice = random.choice(VALID_CHOICES)

        # קביעת המנצח
        if user_choice == computer_choice:
            result_text = "תֵּיקוּ!"
        elif (user_choice == "אבן" and computer_choice == "מספריים") or \
             (user_choice == "נייר" and computer_choice == "אבן") or \
             (user_choice == "מספריים" and computer_choice == "נייר"):
            result_text = "נִיצַחְתֶּם!"
            player_score += 1
        else:
            result_text = "הִפְסַדְתֶּם."
            computer_score += 1

        # בניית הודעת התגובה למשתמש
        score_text = f"הַתּוֹצָאָה הִיא {player_score} לָכֶם, וְ-{computer_score} לִי."
        prompt_text = "מָה הַבְּחִירָה הַבָּאָה שֶׁלָכֶם?"
        response_message = f"אֲנִי בָּחַרְתִּי {computer_choice}. {result_text} {score_text} {prompt_text}"

        # עדכון המצב לקראת התור הבא
        next_state = {
            "stage": "in_game",
            "player_score": player_score,
            "computer_score": computer_score
        }

    # הכנת התשובה לפלטפורמה
    response_data = {
        "message": response_message,
        "required_data_schema": {
            "user_choice": "str"
        },
        "returned_data": next_state
    }
    
    return jsonify(response_data)


# ------------------------------------------------------------------------------------
# ה-Route הראשי שיקבל את כל הפניות מהפלטפורמה
# ------------------------------------------------------------------------------------
@app.route(API_PATH, methods=['POST'])
def rock_paper_scissors_service():
    """
    נקודת הכניסה הראשית (Endpoint).
    מנתבת את הבקשה לפונקציה המתאימה לפי ערך ה-'target'.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        target = data.get("target")

        if target == "registration":
            return handle_registration()
        
        elif target == "service_processing":
            return handle_game_turn(data)
        
        else:
            # במקרה של target לא מוכר, מחזירים תשובה ריקה כדי לא לתקוע את השירות
            return jsonify({}), 200

    except Exception as e:
        # במקרה של תקלה, חשוב להחזיר תגובת 200 עם JSON ריק
        # כדי למנוע השעיה של השירות עקב שגיאות תקשורת.
        print(f"An error occurred: {e}")
        return jsonify({}), 200

# ------------------------------------------------------------------------------------
# הרצת השרת (מותאם ל-Render)
# ------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Render מגדיר את הפורט דרך משתנה סביבה.
    port = int(os.environ.get("PORT", 5000))
    # '0.0.0.0' חשוב כדי שהשרת יהיה נגיש מחוץ לקונטיינר.
    app.run(host='0.0.0.0', port=port)
