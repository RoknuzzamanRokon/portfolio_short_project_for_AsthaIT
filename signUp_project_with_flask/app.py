from flask import Flask, render_template, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os


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

@app.route('/submit', methods=['POST'])
def signup():
    try:
        user_data = request.json
        table.put_item(Item=user_data)
        return jsonify({'message': 'Data save successfully!'}), 200
    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials no provide'}), 500
    except PartialCredentialsError:
        return jsonify({'error': 'Incomplete AWS credentials'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)