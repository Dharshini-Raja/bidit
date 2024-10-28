import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import requests
import vonage
import random
import psycopg2
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ironman'

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="Bid",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

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
  # return render_template("business_details.html")



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
  # return render_template("business_details.html")


def verify_gstin(gstin, api_key="b67eec122c41145dc3c84095dd0c9f76"):  # Replace with actual API key if required
  url = f"http://sheet.gstincheck.co.in/check/{api_key}/{gstin}"
  response = requests.get(url)
  if response.status_code == 200:
      try:
          # API response format might be unclear, handle potential parsing errors
          data = response.json()
          print(data)
          # print(data['flag'],"data")
          if data['flag'] == True:
            return data  # Assuming "active" indicates valid GSTIN
          else:
             return None
      except Exception as e:
          print(f"Error parsing response: {e}")
          return None
  else:
      # Handle other HTTP errors
      return None
  


@app.route("/login_check_vendor", methods=['GET', 'POST'])
def login_check_vendor():
   if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user exists in database
        cur.execute("SELECT * FROM vendor_details WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()

        if user:
            print(user,"user")
            session['username'] = username
            return redirect('main_vendor_page')
        else:
            # Invalid credentials, display error message or redirect back to login page
            flash('Invalid username or password')
            return render_template('vendor_login_page.html')
   return redirect('main_vendor_page')

@app.route("/login_check_bidder", methods=['GET', 'POST'])
def login_check_bidder():
   if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user exists in database
        cur.execute("SELECT * FROM bidder_details WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()

        if user:
            print(user,"user")
            session['username'] = username
            return redirect('/bidder_dashboard')
            # Invalid credentials, display error message or redirect back to login page
            flash('Invalid username or password')
            return render_template('bidder_login_page.html')
   return render_template('bidder_dashboard.html')

@app.route("/vendor_dashboard", methods=['GET', 'POST'])
def vendor_dashboard():
    username = request.form['username']
    password = request.form['password']  # Replace with actual password handling
    phone_number = request.form['phone_number']
    gst_details = session['details']
    print(type(gst_details),"type")
    registration_date = datetime.datetime.strptime(gst_details['data']['rgdt'], '%d/%m/%Y')
    cur.execute("INSERT INTO vendor_details (username, password, phone_number, lgnm, gstin, stj, ntcrbs, dty, ctb, trade_name, registration_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ", 
                (username, password, phone_number, str(gst_details['data']['lgnm']), str(gst_details['data']['gstin']), str(gst_details['data']['stj']), str(gst_details['data']['ntcrbs']), str(gst_details['data']['dty']), str(gst_details['data']['ctb']), str(gst_details['data']['tradeNam']), registration_date, str(gst_details['data']['sts'])))
    
    print("lallalala",username, password, phone_number, gst_details['data']['lgnm'], gst_details['data']['gstin'], gst_details['data']['stj'], gst_details['data']['ntcrbs'], gst_details['data']['dty'], gst_details['data']['ctb'], gst_details['data']['tradeNam'], registration_date,  gst_details['data']['sts'], gst_details)
    conn.commit()



    # Render the dashboard template
    return render_template('vendor_dashboard.html')

@app.route("/bidder_dashboard", methods=['GET', 'POST'])
def bidder_dashboard():
    # username = request.form['username']
    # password = request.form['password']  # Replace with actual password handling
    # phone_number = request.form['phone_number']
    # gst_details = session['details']
    # print(type(gst_details),"type")
    # registration_date = datetime.datetime.strptime(gst_details['data']['rgdt'], '%d/%m/%Y')
    # cur.execute("INSERT INTO bidder_details (username, password, phone_number, lgnm, gstin, stj, ntcrbs, dty, ctb, trade_name, registration_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ", 
    #             (username, password, phone_number, str(gst_details['data']['lgnm']), str(gst_details['data']['gstin']), str(gst_details['data']['stj']), str(gst_details['data']['ntcrbs']), str(gst_details['data']['dty']), str(gst_details['data']['ctb']), str(gst_details['data']['tradeNam']), registration_date, str(gst_details['data']['sts'])))
    
    # print("lallalala",username, password, phone_number, gst_details['data']['lgnm'], gst_details['data']['gstin'], gst_details['data']['stj'], gst_details['data']['ntcrbs'], gst_details['data']['dty'], gst_details['data']['ctb'], gst_details['data']['tradeNam'], registration_date,  gst_details['data']['sts'], gst_details)
    # conn.commit()
    cur.execute("SELECT * FROM tenders")
    tenders = cur.fetchall()
    # print(tenders,"tenders")
    return render_template('bidder_dashboard.html', tenders=tenders)



    # Render the dashboard template
    return render_template('bidder_dashboard.html')


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
    cur.execute("""
      INSERT INTO tenders 
      (Title, Description, TenderType, IssueDate, SubmissionDeadline, VendorID, Status, priority1, priority2, priority3) 
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """, 
      (
          title, description, tender_type, issue_date, submission_deadline, username, status, priority1, priority2, priority3
      )
  )

    conn.commit()
    print(title, description, tender_type, issue_date, submission_deadline, username, status, priority1, priority2, priority3)
    return render_template('vendor_dashboard.html')

@app.route("/main_vendor_page", methods = ['GET','POST'])
def main_vendor_page():
   
    if 'username' not in session:
        return redirect(url_for('vendor_login_page'))

    username = session['username']
    print(username,"comeon")
    # Fetch tenders created by the logged-in user
    cur.execute("SELECT * FROM tenders WHERE VendorID = %s", (username,))
    tenders = cur.fetchall()
    print(tenders,"tenders")
    return render_template('vendor_dashboard.html', tenders=tenders)

@app.route('/get_user_details', methods=['GET'])
def get_user_details():
    # Fetch user details from the database
    if 'username' not in session:
        return redirect(url_for('vendor_login_page'))

    username = session['username']
    print(username,"comeon")
    # Fetch tenders created by the logged-in user
    cur.execute("SELECT * FROM vendor_details WHERE username = %s", (username,))
    deets = cur.fetchone()
    userdata = {
        'username': deets[0],
        'phone_number': deets[2],
        'lgnm': deets[3],
        'gstin':deets[4],
        'stj':deets[5],
        'ntcrbs':deets[6],
        'dty':deets[7],
        'ctb':deets[8],
        'trade_name':deets[9],
        'registration_date':deets[10],
        'status':deets[11],
    }
    return render_template('userdetails.html', deets=userdata)


@app.route("/update_status", methods=['POST'])
def update_status():
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['Active', 'Inactive']:
        return jsonify({'error': 'Invalid status'}), 400

    # Assuming you pass the tender ID in the request
    tender_id = data.get('tender_id')
    if not tender_id:
        return jsonify({'error': 'Tender ID is required'}), 400

    try:
        cur.execute("""
            UPDATE tenders
            SET status = %s
            WHERE id = %s;
        """, (status, tender_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
    
    return jsonify({'success': 'Status updated successfully'})


@app.route("/bid", methods=['GET','POST'])
def bid():
    if request.method == 'POST':
        gstin = request.form['gstin']
        tenderId = request.form['tenderId']
        priority1 = request.form['priority1']
        priority2 = request.form['priority2']
        priority3 = request.form['priority3']

    try:
        cur.execute("""
            INSERT INTO bids 
            (tender_id, gstin, priority1, priority2, priority3) 
            VALUES (%s, %s, %s, %s, %s)
            """, 
            (tenderId, gstin, priority1, priority2, priority3)
        )
        conn.commit()
    except psycopg2.Error as e:
        # Handle the error, e.g., log the error, roll back the transaction, or display an error message to the user.
        conn.rollback()
        print(f"Error inserting bid: {e}")
    return redirect('bidder_dashboard')

@app.route('/submit_bid', methods=['POST', 'GET'])
def submit_bid():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'tenderId' not in data:
            return "Error: tenderId not found in the request", 400
        
        tender_id = data['tenderId']
        print(data, "data")

        # Here, you would insert into the database (if needed).
        # For now, just rendering the page.
        return render_template('bid.html', tender_id=tender_id)

    # Handle GET request (if needed, or you can just remove it)
    return "This endpoint only supports POST requests for submitting a bid."

@app.route('/result', methods=['POST', 'GET'])
def result():
    data = request.get_json()
    if not data or 'tenderId' not in data:
        return "Error: tenderId not found in the request", 400
    
    tender_id = data['tenderId']
    print("hello")
    # Fetch the tender details
    cur.execute("SELECT priority1, priority2, priority3 FROM tenders WHERE tenderid = %s", (tender_id,))
    tender_priorities = cur.fetchone()

    # Fetch bids for the given tender_id
    cur.execute("SELECT * FROM bids WHERE tender_id = %s", (tender_id,))
    bids = cur.fetchall()
    print(bids, tender_priorities,"lalalalla")
    best_match = None
    for bid in bids:
        if bid[3] == tender_priorities[0] and \
           bid[4] == tender_priorities[1] and \
           bid[5] == tender_priorities[2]:
            best_match = bid
            break
    print("bestmatch", best_match)
    if best_match:
        # Fetch bidder details using gstin
        cur.execute("SELECT * FROM bidder_details WHERE gstin = %s", (best_match[2],))
        bidder_details = cur.fetchone()

        # Display winner details in an alert or any other desired method
        # flash(f"Best Bidder: {bidder_details['unique_name']}")
        print(bidder_details,"bd")
        return render_template('winner_details.html', bidder_details=bidder_details)
    else:
        flash("No matching bid found.")
        return render_template('no_bid.html')

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000)
  #app.run(debug=True)
