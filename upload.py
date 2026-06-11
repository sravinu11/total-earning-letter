import psycopg2

# 🔹 UPDATE THESE
CSV_FILE = r"C:\xampp\htdocs\Total Earning Letter\masterdata.csv"
DATABASE_URL = (
    "postgresql://neondb_owner:npg_V5PaQdjhX2It@"
    "ep-raspy-dream-a1pa5xzv-pooler.ap-southeast-1.aws.neon.tech/"
    "neondb?sslmode=require"
)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Optional: clean table
cur.execute("TRUNCATE TABLE total_earning;")

with open(CSV_FILE, "r", encoding="utf-8") as f:
    cur.copy_expert(
        """
        COPY total_earning (
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
        )
        FROM STDIN
        WITH (FORMAT CSV, HEADER TRUE)
        """,
        f
    )

conn.commit()
cur.close()
conn.close()

print("✅ CSV uploaded successfully to Neon")
