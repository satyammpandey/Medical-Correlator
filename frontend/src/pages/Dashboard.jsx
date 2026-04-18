// frontend/src/pages/Dashboard.jsx
// Main dashboard - entry point

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Activity, Upload, BarChart3, Shield, 
  ChevronRight, Zap, Brain, Heart
} from 'lucide-react';

const API_BASE = 'http://localhost:8000/api/v1';

export default function Dashboard() {
  const navigate = useNavigate();
  const [showNewPatient, setShowNewPatient] = useState(false);
  const [patientForm, setPatientForm] = useState({ name: '', gender: '', date_of_birth: '' });
  const [loading, setLoading] = useState(false);

  const createPatientAndUpload = async () => {
    if (!patientForm.name) {
      toast.error('Please enter patient name');
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/patients`, patientForm);
      const patientId = response.data.id;
      toast.success('Patient created!');
      navigate(`/upload/${patientId}`);
    } catch (err) {
      toast.error('Failed to create patient: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Hero */}
      <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-10 text-white mb-10 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full -translate-y-1/2 translate-x-1/2" />
        </div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="w-10 h-10" />
            <span className="text-sm font-medium bg-white bg-opacity-20 px-3 py-1 rounded-full">
              Patent-Grade AI System
            </span>
          </div>
          <h1 className="text-4xl font-bold mb-4 leading-tight">
            AI Medical Report<br />Correlator & Risk Predictor
          </h1>
          <p className="text-blue-100 text-lg max-w-xl">
            Upload multiple medical reports. Our 7 AI agents analyze ALL of them together 
            to find hidden disease patterns that individual doctors miss.
          </p>
          <div className="flex gap-4 mt-8">
            <button
              onClick={() => setShowNewPatient(true)}
              className="px-8 py-3 bg-white text-blue-600 rounded-xl font-semibold hover:bg-blue-50 transition-all shadow-lg"
            >
              🚀 Start Analysis
            </button>
            <button
              onClick={() => navigate('/demo')}
              className="px-8 py-3 bg-blue-500 text-white rounded-xl font-semibold hover:bg-blue-400 transition-all"
            >
              👁️ View Demo
            </button>
          </div>
        </div>
      </div>

      {/* New Patient Form */}
      {showNewPatient && (
        <div className="bg-white rounded-xl shadow-lg border p-8 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-6">New Patient Profile</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
              <input
                type="text"
                value={patientForm.name}
                onChange={e => setPatientForm({...patientForm, name: e.target.value})}
                placeholder="e.g., John Smith"
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
              <input
                type="date"
                value={patientForm.date_of_birth}
                onChange={e => setPatientForm({...patientForm, date_of_birth: e.target.value})}
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
              <select
                value={patientForm.gender}
                onChange={e => setPatientForm({...patientForm, gender: e.target.value})}
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={createPatientAndUpload}
              disabled={loading}
              className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Continue to Upload →'}
            </button>
            <button
              onClick={() => setShowNewPatient(false)}
              className="px-6 py-2.5 border rounded-lg text-gray-600 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* How It Works */}
      <h2 className="text-2xl font-bold text-gray-800 mb-6">How Our 7-Agent System Works</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        {[
          { emoji: '🔍', title: 'Agent 1', subtitle: 'Document Classifier', desc: 'Identifies each report type automatically' },
          { emoji: '🔬', title: 'Agent 2-3', subtitle: 'Report Analyzers', desc: 'Extracts all values and flags abnormalities' },
          { emoji: '🔗', title: 'Agent 4 ⭐', subtitle: 'Cross-Report Correlator', desc: 'Finds hidden patterns across ALL reports over time' },
          { emoji: '⚠️', title: 'Agent 5', subtitle: 'Risk Predictor', desc: 'Calculates precise disease risk percentages' },
          { emoji: '📄', title: 'Agent 6', subtitle: 'Report Generator', desc: 'Explains findings in simple patient language' },
          { emoji: '💊', title: 'Agent 7', subtitle: 'Recommendation AI', desc: 'Suggests specialists, tests & lifestyle changes' },
          { emoji: '🧬', title: 'RAG Engine', subtitle: 'Medical Knowledge', desc: 'Cross-references against medical literature' },
          { emoji: '🔒', title: 'HIPAA', subtitle: 'Compliance', desc: 'AES-256 encryption, fully secure' },
        ].map((item, idx) => (
          <div key={idx} className="bg-white rounded-xl shadow-sm border p-5 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-3">{item.emoji}</div>
            <p className="font-bold text-gray-800">{item.title}</p>
            <p className="text-sm font-medium text-blue-600 mb-2">{item.subtitle}</p>
            <p className="text-xs text-gray-600">{item.desc}</p>
          </div>
        ))}
      </div>

      {/* Example Alert Preview */}
      <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
        <h3 className="font-bold text-red-800 text-lg mb-3">
          ⚠️ Example: What Our AI Detects (That Doctors Miss)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-semibold text-gray-700 mb-2">📋 Individual Reports Say:</p>
            {[
              'Jan: Glucose 110 → "borderline, monitor"',
              'Apr: Glucose 118 → "slightly elevated"',
              'Jul: HbA1c 6.2% → "pre-diabetic range"',
              'Jul: Eye exam → "mild retinal changes"',
              'Aug: Kidney → "microalbumin slightly up"',
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-2 mb-1 text-gray-600">
                <span>•</span> {item}
              </div>
            ))}
          </div>
          <div>
            <p className="font-semibold text-gray-700 mb-2">🤖 Our AI Sees:</p>
            <div className="bg-red-100 rounded-lg p-4">
              <p className="font-bold text-red-700">HIGH RISK: Type 2 Diabetes Progression</p>
              <p className="text-red-600 mt-1">Confidence: 89.3%</p>
              <ul className="mt-2 space-y-1 text-red-700">
                <li>• Glucose trending up +13.6% over 6 months</li>
                <li>• HbA1c confirms sustained elevation</li>
                <li>• Retinal changes = early diabetic retinopathy</li>
                <li>• Microalbumin = early kidney involvement</li>
              </ul>
              <p className="font-bold text-red-800 mt-2">→ URGENT: See endocrinologist now!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
