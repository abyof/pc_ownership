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
def update_pc(id_number, new_pc_brand, new_serial_number):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE pc_data SET pc_brand= ?, serial_number= ? WHERE id_number= ?", (new_pc_brand, new_serial_number, id_number))
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
        return f"Input is requried: {e}."
    register = register_pc(holder_name, id_number, serial_number, pc_brand)
    return render_template("pc_input.html", holder_name= holder_name, pc_brand= pc_brand, serial_number= serial_number, register = register)
if __name__ == "__main__":
    app.run(debug= True)