import logging
from flask import Flask

app = Flask(__name__)

# Category 7 violation: logging passwords and tokens in plaintext
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    app.logger.info(f"User {username} logged in with password {password}")
    return 'ok'

# Category 7 violation: logging API keys and credit card numbers
def charge_card(api_key, card_number, cvv, amount):
    app.logger.info(f"Charging card {card_number} cvv={cvv} with key {api_key} amount={amount}")
    # ...
