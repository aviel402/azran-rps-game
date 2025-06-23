from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# --- הגדרות בסיסיות של השירות ---
# מומלץ למלא את הפרטים האמיתיים שלך כאן
manager_phone: 0583289789
email: x0583289789@gmail.com
connection_url: https://aviel123.onrender.com/game.com
service_name: אבן נייר ומספריים
brief_description: משחק אבן נייר ומספריים בטלפון
audio_url: 0
message: 0
long_explanation: 0
required_data_schema: 0
number_of_digits: 1
phone_number_required: True
email_required: False
credit_card_required: False
system_payments: False
external_payments: False
entry_amount_to_be_paid: 0
referral_phone: 0
analysis_delay: False
tracking_fields: 0
returned_data: 0
# --- הגדרות המשחק ---
CHOICES = {
    '1': 'אבן',
    '2': 'נייר',
    '3': 'מספריים'
}

RESULT_TEXT = {
    'win': 'כל הכבוד, ניצחת!',
    'lose': 'אופס, הפעם הפסדת.',
    'draw': 'תיקו! נסו שוב.'
}

# פונקציה שמחליטה מי ניצח
def decide_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return 'draw'
    
    winning_combos = {
        '1': '3',  # אבן מנצחת מספריים
        '2': '1',  # נייר מנצח אבן
        '3': '2'   # מספריים מנצחות נייר
    }

    if winning_combos.get(player_choice) == computer_choice:
        return 'win'
    else:
        return 'lose'

# --- הנתיב הראשי שאליו "עזרן" יפנה ---
@app.route('/rps_game', methods=['POST'])
def rps_game():
    # קודם כל, נבדוק מה "עזרן" מבקש מאיתנו
    target = request.json.get('target')

    # 1. שלב הרישום הראשוני של השירות
    # 1. שלב הרישום הראשוני של השירות
    if target == 'registration':
        service_data = {
            'manager_phone': MANAGER_PHONE,
            'email': EMAIL,
            'connection_url': BASE_URL + "/rps_game",
            'service_name': 'משחק אבן, נייר ומספריים',
            'brief_description': 'שירות המאפשר לשחק אבן, נייר ומספריים נגד המחשב.',
            'message': 'ברוכים הבאים למשחק אבן, נייר, מספריים. לחצו 1 לאבן, 2 לנייר, או 3 למספריים.',
            'long_explanation': 'שירות זה מאפשר לכם לשחק את המשחק הקלאסי אבן, נייר ומספריים נגד המחשב. בצעו את בחירתכם והמערכת תגיב.', # <-- השורה החדשה
            'number_of_digits': 1,
            'phone_number_required': False,
        }
        return jsonify(service_data)
    # 2. שלב עיבוד השיחה עצמה
    if target == 'service_processing':
        # נקבל את הבחירה של השחקן
        player_choice = request.json.get('digits')

        # אם השחקן לא הקיש כלום או הקיש משהו לא חוקי
        if player_choice not in CHOICES:
            # נחזיר הודעת שגיאה ונבקש ממנו לנסות שוב
            response = {
                'message': 'בחירה לא חוקית. אנא לחצו 1 לאבן, 2 לנייר, או 3 למספריים.',
                'number_of_digits': 1
            }
            return jsonify(response)

        # המחשב מגריל בחירה
        computer_choice = random.choice(list(CHOICES.keys()))

        # נבדוק מי ניצח
        result = decide_winner(player_choice, computer_choice)

        # נבנה את הודעת התוצאה
        result_message = (
            f"בחרתם {CHOICES[player_choice]}. "
            f"המחשב בחר {CHOICES[computer_choice]}. "
            f"{RESULT_TEXT[result]} "
            "כדי לשחק שוב, פשוט בחרו שוב: 1 לאבן, 2 לנייר, או 3 למספריים."
        )
        
        # נשלח את התוצאה בחזרה לעזרן, עם בקשה לקלט חדש
        response = {
            'message': result_message,
            'number_of_digits': 1
        }
        return jsonify(response)

    # אם הגענו לכאן, משהו לא תקין. נסיים את השיחה.
    # החזרת JSON ריק מסמנת לעזרן לנתק את השיחה.
    return jsonify({})

if __name__ == '__main__':
    # הרצת השרת. Port 5000 הוא ברירת מחדל נפוצה.
    app.run(host='0.0.0.0', port=5000)
