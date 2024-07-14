from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from boto3.dynamodb.conditions import Attr
from dotenv import load_dotenv
import os
import uuid



app = Flask(__name__)

load_dotenv()

aws_access_key = os.environ.get("AWS_ACCESS_KEY")
aws_secret_key = os.environ.get("AWS_SECRET_KEY")
aws_region = os.environ.get("REGION_NAME")

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

table = dynamodb.Table('asignUp')
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login-submit', methods=['POST'])
def handle_login():
    contact = request.form.get("contact")
    password = request.form.get("password")

    if not contact or not password:
        return render_template('login.html', error='Both fields are required')


    try:
        response = table.scan(
            FilterExpression=Attr('contact').eq(contact)
        )
        items = response.get('Items', [])
        if items and items[0]['password'] == password:
            session['user'] = items[0]
            print("Login successful")
            return redirect(url_for('about'))
        else:
            print("Invalid credentials")
            return render_template('login.html', error='Invalid credentials')
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials not provided'}), 500
    except PartialCredentialsError:
        return jsonify({'error': 'Incomplete AWS credentials'}), 500
    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'error': str(e)}), 500





@app.route('/submit', methods=['POST'])
def handle_signup():
    try:
        user_data = request.form.to_dict()

        contact = user_data.get("contact")
        password = user_data.get("password")

        if not contact or not password:
            return render_template('signup.html', error='Contact and password are required')
        
        if len(password) < 4:
            return render_template('signup.html', error='Password must be at least 4 characters long.')
    
        user_data['user-id'] = str(uuid.uuid4())
        table.put_item(Item=user_data)
        return redirect(url_for('login'))
        
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials no provide'}), 500
    except PartialCredentialsError:
        return jsonify({'error': 'Incomplete AWS credentials'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)