from flask import Flask, request, render_template
import sqlite3
import os 
import re 
app = Flask(__name__)
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pc_document.db")
def pc_archive():
    conn = sqlite3.connect(db_path)
    try:
        cursor= conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS pc_data (holder_name TEXT, id_number TEXT PRIMARY KEY, serial_number TEXT, pc_brand TEXT)")
    finally:
        conn.commit()
        conn.close()
def register_pc(holder_name, id_number, serial_number, pc_brand):
    conn = sqlite3.connect(db_path)
    try: 

        cursor = conn.cursor()
        cursor.execute("INSERT INTO pc_data VALUES(?,?,?,?)", (holder_name, id_number, serial_number, pc_brand))
        conn.commit()
        conn.close()
        return "PC's info registered successfully."
    except sqlite3.IntegrityError as e:
        return f"This id already exists. Error occurred. {e}"
def find_pc(id_number, serial_number):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pc_data WHERE id_number = ? AND serial_number = ?", (id_number, serial_number))
    data = cursor.fetchone()
    if data:
        return ("Pc is available.", data)
    else:
        return ("Pc not found.", None)
def update_pc(id_number, serial_number, new_pc_brand, new_serial_number):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE pc_data SET pc_brand= ?, serial_number= ? WHERE id_number= ? AND serial_number= ?", (new_pc_brand, new_serial_number, id_number, serial_number))
    if cursor.rowcount > 0:
        conn.commit()
        conn.close()
        return "Pc's info updated successfully." 
    else:
        return "Update failed. No pc found by the provided id number."
@app.route('/')
def home():
    return render_template("pc_input.html")
@app.route('/belong', methods= ['POST'])
def pc_belong():
    holder_name = request.form.get("holder_name", "").strip()
    id_number = request.form.get("id_number", "").strip()
    pc_brand = request.form.get("pc_brand", "").strip()
    serial_number = request.form.get("serial_number", "").strip()
    four_values = [holder_name, id_number, pc_brand, serial_number]
    try:
        if any (not val for val in four_values):
            return "Error: All fields are required!"
        elif not re.match(r"^\d{4}/\d{2}$", id_number):
            return "Please write your id in the correct format.(0093/17)"
        elif not re.match(r"^[A-Za-z0-9]+$", serial_number):
            return "Serial_number must be a combinations of characters."

    except (TypeError, ValueError) as e:
        return f"Error occured: {e}."
    register = register_pc(holder_name, id_number, serial_number, pc_brand)
    return render_template("pc_input.html", holder_name= holder_name, pc_brand= pc_brand, serial_number= serial_number, register = register)
@app.route('/find', methods= [ 'GET','POST'])
def pc_search():
    if request.method == "GET":
        return render_template("pc_find.html")
    id_number = request.form.get("id_number", "").strip()
    serial_number = request.form.get("serial_number", "").strip()
    search_values = [id_number, serial_number]

    try:
        if any(not val for val in search_values):
            return "Something is empty check your inputs."
        elif not re.match(r"^\d{4}/\d{2}$", id_number):
            return "Invalid id_number. insert your id in this form. e.g, 0024/14. "
        elif not re.match(r"^[A-Za-z0-9]+$", serial_number):
            return "Serial_number must have a combination of characters."
    except (TypeError, ValueError):
        return "Unexpected error occurred."
    
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
    new_pc_brand = ""
    new_serial_number = ""
    found = None
    update = None

    user_action = request.form.get("action")

    if user_action == "verify":
        id_number = request.form.get("id_number", "").strip()
        serial_number = request.form.get("serial_number", "").strip()
        values = [id_number, serial_number]
        try:
            if any(not val for val in values):
                return "Something is empty check your inputs."
            elif not re.match(r"^\d{4}/\d{2}$", id_number):
                return "Invalid id_number. insert your id in this form. e.g, 0024/14. "
            elif not re.match(r"^[A-Za-z0-9]+$", serial_number):
                return "Serial_number must have a combination of characters."
        except (TypeError, ValueError):
            return "Unexpected error occurred."
        found = find_pc(id_number, serial_number)
    elif user_action == "update":
        new_pc_brand = request.form.get("new_pc_brand", "").strip()
        new_serial_number = request.form.get("new_serial_number", "").strip()
        values = [new_pc_brand, new_serial_number]
        try:
            if any(not val for val in values):
                return "Something is empty check your inputs."
            elif not re.match(r"^[A-Za-z0-9]+$", new_serial_number):
                return "Serial_number must have a combination of characters."
        except (TypeError, ValueError):
            return "Unexpected error occurred."
        update = update_pc(id_number, serial_number, new_pc_brand, new_serial_number)
        found = True

    return render_template("pc_update.html", id_number=id_number, new_pc_brand=new_pc_brand, new_serial_number=new_serial_number, found= found, update=update)
if __name__ == "__main__":
    app.run(debug= True)