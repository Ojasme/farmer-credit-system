import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

// ✅ Separate APIs
const ML_API = "http://localhost:8000";
const OTP_API = "http://localhost:8001";

function App() {
  // 🔐 OTP STATES
  const [isVerified, setIsVerified] = useState(false);
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpStep, setOtpStep] = useState(1);
  const [otpLoading, setOtpLoading] = useState(false);

  // 🌾 ML STATES
  const [form, setForm] = useState({
    loan_amount: "",
    term_in_months: "",
    repayment_interval: "",
    country: "",
    activity: "",
    region: "",
    loan_theme_type: "",
    mpi: "",
    theme_loan_density: "",
    num_female_borrowers: "",
    num_male_borrowers: ""
  });

  const [mappings, setMappings] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // 🔐 Check if already verified


  // 🌾 Load dropdown mappings
  useEffect(() => {
    setMappings({
      repayment_interval: ["monthly", "irregular", "bullet"],
      country: [
        "Philippines", "Kenya", "Cambodia", "Pakistan", "Peru",
        "Colombia", "Ecuador", "Nicaragua", "Tanzania", "Ghana"
      ],
      activity: [
        "Farming", "Livestock", "Poultry", "Agriculture",
        "Dairy", "Crops", "Fisheries", "Forestry",
        "Beekeeping", "Animal Husbandry"
      ],
      region: [
        "Central", "North", "South", "East", "West",
        "Northeast", "Southeast", "Northwest", "Southwest", "Central Region"
      ],
      loan_theme_type: [
        "General", "Agriculture", "Women Entrepreneurs",
        "Underserved", "Rural Inclusion", "Green",
        "Youth", "Vulnerable Populations",
        "Startup", "Micro-enterprise"
      ]
    });
  }, []);

  // 🔐 SEND OTP
  const sendOtp = async () => {
    if (!email) {
      alert("Please enter email");
      return;
    }

    setOtpLoading(true);
    try {
      await axios.post(`${OTP_API}/send-otp`, { email });
      alert("OTP Sent to your email!");
      setOtpStep(2);
    } catch (err) {
      alert("Failed to send OTP");
    }
    setOtpLoading(false);
  };

  // 🔐 VERIFY OTP
  const verifyOtp = async () => {
    if (!otp) {
      alert("Enter OTP");
      return;
    }

    setOtpLoading(true);
    try {
      await axios.post(`${OTP_API}/verify-otp`, { email, otp });
      localStorage.setItem("otp_verified", "true");
      setIsVerified(true);
    } catch (err) {
      alert("Invalid OTP");
    }
    setOtpLoading(false);
  };

  // 🌾 Handle form change
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // 🌾 Submit ML form
  const submitForm = async () => {
    setLoading(true);
    setResult(null);

    try {
      const payload = {
        ...form,
        loan_amount: Number(form.loan_amount),
        term_in_months: Number(form.term_in_months),
        mpi: Number(form.mpi),
        theme_loan_density: Number(form.theme_loan_density),
        num_female_borrowers: Number(form.num_female_borrowers),
        num_male_borrowers: Number(form.num_male_borrowers)
      };

      const response = await axios.post(`${ML_API}/predict`, payload);
      setResult(response.data);

    } catch (err) {
      alert("Backend error: " + err.message);
    }

    setLoading(false);
  };

  // 🔐 OTP SCREEN
  if (!isVerified) {
    return (
      <div className="container">
        <h1>📧 Email OTP Verification</h1>

        {otpStep === 1 && (
          <>
            <input
              type="email"
              placeholder="Enter Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <button onClick={sendOtp} disabled={otpLoading}>
              {otpLoading ? "Sending..." : "Send OTP"}
            </button>
          </>
        )}

        {otpStep === 2 && (
          <>
            <input
              type="text"
              placeholder="Enter OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
            />
            <button onClick={verifyOtp} disabled={otpLoading}>
              {otpLoading ? "Verifying..." : "Verify OTP"}
            </button>
          </>
        )}
      </div>
    );
  }

  // 🌾 MAIN ML APP
  return (
    <div className="container">
      <h1>🌾 Farmer Credit Assessment System</h1>
      <p className="subtitle">
        Credit score based loan approval using Kiva data
      </p>

      <div className="form-grid">
        {Object.keys(form).map((key) => (
          <div className="form-group" key={key}>
            <label>
              {key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
            </label>

            {mappings[key] ? (
              <select name={key} value={form[key]} onChange={handleChange}>
                <option value="">Select</option>
                {mappings[key]?.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            ) : (
              <input
                type="number"
                name={key}
                value={form[key]}
                onChange={handleChange}
                step={key === "mpi" ? "0.01" : "1"}
              />
            )}
          </div>
        ))}
      </div>

      <button onClick={submitForm} disabled={loading}>
        {loading ? "Assessing Credit..." : "Check Credit Eligibility"}
      </button>

      {result && (
        <div className="result">
          <h2>Credit Assessment</h2>
          <p><b>Credit Score:</b> {result.credit_score} / 900</p>
          <p><b>Approval Probability:</b> {result.approval_probability}%</p>
          <p className={
            result.decision.includes("Approved") ? "approved" : "rejected"
          }>
            <b>{result.decision}</b>
          </p>
        </div>
      )}
    </div>
  );
}

export default App;