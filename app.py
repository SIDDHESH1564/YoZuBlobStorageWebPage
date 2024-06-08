import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from azure.core.exceptions import ResourceNotFoundError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

# Azure Blob Storage credentials
account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')


if not account_name or not account_key:
    raise ValueError("Azure Storage account name and/or key not provided in environment variables.")

container_name = 'images'

app = Flask(__name__)

# Create a BlobServiceClient
connect_str = f'DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net'

blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            blob_client = container_client.get_blob_client(file.filename)
            blob_client.upload_blob(file)
    return redirect(url_for('index'))

@app.route('/load', methods=['GET'])
def load_images():
    page = int(request.args.get('page', 1))
    per_page = 12
    offset = (page - 1) * per_page
    try:
        # Add logging to capture more details
        logging.debug("Listing blobs in the container")
        blob_list = container_client.list_blobs()
        
        # Correctly handle pagination
        blobs = []
        for i, blob in enumerate(blob_list):
            if i >= offset and i < offset + per_page:
                blobs.append(blob)
            if i >= offset + per_page:
                break

        images = [{'name': blob.name, 'url': container_client.get_blob_client(blob.name).url} for blob in blobs]
        return jsonify({'images': images})
    except Exception as e:
        logging.exception("An error occurred while loading images:")
        return jsonify({'images': []})

@app.route('/delete/<blob_name>', methods=['POST'])
def delete_image(blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.delete_blob()
    return redirect(url_for('index'))

