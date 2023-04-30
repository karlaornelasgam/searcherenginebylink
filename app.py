from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__, template_folder='C:/Users/karla/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0/LocalCache/local-packages/Python310/site-packages/flask/projecto/templates')
# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['motor']
collection = db['palabras']

# Define a route for the homepage
@app.route('/')
def index():
    # Get all the documents from the MongoDB collection
    documents = collection.find()
    # Render the template with the documents as context
    return render_template('index.html', documents=documents)

if __name__ == '__main__':
    app.run(debug=True)
