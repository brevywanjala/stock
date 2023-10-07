from flask import *
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# SQLite database connection
conn = sqlite3.connect('stock.db')
c = conn.cursor()

# Create stock table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS stock
             (item_id INTEGER PRIMARY KEY AUTOINCREMENT,
             item_name TEXT NOT NULL,
             quantity INTEGER NOT NULL,
             days_to_next_pick INTEGER NOT NULL,
             quantity_threshold INTEGER NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS students
             (student_id INTEGER PRIMARY KEY AUTOINCREMENT,
             student_name TEXT NOT NULL)''')

# Create students_pick table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS students_pick
             (pick_id INTEGER PRIMARY KEY AUTOINCREMENT,
             student_id INTEGER NOT NULL,
             item_id INTEGER NOT NULL,
             pick_timestamp TIMESTAMP,
             FOREIGN KEY (student_id) REFERENCES students(student_id),
             FOREIGN KEY (item_id) REFERENCES stock(item_id))''')




# Commit changes and close the connection
conn.commit()
conn.close()
# Dummy student data
app.secret_key = 'yodwudu8d?jkey'
@app.route('/')
def index():
    # Query the students_pick table to retrieve all student names and picked items
 
    return render_template('stock/index.html')

@app.route('/get_picked_items')
def get_picked_items():
    student_name = request.args.get('student_name')

    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    
    c.execute("SELECT stock.item_name, students_pick.pick_timestamp FROM students INNER JOIN students_pick ON students.student_id = students_pick.student_id INNER JOIN stock ON students_pick.item_id = stock.item_id WHERE students.student_name = ?", (student_name,))
    picked_items = [{'item_name': item[0], 'pick_date': item[1]} for item in c.fetchall()]
    conn.close()

    return jsonify(picked_items)



@app.route('/admin_panel')
def admin_panel():
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    
    # Retrieve the list of items in stock
    c.execute("SELECT item_id, item_name, quantity FROM stock")
    items = c.fetchall()

    # Retrieve the list of students
    c.execute("SELECT student_id, student_name FROM students")
    students = c.fetchall()
    
    conn.close()

    return render_template('stock/admin.html', items=items, students=students)

@app.route('/get_item_details')
def get_item_details():
    item_name = request.args.get('item_name')

    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute("SELECT item_name, quantity, days_to_next_pick, quantity_threshold FROM stock WHERE item_name = ?", (item_name,))
    item_details = c.fetchone()
    conn.close()

    if item_details:
        return jsonify({
            'item_name': item_details[0],
            'quantity': item_details[1],
            'days_to_next_pick': item_details[2],
            'quantity_threshold': item_details[3]
        })
    else:
        return jsonify(None)

@app.route('/insert_item', methods=['POST'])
def insert_item():
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        quantity = int(request.form.get('quantity'))

        conn = sqlite3.connect('stock.db')
        c = conn.cursor()

        try:
            # Check if the item already exists in the stock
            c.execute("SELECT item_id, days_to_next_pick, quantity_threshold FROM stock WHERE item_name = ?", (item_name,))
            existing_item = c.fetchone()

            if existing_item:
                item_id, days_to_next_pick, quantity_threshold = existing_item
                # If the item exists, update its quantity by adding the new quantity
                c.execute("UPDATE stock SET quantity = quantity + ? WHERE item_id = ?", (quantity, item_id))
                flash("Quantity updated successfully!", "success")

            else:
                # If the item does not exist, retrieve additional details from the form
                days_to_next_pick = int(request.form.get('days_to_next_pick'))
                quantity_threshold = int(request.form.get('quantity_threshold'))

                # Check if the required fields are provided
                if not days_to_next_pick or not quantity_threshold:
                    raise ValueError("Days to Next Pick and Quantity Threshold are required for a new item!","error")

                # Insert the item into the stock
                c.execute("INSERT INTO stock (item_name, quantity, days_to_next_pick, quantity_threshold) VALUES (?, ?, ?, ?)",
                          (item_name, quantity, days_to_next_pick, quantity_threshold))
                flash("Item added successfully!","success")

            conn.commit()
            conn.close()
            print("existing item",existing_item)
            return redirect(url_for('admin_panel'))
        except ValueError as e:
            flash(f"Days to Next Pick and Quantity Threshold are required for a new item", "warning")
            return redirect(url_for('admin_panel'))
        except Exception as e:
            flash(f"Internal Server Error: {str(e)}")
            return redirect(url_for('admin_panel'))


