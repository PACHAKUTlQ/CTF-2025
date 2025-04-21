#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask import render_template

app = Flask(__name__)

@app.route('/calc', methods=['GET'])
def calculate():
    expression = request.args.get('expr')
    
    if not expression:
        return jsonify({"error": "No expression provided"}), 400
    
    for n in range(26):
        if (chr(n + 65) in expression or chr(n + 97) in expression):
            return jsonify({"error": "No letters allowed"}), 400
    
    for n in "!\"#$%&',:;<=>?@[\]^_`{|}~":
        if n in expression:
            return jsonify({"error": "No special characters allowed"}), 400
    
    try:
        result = eval(expression)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)