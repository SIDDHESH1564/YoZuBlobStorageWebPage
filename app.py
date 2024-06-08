from flask import Flask, render_template, request, redirect, url_for, jsonify
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

app = Flask(__name__)

# Azure Blob Storage credentials
account_name = 'yozuaiservice1353585945'
account_key = 'aQYvk+s8Mv1VCSwo9tUxiUFdMttRteYvqMNEVhZGuWcrvLQ87bmrif7CYtegt3B4HVF22juILERm+ASt1N0A7g=='
container_name = 'images'

# Create a BlobServiceClient
connect_str = 'DefaultEndpointsProtocol=https;AccountName=' + account_name + ';AccountKey=' + account_key + ';EndpointSuffix=core.windows.net'
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
    blob_list = [blob.name for blob in container_client.list_blobs()][offset:offset + per_page]
    images = [{'name': blob, 'url': container_client.get_blob_client(blob).url} for blob in blob_list]
    return jsonify({'images': images})

@app.route('/delete/<blob_name>', methods=['POST'])
def delete_image(blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.delete_blob()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
