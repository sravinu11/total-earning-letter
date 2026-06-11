from flask import Flask, render_template, request, Response, session, redirect, url_for
import psycopg2
import paramiko
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-me")

DATABASE_URL = os.getenv("DATABASE_URL")

SFTP_HOST = os.getenv("SFTP_HOST")
SFTP_PORT = int(os.getenv("SFTP_PORT", "22"))
SFTP_USERNAME = os.getenv("SFTP_USERNAME")
SFTP_PASSWORD = os.getenv("SFTP_PASSWORD")

PDF_FOLDER = "/qinedgehep/upload/Letters/EmployeeLetter1"

LOGIN_PASSWORD = "QueSScorptoTaleArning@"


def get_connection():
    return psycopg2.connect(DATABASE_URL)


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        
        if password == LOGIN_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid password. Please try again.")

    # If already authenticated, redirect to dashboard
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    
    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    # Check if authenticated
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    if request.method == "POST":

        ho_id = request.form.get("ho_id", "").strip()

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                ho_id,
                region,
                state,
                town,
                sec_name,
                sec_doj,
                original_doj,
                sec_band,
                contact_no,
                outlet_code,
                outlet_name,
                outlet_category
            FROM total_earning
            WHERE ho_id = %s
        """, (ho_id,))

        row = cur.fetchone()

        cur.close()
        conn.close()

        if row:

            data = {
                "ho_id": row[0],
                "region": row[1],
                "state": row[2],
                "town": row[3],
                "sec_name": row[4],
                "sec_doj": row[5],
                "original_doj": row[6],
                "sec_band": row[7],
                "contact_no": row[8],
                "outlet_code": row[9],
                "outlet_name": row[10],
                "outlet_category": row[11]
            }

            return render_template(
                "result.html",
                data=data
            )

        return render_template(
            "index.html",
            error="HO ID not found"
        )

    return render_template("index.html")

@app.route("/pdf/<ho_id>")
def view_pdf(ho_id):

    transport = paramiko.Transport(
        (SFTP_HOST, SFTP_PORT)
    )

    transport.connect(
        username=SFTP_USERNAME,
        password=SFTP_PASSWORD
    )

    sftp = paramiko.SFTPClient.from_transport(
        transport
    )

    pdf_path = f"{PDF_FOLDER}/{ho_id}.pdf"

    try:

        with sftp.open(pdf_path, "rb") as pdf_file:

            pdf_data = pdf_file.read()

        sftp.close()
        transport.close()

        return Response(
            pdf_data,
            mimetype="application/pdf"
        )

    except Exception as e:

        sftp.close()
        transport.close()

        return f"PDF not found: {str(e)}", 404


if __name__ == "__main__":
    app.run(debug=True)
