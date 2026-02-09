import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

function App() {
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

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

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

      const response = await axios.post(
        "http://localhost:8000/predict",
        payload
      );

      setResult(response.data);
    } catch (err) {
      alert("Backend error: " + err.message);
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>🌾 Farmer Credit Assessment System</h1>
      <p className="subtitle">
        Credit score based loan approval using Kiva data
      </p>

      <div className="form-grid">
        {/* All form inputs remain unchanged */}
        {Object.keys(form).map((key) => (
          <div className="form-group" key={key}>
            <label>{key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</label>
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
