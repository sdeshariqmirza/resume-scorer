import { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resumes, setResumes] = useState([]);
const [resumesLoading, setResumesLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "https://resume-scorer-backend.onrender.com/score-resume",
        formData,
      );
      setResult(response.data);
    } catch (err) {
      setError("Kuch Galat Hua, Dobara Try Karo");
    }
    setLoading(false);
  };

  const handleDownloadReport = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const response = await axios.post(
      "https://resume-scorer-backend.onrender.com/generate-report",
      formData,
      { responseType: "blob" },
    );
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "resume_report.pdf");
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const handleGenerateResumes = async () => {
    if (!file) return;
    setResumesLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    const response = await axios.post(
      "https://resume-scorer-backend.onrender.com/generate-resumes",
      formData
    );
    setResumes(response.data.resumes);
    setResumesLoading(false);
  };

  const scoreColor = (score) => {
    if (score >= 80) return "text-green-500";
    if (score >= 60) return "text-yellow-500";
    return "text-red-500";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-700 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-2">📄</div>
          <h1 className="text-3xl font-bold text-indigo-900 mb-1">
            AI Resume Scorer
          </h1>
          <p className="text-gray-500 text-sm">
            Apna resume upload karo, ATS score aur suggestions pao
          </p>
        </div>

        {/* Upload Box */}
        <label
          htmlFor="fileInput"
          className="cursor-pointer block border-2 border-dashed border-purple-300 rounded-xl p-8 text-center bg-purple-50 hover:bg-purple-100 transition mb-4"
        >
          <input
            type="file"
            accept=".pdf"
            id="fileInput"
            className="hidden"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <div className="text-3xl mb-2"></div>
          <div className="text-purple-700 font-semibold text-sm">
            {file ? file.name : "Click karke PDF choose karo"}
          </div>
          <div className="text-gray-400 text-xs mt-1">
            Sirf PDF format supported hai
          </div>
        </label>

        {/* Button */}
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className={`w-full py-3 rounded-xl text-white font-semibold text-base transition mb-4 ${
            !file || loading
              ? "bg-gray-300 cursor-not-allowed"
              : "bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 cursor-pointer"
          }`}
        >
          {loading ? " Analyzing your resume..." : " Score My Resume"}
        </button>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-red-600 text-sm mb-4">
            ❌ {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div>
            {/* Score Card */}
            <div className="bg-gray-50 rounded-2xl p-6 text-center mb-5">
              <div className="text-gray-400 text-sm mb-1">ATS Score</div>
              <div
                className={`text-6xl font-bold ${scoreColor(result.ats_score)}`}
              >
                {result.ats_score}
              </div>
              <div className="text-gray-400 text-sm">/100</div>
            </div>

            {/* Strengths */}
            <div className="mb-4">
              <h3 className="text-indigo-900 font-semibold text-base mb-2">
                ✅ Strengths
              </h3>
              {result.strengths.map((s, i) => (
                <div
                  key={i}
                  className="bg-green-50 border border-green-200 rounded-lg px-4 py-2 mb-2 text-green-800 text-sm"
                >
                  {s}
                </div>
              ))}
            </div>

            {/* Improvements */}
            <div className="mb-4">
              <h3 className="text-indigo-900 font-semibold text-base mb-2">
                💡 Improvements
              </h3>
              {result.improvements.map((imp, i) => (
                <div
                  key={i}
                  className="bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-2 mb-2 text-yellow-800 text-sm"
                >
                  {imp}
                </div>
              ))}
            </div>

            {/* Missing Keywords */}
            <div>
              <h3 className="text-indigo-900 font-semibold text-base mb-2">
                🔍 Missing Keywords
              </h3>
              <div className="flex flex-wrap gap-2">
                {result.missing_keywords.map((k, i) => (
                  <span
                    key={i}
                    className="bg-purple-100 text-purple-700 px-4 py-1 rounded-full text-sm font-medium"
                  >
                    {k}
                  </span>
                ))}
              </div>
            </div>
            <button
              onClick={handleDownloadReport}
              className="mt-6 w-full py-3 rounded-xl text-white font-semibold text-base bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 cursor-pointer"
            >
               Download PDF Report
            </button>
            <div className="mt-6">
  <button
    onClick={handleGenerateResumes}
    disabled={resumesLoading}
    className={`w-full py-3 rounded-xl text-white font-semibold text-base cursor-pointer ${
      resumesLoading
        ? "bg-gray-300 cursor-not-allowed"
        : "bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700"
    }`}
  >
    {resumesLoading ? "⏳ Generating Resumes..." : "✨ Generate ATS-Friendly Resumes"}
  </button>

  {resumes.length > 0 && (
    <div className="mt-6">
      <h3 className="text-indigo-900 font-semibold text-base mb-4">
        ✨ Your ATS-Friendly Resumes
      </h3>
      <div className="grid grid-cols-1 gap-4">
        {resumes.map((resume, i) => (
          <div key={i} className="relative border border-purple-200 rounded-xl overflow-hidden">
            
            {/* Resume Title */}
            <div className="bg-purple-50 px-4 py-3 flex items-center justify-between">
              <span className="text-purple-800 font-semibold text-sm">
                {i + 1}. {resume.title}
              </span>
              <span className="text-xs bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full font-medium">
                🔒 Locked
              </span>
            </div>

            {/* Blurred Content */}
            <div className="relative">
              <div className="p-4 text-sm text-gray-700 whitespace-pre-wrap blur-sm select-none pointer-events-none h-48 overflow-hidden">
                {resume.content}
              </div>

              {/* Lock Overlay */}
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/60">
                <div className="text-3xl mb-2">🔒</div>
                <p className="text-gray-700 font-semibold text-sm mb-3">
                  Unlock karo ₹149 mein
                </p>
                <button className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-2 rounded-xl text-sm font-semibold hover:from-indigo-600 hover:to-purple-700 cursor-pointer">
                  💳 Pay ₹149 & Download
                </button>
              </div>
            </div>

          </div>
        ))}
      </div>
    </div>
  )}
</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
