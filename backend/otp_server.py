from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import random
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# =========================
# Load environment variables
# =========================
load_dotenv()

app = FastAPI()

# =========================
# CORS Middleware (Fixes frontend error)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React/Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Temporary OTP Store
# =========================
otp_store = {}

# =========================
# SMTP Config
# =========================
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

print("SMTP_SERVER:", SMTP_SERVER)
print("SMTP_PORT:", SMTP_PORT)
print("EMAIL_ADDRESS:", EMAIL_ADDRESS)

# =========================
# Request Models
# =========================
class EmailRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


# =========================
# Email Sending Function
# =========================
def send_email(to_email: str, otp: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = "Your OTP Code"

        body = f"""
Hello,

Your OTP is: {otp}

This OTP will expire in 5 minutes.

Thank you.
        """

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")


# =========================
# Send OTP Endpoint
# =========================
@app.post("/send-otp")
def send_otp(data: EmailRequest):
    otp = str(random.randint(100000, 999999))
    expiry_time = datetime.now() + timedelta(minutes=5)

    otp_store[data.email] = {
        "otp": otp,
        "expires": expiry_time
    }

    send_email(data.email, otp)

    return {"message": "OTP sent successfully"}


# =========================
# Verify OTP Endpoint
# =========================
@app.post("/verify-otp")
def verify_otp(data: OTPVerify):

    if data.email not in otp_store:
        raise HTTPException(status_code=400, detail="OTP not found")

    stored_data = otp_store[data.email]

    # Check expiry
    if datetime.now() > stored_data["expires"]:
        del otp_store[data.email]
        raise HTTPException(status_code=400, detail="OTP expired")

    # Check OTP match
    if stored_data["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    del otp_store[data.email]

    return {"message": "OTP verified successfully"}