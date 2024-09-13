from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['energy_db']

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Mapping department names to MongoDB field names
department_map = {
    "east campus": "East_Campus",
    "mba": "MBA_&_MCA",
    "mca": "MBA_&_MCA",
    "civil": "Civil",
    "mech": "Mech",
    "auto": "Auto"
}

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_query = data.get('query', '').lower()

    collection_name = get_collection_name(user_query)
    if not collection_name:
        return jsonify({"response": "I can provide data on solar power and electricity. Please ask about either!"})

    date_query = extract_date(user_query)
    department_query = extract_department(user_query)
    total_query = extract_total(user_query)

    try:
        query = build_query(date_query, department_query, total_query)

        logger.debug(f"Query: {query}")  # Debug statement
        response = db[collection_name].find_one(query)
        
        if not response:
            return jsonify({"response": "No data found for the specified criteria."})
        
        return jsonify({"response": dumps(response)})
    except Exception as e:
        logger.error(f"Error fetching data from the database: {str(e)}")
        return jsonify({"response": f"Error fetching data from the database: {str(e)}"})

def get_collection_name(query):
    """Determine the MongoDB collection based on the user query."""
    if "solar" in query:
        return 'solar_power'
    elif "electricity" in query:
        return 'electricity_data'
    return None

def extract_date(query):
    """Extract date from the query if present and valid."""
    if "on" in query:
        date_part = query.split("on")[1].strip()
        try:
            date_object = datetime.strptime(date_part, "%d.%m.%Y")
            return date_object
        except ValueError:
            logger.error(f"Invalid date format: {date_part}")
            return None
    return None

def extract_department(query):
    """Extract department from the query if present."""
    for key, value in department_map.items():
        if key in query:
            return value
    return None

def extract_total(query):
    """Extract total from the query if present and valid."""
    if "total" in query:
        try:
            total_part = query.split("total of")[1].strip()
            return int(total_part)
        except (ValueError, IndexError):
            logger.error(f"Invalid total value: {total_part}")
            return None
    return None

def build_query(date_query, department_query, total_query):
    """Build the query for MongoDB based on extracted parameters."""
    query = {}

    if date_query:
        # Adjust to MongoDB's ISODate format range for the given day
        start_date = datetime.combine(date_query, datetime.min.time())
        end_date = datetime.combine(date_query, datetime.max.time())
        query["Date"] = {"$gte": start_date, "$lte": end_date}
        logger.debug(f"Date Query: {query['Date']}")

    if department_query:
        query[department_query] = {"$exists": True}

    if total_query is not None:
        query["Total"] = total_query

    return query

if __name__ == '__main__':
    app.run(debug=True)
