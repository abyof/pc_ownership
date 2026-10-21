from flask import Flask, request, render_template
import sqlite3
import os 
import re 
app = Flask(__name__)
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pc_document.db")
def pc_archive():
    conn = sqlite3.connect(db_path) #opens the door for the database
    try:
        cursor= conn.cursor() # (pointer)prepare the workers to carry out commands like create, insert, delete, find...
        cursor.execute("CREATE TABLE IF NOT EXISTS pc_data (holder_name TEXT, id_number TEXT PRIMARY KEY, serial_number TEXT, pc_brand TEXT)")
        conn.commit()
    finally:
        conn.close()
def register_pc(holder_name, id_number, serial_number, pc_brand):
    conn = sqlite3.connect(db_path)
    try: 
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pc_data VALUES(?,?,?,?)", (holder_name, id_number, serial_number, pc_brand))
        conn.commit()
        return "PC's info registered successfully."
    except sqlite3.IntegrityError as e:
        return f"This id already exists. Error occurred. {e}"
    finally:
        conn.close()
def find_pc(id_number, serial_number):
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pc_data WHERE id_number = ? AND serial_number = ?", (id_number, serial_number))
        data = cursor.fetchone()
        if data:
            return ("Pc is available.", data)
        else:
            return ("Pc not found.", None)
    finally:
        conn.close()
def update_pc(id_number, serial_number, new_pc_brand, new_serial_number):
    conn = sqlite3.connect(db_path)
    
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE pc_data SET pc_brand= ?, serial_number= ? WHERE id_number= ? AND serial_number= ?", (new_pc_brand, new_serial_number, id_number, serial_number))
        if cursor.rowcount > 0:
            conn.commit()
            return "Pc's info updated successfully." 
        else:
            return "Update failed. No pc found by the provided id number."
    finally:
        conn.close()
def validate_id(id_number):
    clean_id = re.match(r"^\d{4}/\d{2}$", id_number)
    if not clean_id:
        return "Please write your id in the correct format.(0093/17)"
def validate_serial(serial_number):
    clean_serial = re.match(r"^[A-Za-z0-9]+$", serial_number)
    if not clean_serial:
        return "Serial_number must be a combinations of characters."
def validate_new_serial(new_serial_number):
    clean_serial = re.match(r"^[A-Za-z0-9]+$", new_serial_number)
    if not clean_serial:
        return "Serial_number must be a combinations of characters."

def register_validation(holder_name, id_number, pc_brand, serial_number):
    four_values = [holder_name, id_number, pc_brand, serial_number]
    clean_brand = pc_brand.replace("-", "").replace("_", "")
    invalid_id = validate_id(id_number)
    invalid_serial = validate_serial(serial_number)
    if any (not val for val in four_values):
        return "Error: All fields are required!"
    elif not clean_brand.isalnum():
            return "Error. Invalid characters used."
    elif clean_brand.isdigit():
        return "Error. Pc name can't be numbers."
    elif invalid_id:
        return invalid_id
    elif invalid_serial:
        return invalid_serial
def search_validation(id_number, serial_number):
    search_values = [id_number, serial_number]
    invalid_id = validate_id(id_number)
    invalid_serial = validate_serial(serial_number)
    if any (not val for val in search_values):
        return "Error: All fields are required!"
    elif invalid_id:
        return invalid_id
    elif invalid_serial:
        return invalid_serial
    
def update_validation(new_pc_brand, new_serial_number):
    update_values = [new_pc_brand, new_serial_number]
    clean_brand = new_pc_brand.replace("-", "").replace("_", "")
    invalid_serial = validate_new_serial(new_serial_number)
    if any(not val for val in update_values):
        return "Error. All fields are required."
    elif not clean_brand.isalnum():
        return "Error. Invalid characters used."
    elif clean_brand.isdigit():
        return "Error. Pc name can't be numbers."
    elif invalid_serial:
        return invalid_serial
    
@app.route('/')
def home():
    return render_template("pc_input.html")
@app.route('/belong', methods= ['POST'])
def pc_belong():
    holder_name = request.form.get("holder_name", "").strip()
    id_number = request.form.get("id_number", "").strip()
    pc_brand = request.form.get("pc_brand", "").strip()
    serial_number = request.form.get("serial_number", "").strip()
    error = register_validation(holder_name, id_number, pc_brand, serial_number)
    if error:
        return render_template("pc_input.html", error= error)
    register = register_pc(holder_name, id_number, serial_number, pc_brand)
    return render_template("pc_input.html", holder_name= holder_name, pc_brand= pc_brand, serial_number= serial_number, register = register)
@app.route('/find', methods= [ 'GET','POST'])
def pc_search():
    if request.method == "GET":
        return render_template("pc_find.html")
    id_number = request.form.get("id_number", "").strip()
    serial_number = request.form.get("serial_number", "").strip()
    error = search_validation(id_number, serial_number)
    if error:
        return render_template("pc_find.html", error= error)
    search = find_pc(id_number, serial_number)
    status_message = search[0]
    info = search[1]
    holder_name = id_num = serial_num = pc_brand = ""
    if info:
        holder_name = info[0]
        id_num = info[1]
        serial_num = info[2]
        pc_brand = info[3]
    return render_template("pc_find.html", holder_name= holder_name, id_number= id_num, serial_number= serial_num, pc_brand= pc_brand, status_message= status_message, info= info)
@app.route('/update', methods= ['GET', 'POST'])

def alter_pc():
    if request.method == 'GET':
        return render_template("pc_update.html")
    id_number = ""
    serial_number = ""
    new_serial_number = ""
    new_pc_brand = ""
    user_action = None
    found = None
    update = None
    status_message = ""
    show = ""
    error = None

    user_action = request.form.get("action")

    if user_action == "verify":
        id_number = request.form.get("id_number", "").strip()
        serial_number = request.form.get("serial_number", "").strip()
        error = search_validation(id_number, serial_number)
        if error:
            return render_template("pc_update.html", error= error)        
        found = find_pc(id_number, serial_number)
        status_message = found[0]
        show = found[1]
    elif user_action == "update":
        id_number = request.form.get("valid_id_number", "").strip()
        serial_number = request.form.get("valid_serial_number", "").strip()
        error = search_validation(id_number, serial_number)
        if error:
            return render_template("pc_update.html", error= error) 
        new_serial_number = request.form.get("new_serial_number", "").strip()
        new_pc_brand = request.form.get("new_pc_brand", "").strip()
        error = update_validation(new_pc_brand, new_serial_number)
        if error:
            return render_template("pc_update.html", error= error)
        update = update_pc(id_number, serial_number, new_pc_brand, new_serial_number)
        found = True
        serial_number = new_serial_number
        new_serial_number = ""
    return render_template("pc_update.html", id_number=id_number,serial_number= serial_number, found= found, status_message= status_message, show= show, new_serial_number= new_serial_number, new_pc_brand= new_pc_brand, update= update)
if __name__ == "__main__":
    pc_archive()
    app.run(debug= True)