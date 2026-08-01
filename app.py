from flask import Flask,request,jsonify
import psycopg2
import bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
        )
    return conn
@app.route('/')
def home():
    return "Hello DevJourney!"

@app.route('/api/signup',methods = ['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
            "INSERT INTO users (name,email,password_hash) VALUES(%s,%s,%s)",
            (name,email,password_hash)
        )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"massage" : "Signup successful"}) , 201

@app.route('/api/login' , methods = ['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name,password_hash FROM users WHERE email = %s",(email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        return jsonify({"message" : "Invalid email or password"}) , 401
    user_id,name,stored_hash = user

    if bcrypt.checkpw(password.encode('utf-8'),stored_hash.encode('utf-8')):
        return jsonify({"message" : "Login successfully","user_id":user_id,"name":name}) ,200
    else:
        return jsonify({"message" : "Invalid email or password"}),401
    

if __name__=='__main__':
    app.run(debug=True)