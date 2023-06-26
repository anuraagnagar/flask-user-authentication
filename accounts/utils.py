from flask import render_template
import uuid

def unique_uid():
    return str(uuid.uuid4())

def page_not_found():
    return render_template('error.html')
