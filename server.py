from datetime import *
from flask import *
from json import *
import uuid
import math
import re

app = Flask(__name__)

# Database to hold receipts - Not Persistent
receipts_db = {}


# Class for one item in a receipt
class Item:
    def __init__(self, shortDescription, price):
        self.shortDescription = shortDescription
        self.price = price


# Class for a receipt
class Receipt:
    def __init__(self, retailer, purchaseDate, purchaseTime, total, items):
        self.retailer = retailer
        self.purchaseDate = purchaseDate
        self.purchaseTime = purchaseTime
        self.total = total
        self.items = items


# Encode one item for json
def encode_item(item):
    property_order = ["price", "shortDescription"]
    item_dict = item.__dict__
    sorted_dict = {key: item_dict[key] for key in property_order}
    return sorted_dict


# Encode a receipt for json
def encode_receipt(receipt):
    property_order = ["retailer", "purchaseDate", "purchaseTime", "total", "items"]
    receipt_dict = receipt.__dict__
    receipt_dict["items"] = [encode_item(item) for item in receipt_dict["items"]]
    sorted_dict = {key: receipt_dict[key] for key in property_order}
    return sorted_dict


# make uuid for a single receipt
def generate_receipt_id():
    return str(uuid.uuid4())


# One point for every alphanumeric character in the retailer name.
def getRetailerPoints(retailer):
    count = 0
    for char in retailer:
        if char.isalnum():
            count += 1
    return count


# 50 points if the total is a round dollar amount with no cents.
# 25 points if the total is a multiple of 0.25.
def getTotalPoints(total):
    total = float(total)
    count = 0
    if total % 1 == 0.0:
        count += 50
    if total % 0.25 == 0.0:
        count += 25
    return count


# 5 points for every two items on the receipt.
# If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer.
# The result is the number of points earned.
def getItemsPoints(items):
    count = 0
    count += 5 * (len(items) // 2)
    for item in items:
        trimLength = len(item.shortDescription.strip())
        if trimLength % 3 == 0:
            count += math.ceil((float(item.price) * 0.2))
    return count


# 6 points if the day in the purchase date is odd.
def getDayPoints(date):
    day = int(date.split("-")[2])
    if day % 2 != 0:
        return 6
    else:
        return 0


# 10 points if the time of purchase is after 2:00pm and before 4:00pm.
def getTimePoints(time):
    hour = float(time.replace(":", "."))
    if hour > 14.00 and hour < 16.00:
        return 10
    else:
        return 0


# Get all the points earned by a receipt as specified in prompt
def getPoints(receipt):
    points = 0
    points += getRetailerPoints(receipt.retailer)
    points += getTotalPoints(receipt.total)
    points += getItemsPoints(receipt.items)
    points += getDayPoints(receipt.purchaseDate)
    points += getTimePoints(receipt.purchaseTime)
    return points


# validate the purchase date happened on valid earth date
def validateDate(date):
    try:
        # Check if the date string matches the pattern "YYYY-MM-DD"
        datetime.strptime(date, "%Y-%m-%d")

        # Check if the date is valid (handles non-existent dates)
        year, month, day = map(int, date.split("-"))
        datetime(year, month, day)

        return True
    except:
        return False


# validate the retailer is a string of alphanumeric characters
# FYI - README had retailer with space. However, yml had regex pattern for no non-alphanumeric or spaces. going to go off README
def validateRetailer(retailer):
    try:
        return type(retailer) == str
    except:
        return False


# Validate 24 hour time string "HH-MM"
def validateTime(purchaseTime):
    try:
        # Check if the time string matches the pattern "HH:MM"
        datetime.strptime(purchaseTime, "%H:%M")

        # Check if the time is valid
        hour, minute = map(int, purchaseTime.split(":"))
        datetime(1900, 1, 1, hour, minute)

        return True
    except:
        return False


# Validate the total is a decimal number with two places after the decimal (which must exist)
def validateTotal(total):
    try:
        return re.match(r"^\d+\.\d{2}$", total)
    except:
        return False


# Validate the items in the receipt (the description and price)
def validateItems(items):
    try:
        itemObjects = []
        if len(items) < 1:
            return False
        for item in items:
            if not re.match(r"^[\w\s\-]+$", item["shortDescription"]):
                return False
            if not re.match(r"^\d+\.\d{2}$", item["price"]):
                return False

            itemObj = Item(item["shortDescription"], item["price"])
            itemObjects.append(itemObj)
        return itemObjects
    except:
        return False


# Return a receipt object from properties, but return an error if they aren't cool
def safeMakeReceipt(retailer, purchaseDate, purchaseTime, total, items):
    if not validateRetailer(retailer):
        return None
    if not validateDate(purchaseDate):
        return None
    if not validateTime(purchaseTime):
        return None
    if not validateTotal(total):
        return None
    itemObjs = validateItems(items)
    if not itemObjs:
        return None
    return Receipt(retailer, purchaseDate, purchaseTime, total, itemObjs)


# POST endpoint
# Add a receipt to the database and return the ID generated for it
@app.route("/receipts/process", methods=["POST"])
def process_receipt():
    try:
        data = request.get_json()  # Get the JSON payload from the request
        retailer = data.get("retailer")
        purchaseDate = data.get("purchaseDate")
        purchaseTime = data.get("purchaseTime")
        total = data.get("total")
        items = data.get("items")

        # Make the receipt object from the data provided in request
        receipt = safeMakeReceipt(retailer, purchaseDate, purchaseTime, total, items)
        if receipt == None:
            response = make_response(
                jsonify({"description": "The receipt is invalid"}), 400
            )
            return response
        else:
            receipt_id = generate_receipt_id()
            receipts_db[receipt_id] = receipt  # Add receipt to database

            response_data = {"id": receipt_id}  # Return the id payload
            response = make_response(jsonify(response_data), 200)
            return response
    except:
        response = make_response(
            jsonify({"description": "The receipt is invalid"}), 400
        )
        return response


# GET Endoint
# Calculate the points earned for a receipt in the database and return
@app.route("/receipts/<string:id>/points", methods=["GET"])
def get_receipt_points(id):
    if id in receipts_db:
        receipt = receipts_db[id]
        points = getPoints(receipt)
        response = make_response(jsonify({"points": points}), 200)
        return response
    else:
        response = make_response(
            jsonify({"description": "No receipt found for that id"}), 404
        )
        return response


# GET Endpoint
# Give an ID for a receipt and return the encoded json value
@app.route("/receipts/<string:id>", methods=["GET"])
def get_receipt(id):
    if id in receipts_db:
        receipt = receipts_db[id]
        return jsonify(encode_receipt(receipt))
    else:
        return jsonify({"error": "Receipt ID not found"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
