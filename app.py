import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import requests
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ironman'

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://dharshiniraja2002:dharshiniraja2002@cluster0.msvm0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Bid"]
vendor_collection = db["vendor_details"]
bidder_collection = db["bidder_details"]
tender_collection = db["tenders"]
bid_collection = db["bids"]

@app.route("/", methods=['GET', 'POST'])
def index():
    """Renders the landing page with basic navigation"""
    return render_template("index.html")

@app.route("/animating")
def animating():
    """Renders the animation page"""
    return render_template("animating.html")

@app.route("/vendor_login_page", methods=['GET', 'POST'])
def vendor_login_page():
    return render_template("vendor_login_page.html")

@app.route("/vendor_registration.html", methods=['GET', 'POST'])
def vendor_registration():
    return render_template("vendor_registration.html")

@app.route("/bidder_login_page", methods=['GET', 'POST'])
def bidder_login_page():
    return render_template("bidder_login_page.html")

@app.route("/bidder_registration.html", methods=['GET', 'POST'])
def bidder_registration():
    return render_template("bidder_registration.html")

@app.route("/business_details", methods=['GET', 'POST'])
def business_details():
    if request.method == 'POST':
        gstin = request.form['gstin']
        business_details = verify_gstin(gstin)
        if business_details:
            session['details'] = business_details
            return render_template('business_details.html', details=business_details)
        else:
            return render_template('vendor_registration.html')

@app.route("/bidder_business_details", methods=['GET', 'POST'])
def bidder_business_details():
    if request.method == 'POST':
        gstin = request.form['gstin']
        bidder_business_details = verify_gstin(gstin)
        if bidder_business_details:
            session['details'] = bidder_business_details
            return render_template('bidder_business_details.html', details=bidder_business_details)
        else:
            return render_template('bidder_registration.html')

def verify_gstin(gstin, api_key="b67eec122c41145dc3c84095dd0c9f76"):  # Replace with actual API key if required
    url = f"http://sheet.gstincheck.co.in/check/{api_key}/{gstin}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            if data['flag']:
                return data
            else:
                return None
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None
    else:
        return None

@app.route("/login_check_vendor", methods=['GET', 'POST'])
def login_check_vendor():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = vendor_collection.find_one({"username": username, "password": password})

        if user:
            session['username'] = username
            return redirect('main_vendor_page')
        else:
            flash('Invalid username or password')
            return render_template('vendor_login_page.html')
    return redirect('main_vendor_page')

@app.route("/login_check_bidder", methods=['GET', 'POST'])
def login_check_bidder():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = bidder_collection.find_one({"username": username, "password": password})

        if user:
            session['username'] = username
            return redirect('/bidder_dashboard')
        else:
            flash('Invalid username or password')
            return render_template('bidder_login_page.html')
    return render_template('bidder_dashboard.html')

@app.route("/vendor_dashboard", methods=['GET', 'POST'])
def vendor_dashboard():
    username = request.form['username']
    password = request.form['password']
    phone_number = request.form['phone_number']
    gst_details = session['details']
    registration_date = datetime.datetime.strptime(gst_details['data']['rgdt'], '%d/%m/%Y')

    vendor_collection.insert_one({
        "username": username,
        "password": password,
        "phone_number": phone_number,
        "lgnm": gst_details['data']['lgnm'],
        "gstin": gst_details['data']['gstin'],
        "stj": gst_details['data']['stj'],
        "ntcrbs": gst_details['data']['ntcrbs'],
        "dty": gst_details['data']['dty'],
        "ctb": gst_details['data']['ctb'],
        "trade_name": gst_details['data']['tradeNam'],
        "registration_date": registration_date,
        "status": gst_details['data']['sts']
    })

    return render_template('vendor_dashboard.html')

@app.route("/bidder_dashboard", methods=['GET', 'POST'])
def bidder_dashboard():
    tenders = list(tender_collection.find())
    return render_template('bidder_dashboard.html', tenders=tenders)

@app.route("/add_tender", methods=['GET', 'POST'])
def add_tender():
    username = session['username']
    title = request.form['tenderName']
    description = request.form['tenderDescription']
    tender_type = request.form['tenderType']
    issue_date = request.form['issueDate']
    submission_deadline = request.form['submissionDeadline']
    status = "active"
    priority1 = request.form['priority1']
    priority2 = request.form['priority2']
    priority3 = request.form['priority3']

    tender_collection.insert_one({
        "title": title,
        "description": description,
        "tenderType": tender_type,
        "issueDate": issue_date,
        "submissionDeadline": submission_deadline,
        "vendorID": username,
        "status": status,
        "priority1": priority1,
        "priority2": priority2,
        "priority3": priority3
    })

    return render_template('vendor_dashboard.html')

@app.route("/main_vendor_page", methods=['GET', 'POST'])
def main_vendor_page():
    if 'username' not in session:
        return redirect(url_for('vendor_login_page'))

    username = session['username']
    tenders = list(tender_collection.find({"vendorID": username}))
    return render_template('vendor_dashboard.html', tenders=tenders)

@app.route('/get_user_details', methods=['GET'])
def get_user_details():
    if 'username' not in session:
        return redirect(url_for('vendor_login_page'))

    username = session['username']
    user_details = vendor_collection.find_one({"username": username})
    return render_template('userdetails.html', deets=user_details)

@app.route("/update_status", methods=['POST'])
def update_status():
    data = request.get_json()
    status = data.get('status')
    tender_id = data.get('tender_id')

    if status not in ['Active', 'Inactive']:
        return jsonify({'error': 'Invalid status'}), 400

    if not tender_id:
        return jsonify({'error': 'Tender ID is required'}), 400

    tender_collection.update_one({"_id": ObjectId(tender_id)}, {"$set": {"status": status}})
    return jsonify({'success': 'Status updated successfully'})

@app.route("/bid", methods=['GET', 'POST'])
def bid():
    if request.method == 'POST':
        gstin = request.form['gstin']
        tender_id = request.form['tenderId']
        priority1 = request.form['priority1']
        priority2 = request.form['priority2']
        priority3 = request.form['priority3']

        bid_collection.insert_one({
            "tender_id": tender_id,
            "gstin": gstin,
            "priority1": priority1,
            "priority2": priority2,
            "priority3": priority3
        })
    return redirect('bidder_dashboard')

@app.route('/result', methods=['POST', 'GET'])
def result():
    data = request.get_json()
    tender_id = data.get('tenderId')

    if not tender_id:
        return "Error: tenderId not found in the request", 400

    tender = tender_collection.find_one({"_id": ObjectId(tender_id)})
    bids = list(bid_collection.find({"tender_id": tender_id}))
    best_match = None

    for bid in bids:
        if bid['priority1'] == tender['priority1'] and \
           bid['priority2'] == tender['priority2'] and \
           bid['priority3'] == tender['priority3']:
            best_match = bid
            break

    if best_match:
        bidder_details = bidder_collection.find_one({"gstin": best_match['gstin']})
        return render_template('winner_details.html', bidder_details=bidder_details)
    else:
        flash("No matching bid found.")
        return render_template('no_bid.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
