from flask import Flask, render_template, redirect, url_for, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/submit', methods=['POST'])
def handle_signup():
    try:
        user_data = request.form.to_dict()
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