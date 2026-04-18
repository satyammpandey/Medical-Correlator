// frontend/src/pages/ResultsPage.jsx
// ============================================
// RESULTS PAGE
// Shows the complete AI analysis results
// ============================================

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  AlertTriangle, CheckCircle, TrendingUp, TrendingDown,
  Heart, Activity, FileText, Star, ChevronDown, ChevronUp,
  Download, Share2, ArrowLeft
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';

const API_BASE = 'http://localhost:8000/api/v1';

// Traffic light colors
const TRAFFIC_COLORS = {
  GREEN: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300', emoji: '🟢' },
  YELLOW: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300', emoji: '🟡' },
  RED: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300', emoji: '🔴' },
};

const RISK_COLORS = {
  LOW: 'text-green-600',
  MODERATE: 'text-yellow-600',
  HIGH: 'text-orange-600',
  CRITICAL: 'text-red-600',
};

export default function ResultsPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedRisk, setExpandedRisk] = useState(null);

  useEffect(() => {
    fetchResults();
  }, [jobId]);

  const fetchResults = async () => {
    try {
      const response = await axios.get(`${API_BASE}/status/${jobId}`);
      if (response.data.result) {
        setResults(response.data.result);
      }
    } catch (error) {
      console.error('Failed to fetch results:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-800">Results not found</h2>
        <p className="text-gray-600 mt-2">The analysis may still be running. Please wait and refresh.</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>
    );
  }

  const patientReport = results.patient_report || {};
  const riskPrediction = results.risk_prediction || {};
  const recommendations = results.recommendations || {};
  const correlation = results.correlation || {};

  const trafficLight = patientReport.traffic_light_status || 'YELLOW';
  const trafficColors = TRAFFIC_COLORS[trafficLight] || TRAFFIC_COLORS.YELLOW;

  return (
    <div className="max-w-5xl mx-auto">
      {/* Back button */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </button>

      {/* ============ HERO SECTION - Health Score ============ */}
      <div className={`rounded-2xl border-2 p-8 mb-8 ${trafficColors.bg} ${trafficColors.border}`}>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl">{trafficColors.emoji}</span>
              <h1 className={`text-2xl font-bold ${trafficColors.text}`}>
                {riskPrediction.overall_risk_level} RISK DETECTED
              </h1>
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mt-3">
              {patientReport.headline}
            </h2>
          </div>
          {/* Health Score Circle */}
          <div className="text-center">
            <div className="relative w-24 h-24">
              <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" strokeWidth="10" />
                <circle
                  cx="50" cy="50" r="40" fill="none"
                  stroke={trafficLight === 'GREEN' ? '#16a34a' : trafficLight === 'RED' ? '#dc2626' : '#d97706'}
                  strokeWidth="10"
                  strokeDasharray={`${(patientReport.health_score || 50) * 2.51} 251`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-800">
                  {patientReport.health_score || 50}
                </span>
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-1">Health Score</p>
          </div>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-opacity-50" style={{borderColor: 'rgba(0,0,0,0.1)'}}>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-800">{results.reports_analyzed || 0}</p>
            <p className="text-sm text-gray-600">Reports Analyzed</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-800">{results.patterns_found || 0}</p>
            <p className="text-sm text-gray-600">Patterns Found</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-800">
              {riskPrediction.disease_risks?.length || 0}
            </p>
            <p className="text-sm text-gray-600">Risks Identified</p>
          </div>
        </div>
      </div>

      {/* ============ TAB NAVIGATION ============ */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-8">
        {[
          { id: 'overview', label: '📋 Overview' },
          { id: 'risks', label: '⚠️ Risk Details' },
          { id: 'trends', label: '📈 Trends' },
          { id: 'recommendations', label: '💊 What To Do' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all
              ${activeTab === tab.id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ============ TAB CONTENT ============ */}

      {/* OVERVIEW TAB */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Patient-friendly explanation */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              What We Found
            </h3>
            <p className="text-gray-700 leading-relaxed">
              {patientReport.what_we_found}
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-orange-500" />
              What This Means
            </h3>
            <p className="text-gray-700 leading-relaxed">
              {patientReport.what_this_means}
            </p>
          </div>

          {patientReport.good_news && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-green-800 mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                Good News
              </h3>
              <p className="text-green-700">{patientReport.good_news}</p>
            </div>
          )}

          {/* AI Disclaimer */}
          <div className="bg-gray-50 border rounded-xl p-4 text-sm text-gray-500">
            <strong>⚠️ Medical Disclaimer:</strong> This AI analysis is for informational purposes only 
            and should not replace professional medical advice. Always consult a qualified healthcare 
            provider before making any medical decisions.
          </div>
        </div>
      )}

      {/* RISKS TAB */}
      {activeTab === 'risks' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Disease Risk Assessment</h3>
          
          {riskPrediction.disease_risks?.map((risk, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-sm border overflow-hidden">
              {/* Risk Header */}
              <div
                className="p-6 cursor-pointer"
                onClick={() => setExpandedRisk(expandedRisk === idx ? null : idx)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-center min-w-[70px]">
                      <div className={`text-3xl font-bold ${RISK_COLORS[risk.risk_level]}`}>
                        {risk.risk_percentage?.toFixed(1)}%
                      </div>
                      <div className={`text-xs font-medium ${RISK_COLORS[risk.risk_level]}`}>
                        {risk.risk_level} RISK
                      </div>
                    </div>
                    <div>
                      <h4 className="text-lg font-semibold text-gray-800">{risk.disease_name}</h4>
                      <p className="text-sm text-gray-500">
                        Confidence: {risk.confidence?.toFixed(0)}% | ICD-10: {risk.icd10_code}
                      </p>
                    </div>
                  </div>
                  {expandedRisk === idx ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>

                {/* Risk Bar */}
                <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      risk.risk_level === 'CRITICAL' ? 'bg-red-600' :
                      risk.risk_level === 'HIGH' ? 'bg-orange-500' :
                      risk.risk_level === 'MODERATE' ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${risk.risk_percentage}%` }}
                  />
                </div>
              </div>

              {/* Expanded Details */}
              {expandedRisk === idx && (
                <div className="px-6 pb-6 border-t bg-gray-50">
                  <div className="pt-4">
                    <h5 className="font-semibold text-gray-700 mb-3">Evidence (from your reports):</h5>
                    <ul className="space-y-2">
                      {risk.key_factors?.map((factor, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                          <span className="text-orange-500 mt-0.5">•</span>
                          {factor}
                        </li>
                      ))}
                    </ul>

                    {risk.reasoning && (
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <p className="text-sm font-medium text-blue-800 mb-1">AI Reasoning:</p>
                        <p className="text-sm text-blue-700">{risk.reasoning}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* TRENDS TAB */}
      {activeTab === 'trends' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-800">Value Trends Over Time</h3>

          {correlation.trends?.filter(t => t.is_concerning).map((trend, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="font-semibold text-gray-800 capitalize">
                    {trend.test_name?.replace(/_/g, ' ')}
                  </h4>
                  <p className="text-sm text-gray-500">
                    {trend.first_date} → {trend.last_date}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {trend.trend_direction === 'INCREASING' ? (
                    <TrendingUp className="w-5 h-5 text-red-500" />
                  ) : (
                    <TrendingDown className="w-5 h-5 text-green-500" />
                  )}
                  <span className={`font-bold ${trend.change_percent > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {trend.change_percent > 0 ? '+' : ''}{trend.change_percent}%
                  </span>
                </div>
              </div>

              {/* Mini chart */}
              {trend.all_values?.length > 1 && (
                <ResponsiveContainer width="100%" height={120}>
                  <LineChart data={trend.all_values.map(([date, val]) => ({ date, value: val }))}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.5} />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Line
                      type="monotone" dataKey="value"
                      stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          ))}

          {!correlation.trends?.some(t => t.is_concerning) && (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="w-10 h-10 text-green-400 mx-auto mb-3" />
              <p>No concerning trends detected across your reports.</p>
            </div>
          )}
        </div>
      )}

      {/* RECOMMENDATIONS TAB */}
      {activeTab === 'recommendations' && (
        <div className="space-y-6">
          {/* Priority Alert */}
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">
            <h3 className="font-bold text-red-800 text-lg">
              🚨 {recommendations.overall_priority}
            </h3>
          </div>

          {/* Specialist Referrals */}
          {recommendations.specialist_referrals?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                👨‍⚕️ See These Specialists
              </h3>
              <div className="space-y-3">
                {recommendations.specialist_referrals.map((ref, idx) => (
                  <div key={idx} className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
                    <div className="bg-blue-100 rounded-full p-2 flex-shrink-0">
                      <span className="text-lg">👨‍⚕️</span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800">{ref.specialist}</p>
                      <p className="text-sm text-gray-600">{ref.reason}</p>
                      <div className="flex gap-3 mt-2">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          ref.urgency === 'URGENT' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                        }`}>
                          {ref.urgency}
                        </span>
                        <span className="text-xs text-gray-500">See within: {ref.see_within}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Lifestyle Changes */}
          {recommendations.lifestyle_changes?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                🏃 Lifestyle Changes
              </h3>
              <div className="space-y-4">
                {recommendations.lifestyle_changes.map((change, idx) => (
                  <div key={idx} className="border-l-4 border-green-400 pl-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-green-700 bg-green-100 px-2 py-0.5 rounded">
                        {change.category}
                      </span>
                      <span className={`text-xs ${
                        change.difficulty === 'EASY' ? 'text-green-600' : 
                        change.difficulty === 'MODERATE' ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {change.difficulty}
                      </span>
                    </div>
                    <p className="font-medium text-gray-800 mt-1">{change.change}</p>
                    <p className="text-sm text-gray-600">{change.why}</p>
                    {change.how_to_start && (
                      <p className="text-sm text-blue-700 mt-1">
                        <strong>Start today:</strong> {change.how_to_start}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Monitoring Schedule */}
          {recommendations.monitoring_schedule?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                📅 Monitoring Schedule
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {recommendations.monitoring_schedule.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <span className="text-xl">📋</span>
                    <div>
                      <p className="font-medium text-gray-800 text-sm">{item.test}</p>
                      <p className="text-xs text-gray-600">{item.frequency}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <div className="text-xs text-gray-400 p-4 bg-gray-50 rounded-lg">
            {recommendations.disclaimer}
          </div>
        </div>
      )}

      {/* Download Report */}
      <div className="mt-8 flex gap-4 justify-end">
        <button
          onClick={() => window.print()}
          className="flex items-center gap-2 px-6 py-3 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50"
        >
          <Download className="w-4 h-4" />
          Print Report
        </button>
        <button
          onClick={() => {
            navigator.clipboard.writeText(window.location.href);
            alert('Link copied!');
          }}
          className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700"
        >
          <Share2 className="w-4 h-4" />
          Share with Doctor
        </button>
      </div>
    </div>
  );
}