@app.route('/insert_student', methods=['POST'])
def insert_student():
  if request.method=='POST':
    student_name = request.form.get('student_name')

    # Insert the student into the database with initial date last picked as None
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (student_name, last_pick_timestamp ) VALUES (?, ?)",
              (student_name, None))
    conn.commit()
    conn.close()
    flash(f"success . Enjoy!" ,"success")


    return redirect(url_for('admin_panel'))
def insert_dummy_students_if_not_exist():
    dummy_students = [
        ("John Doe"),
        ("Jane Smith"),
        ("Michael Johnson")
    ]
    
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    
    for student_name in dummy_students:
        c.execute("SELECT student_id FROM students WHERE student_name = ?", (student_name,))
        existing_student = c.fetchone()
        
        if not existing_student:
            c.execute("INSERT INTO students (student_name) VALUES (?)", (student_name,))
    
    conn.commit()
    conn.close()
@app.route('/pick_item', methods=['POST'])
def pick_item():
    item_name = request.form.get('item_name')
    student_name = request.form.get('student_name')
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get the item details from the database
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute("SELECT stock.item_id, stock.quantity, stock.days_to_next_pick, stock.quantity_threshold FROM stock WHERE stock.item_name = ?", (item_name,))
    item_details = c.fetchone()

    if item_details:
        item_id, quantity, days_to_next_pick, quantity_threshold = item_details

        # Check if the item quantity is above the threshold
        if quantity > quantity_threshold:
            # Get the student's ID from the database
            c.execute("SELECT student_id FROM students WHERE student_name = ?", (student_name,))
            student_id = c.fetchone()

            if student_id:
                student_id = student_id[0]
                # Get the student's last pick date from the database
                c.execute("SELECT MAX(pick_timestamp) FROM students_pick WHERE student_id = ? AND item_id = ?", (student_id, item_id,))
                last_picked_date = c.fetchone()

                if last_picked_date is None or last_picked_date[0] is None:
                    # If the student hasn't picked the item before, allow the pick
                    insert_pick_date(c, student_id, item_id, current_date)
                    update_item_quantity(c, item_name, quantity - 1)
                    conn.commit()
                    conn.close()
                    flash(f"You picked {item_name}. Enjoy!" ,"success")
                else:
                    
                    # Calculate the number of days since the student's last pick
                    days_since_last_pick = (datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S") -
                                        datetime.strptime(last_picked_date[0], "%Y-%m-%d %H:%M:%S")).days
                    if days_since_last_pick >= days_to_next_pick:
                        # If enough days have passed, allow the pick
                        insert_pick_date(c, student_id, item_id, current_date)
                        update_item_quantity(c, item_name, quantity - 1)
                        conn.commit()
                        conn.close()
                        flash(f"You picked {item_name}. Enjoy!" ,"success")
                    else:
                        conn.close()
                        flash(f"You can pick {item_name} after {days_to_next_pick - days_since_last_pick} day(s)." ,"warning")
            else:
                conn.close()
                flash("Student not found." ,"error")
        else:
            conn.close()
            flash(f"Sorry, {item_name} is out of stock." ,"warning")
    else:
        conn.close()
        flash("Item not found." ,"error")
       
    return redirect(url_for('index'))

def insert_pick_date(cursor, student_id, item_id, pick_date):
    cursor.execute("INSERT INTO students_pick (student_id, item_id, pick_timestamp) VALUES (?, ?, ?)",
                   (student_id, item_id, pick_date))

def update_item_quantity(cursor, item_name, new_quantity):
    cursor.execute("UPDATE stock SET quantity = ? WHERE item_name = ?", (new_quantity, item_name))

@app.route('/get_items')
def get_items():
    query = request.args.get('query', '')

    # Query the stock table to retrieve similar item names
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute("SELECT item_name FROM stock WHERE item_name LIKE ?", ('%' + query + '%',))
    similar_items = [item[0] for item in c.fetchall()]
    conn.close()

    return jsonify(similar_items)
@app.route('/get_students')
def get_students():
    query = request.args.get('query', '')

    # Query the students table to retrieve
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute("SELECT student_name FROM students WHERE student_name LIKE ? ", ('%' + query + '%' ,))
    similar_students= [student[0] for student in c.fetchall()]
    print(similar_students,"similar students")
    conn.close()
    
    return jsonify(similar_students)



if __name__ == '__main__':
    insert_dummy_students_if_not_exist()
    app.run(debug=True)
