// frontend/src/pages/DemoPage.jsx
// Shows a demo analysis without uploading real files

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

export default function DemoPage() {
  const [demoData, setDemoData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDemo();
  }, []);

  const fetchDemo = async () => {
    try {
      const response = await axios.get(`${API_BASE}/demo/sample-analysis`);
      setDemoData(response.data);
    } catch (err) {
      // Use hardcoded data if API not available
      setDemoData(SAMPLE_DATA);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading demo...</div>;
  }

  const report = demoData?.patient_report || {};
  const risks = demoData?.risk_prediction?.disease_risks || [];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-8">
        <p className="text-blue-800 font-medium">
          🎯 Demo Mode: This shows what our AI finds when analyzing the diabetes progression example.
          The real system works with your actual uploaded reports.
        </p>
      </div>

      {/* Alert Banner */}
      <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-8 mb-8">
        <div className="flex items-start gap-4">
          <span className="text-4xl">⚠️</span>
          <div>
            <h2 className="text-2xl font-bold text-red-800">
              HIGH RISK: Type 2 Diabetes Progression Detected
            </h2>
            <p className="text-red-600 mt-1">Confidence: 89.3% | Based on 5 reports over 8 months</p>
            <p className="text-gray-700 mt-4 text-lg leading-relaxed">
              {report.headline || "Your medical reports reveal a hidden pattern when analyzed together."}
            </p>
          </div>
        </div>
      </div>

      {/* Timeline of Reports */}
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-6">📅 Report Timeline (Individual View)</h3>
        <div className="space-y-4">
          {[
            { date: 'Jan 2024', type: '🩸 Blood Test', finding: 'Fasting Glucose: 110 mg/dL', doctorNote: '"Borderline — monitor"', status: 'yellow' },
            { date: 'Apr 2024', type: '🩸 Blood Test', finding: 'Fasting Glucose: 118 mg/dL', doctorNote: '"Slightly elevated — recheck"', status: 'yellow' },
            { date: 'Jul 2024', type: '🩸 Blood Test', finding: 'HbA1c: 6.2% | Glucose: 125 mg/dL', doctorNote: '"Pre-diabetic range"', status: 'orange' },
            { date: 'Jul 2024', type: '👁️ Eye Exam', finding: 'Mild retinal changes noted', doctorNote: '"Routine follow-up in 1 year"', status: 'orange' },
            { date: 'Aug 2024', type: '🫘 Kidney Panel', finding: 'Microalbumin: 45 mg/g (slightly elevated)', doctorNote: '"Repeat in 6 months"', status: 'orange' },
          ].map((item, idx) => (
            <div key={idx} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className={`w-3 h-3 rounded-full mt-1 ${
                  item.status === 'orange' ? 'bg-orange-400' : 'bg-yellow-400'
                }`} />
                {idx < 4 && <div className="w-0.5 h-full bg-gray-200 mt-1" />}
              </div>
              <div className="pb-4 flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-sm font-medium text-gray-500">{item.date}</span>
                  <span className="text-sm">{item.type}</span>
                </div>
                <p className="font-medium text-gray-800">{item.finding}</p>
                <p className="text-sm text-gray-500 italic">Doctor said: {item.doctorNote}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Cross-Report Analysis */}
      <div className="bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200 rounded-xl p-6 mb-6">
        <h3 className="text-lg font-semibold text-red-800 mb-4">
          🤖 What Our AI Sees (Across ALL Reports)
        </h3>
        <div className="space-y-3">
          {[
            { connection: 'Glucose: 110 → 118 → 125 mg/dL over 6 months', insight: '+13.6% upward trend = insulin resistance developing', severity: 'HIGH' },
            { connection: 'HbA1c 6.2% confirms sustained glucose elevation', insight: 'Not just a one-time spike — 3 months of high sugar', severity: 'HIGH' },
            { connection: 'Retinal changes + High glucose (same period)', insight: 'Early diabetic retinopathy — usually takes years to appear', severity: 'HIGH' },
            { connection: 'Microalbumin elevated + Rising glucose', insight: 'Early kidney damage from high blood sugar = diabetic nephropathy stage 1', severity: 'CRITICAL' },
          ].map((item, idx) => (
            <div key={idx} className="bg-white rounded-lg p-4 border border-red-100">
              <div className="flex items-start gap-3">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 mt-0.5 ${
                  item.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                }`}>
                  {item.severity}
                </span>
                <div>
                  <p className="text-sm font-medium text-gray-800">{item.connection}</p>
                  <p className="text-sm text-gray-600 mt-0.5">→ {item.insight}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-4 bg-red-100 rounded-lg">
          <p className="font-bold text-red-800">
            🎯 CONCLUSION: Type 2 Diabetes Progression (89.3% confidence)
          </p>
          <p className="text-red-700 text-sm mt-1">
            Urgent endocrinologist consultation needed. Early intervention can prevent full diabetes 
            and reverse pre-diabetic state in 60% of cases.
          </p>
        </div>
      </div>

      {/* What Individual Doctors Missed */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-gray-50 rounded-xl p-6 border">
          <h4 className="font-semibold text-gray-700 mb-3">❌ Without Our AI</h4>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• 5 separate "borderline" notes</li>
            <li>• No connection between reports</li>
            <li>• Eye changes seen as unrelated</li>
            <li>• Kidney finding dismissed</li>
            <li>• Disease continues progressing</li>
            <li className="text-red-600 font-medium">• Diabetes diagnosed 2-3 years later when damage is done</li>
          </ul>
        </div>
        <div className="bg-green-50 rounded-xl p-6 border border-green-200">
          <h4 className="font-semibold text-green-700 mb-3">✅ With Our AI</h4>
          <ul className="space-y-2 text-sm text-green-700">
            <li>• Patterns across all 5 reports found</li>
            <li>• 89.3% risk alert generated</li>
            <li>• Eye + Blood + Kidney connected</li>
            <li>• 8-month trend detected early</li>
            <li>• Specialist referral suggested</li>
            <li className="font-medium">• Intervention BEFORE full diabetes</li>
          </ul>
        </div>
      </div>

      <div className="text-center">
        <a
          href="/"
          className="inline-block px-10 py-4 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 text-lg"
        >
          🚀 Try With Your Own Reports
        </a>
      </div>
    </div>
  );
}

const SAMPLE_DATA = {
  patient_report: {
    headline: "⚠️ Urgent: 5 of your reports together reveal high risk of Type 2 Diabetes progression",
  },
  risk_prediction: {
    disease_risks: [
      { disease_name: "Type 2 Diabetes", risk_percentage: 89.3, risk_level: "HIGH" }
    ]
  }
};
