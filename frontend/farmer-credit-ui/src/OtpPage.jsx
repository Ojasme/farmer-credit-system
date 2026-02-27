import { useState } from "react";
import axios from "axios";

function OtpPage() {
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState(1);

  const sendOtp = async () => {
    try {
      await axios.post("http://localhost:8001/send-otp", { email });
      alert("OTP Sent to your email!");
      setStep(2);
    } catch (error) {
      alert("Failed to send OTP");
    }
  };

  const verifyOtp = async () => {
    try {
      await axios.post("http://localhost:8001/verify-otp", {
        email,
        otp,
      });
      alert("OTP Verified Successfully!");
      window.location.href = "/";  // redirect to existing main page
    } catch (error) {
      alert("Invalid OTP");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h2>Email OTP Verification</h2>

      {step === 1 && (
        <>
          <input
            type="email"
            placeholder="Enter Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <br /><br />
          <button onClick={sendOtp}>Send OTP</button>
        </>
      )}

      {step === 2 && (
        <>
          <input
            type="text"
            placeholder="Enter OTP"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
          />
          <br /><br />
          <button onClick={verifyOtp}>Verify OTP</button>
        </>
      )}
    </div>
  );
}

export default OtpPage;