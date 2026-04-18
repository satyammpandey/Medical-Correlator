// frontend/src/pages/UploadPage.jsx
// ============================================
// UPLOAD PAGE
// Drag-and-drop interface for uploading medical reports
// ============================================

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import toast from 'react-hot-toast';
import { 
  Upload, FileText, X, CheckCircle, 
  AlertCircle, Loader, Info
} from 'lucide-react';

const API_BASE = 'http://localhost:8000/api/v1';

// Report type icons and labels
const REPORT_TYPES = {
  'Blood Test': '🩸',
  'X-Ray': '🫁',
  'MRI/CT Scan': '🧠',
  'Eye Checkup': '👁️',
  'Kidney Panel': '🫘',
  'Prescription': '💊',
  'Doctor Notes': '📋',
  'ECG': '❤️',
};

export default function UploadPage() {
  const { patientId } = useParams();
  const navigate = useNavigate();
  
  const [files, setFiles] = useState([]);
  const [patientInfo, setPatientInfo] = useState({
    name: '',
    age: '',
    gender: 'unknown'
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');

  // ---- File Drop Handler ----
  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      status: 'ready',  // ready, uploading, done, error
    }));
    setFiles(prev => [...prev, ...newFiles]);
    toast.success(`Added ${acceptedFiles.length} file(s)!`);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff'],
    },
    maxFiles: 20,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  // Remove a file
  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  // ---- Start Analysis ----
  const startAnalysis = async () => {
    if (files.length === 0) {
      toast.error('Please upload at least one medical report!');
      return;
    }
    if (!patientInfo.name) {
      toast.error('Please enter the patient name!');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisProgress(5);
    setCurrentStep('Uploading files...');

    try {
      // ---- Build form data ----
      const formData = new FormData();
      files.forEach(f => formData.append('files', f.file));
      formData.append('patient_name', patientInfo.name);
      if (patientInfo.age) formData.append('patient_age', patientInfo.age);
      formData.append('patient_gender', patientInfo.gender);

      // ---- Upload and start analysis ----
      const response = await axios.post(
        `${API_BASE}/patients/${patientId}/upload-reports`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      const { job_id } = response.data;
      toast.success('Files uploaded! AI analysis starting...');

      // ---- Poll for completion ----
      await pollForCompletion(job_id);

    } catch (error) {
      console.error('Upload failed:', error);
      toast.error(`Upload failed: ${error.response?.data?.detail || error.message}`);
      setIsAnalyzing(false);
    }
  };

  // Poll every 3 seconds until complete
  const pollForCompletion = async (jobId) => {
    const steps = [
      { progress: 15, message: '🔍 Agent 1: Classifying your reports...' },
      { progress: 35, message: '🔬 Agent 2: Analyzing lab values...' },
      { progress: 55, message: '🔗 Agent 4: Finding patterns across reports...' },
      { progress: 70, message: '⚠️ Agent 5: Calculating disease risks...' },
      { progress: 85, message: '📄 Agent 6: Writing your health report...' },
      { progress: 95, message: '💊 Agent 7: Generating recommendations...' },
    ];
    
    let stepIndex = 0;

    const pollInterval = setInterval(async () => {
      try {
        // Show progress steps
        if (stepIndex < steps.length) {
          setAnalysisProgress(steps[stepIndex].progress);
          setCurrentStep(steps[stepIndex].message);
          stepIndex++;
        }

        // Check actual status
        const statusResponse = await axios.get(`${API_BASE}/status/${jobId}`);
        const { status } = statusResponse.data;

        if (status === 'COMPLETE') {
          clearInterval(pollInterval);
          setAnalysisProgress(100);
          setCurrentStep('✅ Analysis complete!');
          
          setTimeout(() => {
            toast.success('🎉 Analysis complete! Viewing results...');
            navigate(`/results/${jobId}`);
          }, 1000);
        } else if (status === 'FAILED') {
          clearInterval(pollInterval);
          toast.error('Analysis failed. Please try again.');
          setIsAnalyzing(false);
        }

      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 3000);
  };

  // ---- FORMAT FILE SIZE ----
  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Upload Medical Reports
        </h1>
        <p className="text-gray-600 mt-2">
          Upload multiple reports — our AI will find patterns across ALL of them together.
        </p>
      </div>

      {/* Patient Info */}
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Patient Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Patient Name *
            </label>
            <input
              type="text"
              value={patientInfo.name}
              onChange={e => setPatientInfo({...patientInfo, name: e.target.value})}
              placeholder="Full name"
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
            <input
              type="number"
              value={patientInfo.age}
              onChange={e => setPatientInfo({...patientInfo, age: e.target.value})}
              placeholder="Age in years"
              min="1" max="120"
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
            <select
              value={patientInfo.gender}
              onChange={e => setPatientInfo({...patientInfo, gender: e.target.value})}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="unknown">Prefer not to say</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tips Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 flex gap-3">
        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-blue-800">Tips for best results:</p>
          <ul className="text-sm text-blue-700 mt-1 space-y-1">
            <li>• Upload reports from <strong>different time periods</strong> — the AI finds patterns over time</li>
            <li>• Include blood tests, eye exams, kidney panels together for diabetes detection</li>
            <li>• More reports = better correlation = more accurate risk prediction</li>
            <li>• Both PDFs and scanned images (JPG/PNG) work</li>
          </ul>
        </div>
      </div>

      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all
          ${isDragActive 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-300 bg-white hover:border-blue-300 hover:bg-blue-50'
          }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-lg font-medium text-gray-700">
          {isDragActive ? 'Drop files here!' : 'Drag & drop medical reports here'}
        </p>
        <p className="text-sm text-gray-500 mt-2">
          or <span className="text-blue-600 font-medium">click to browse</span>
        </p>
        <p className="text-xs text-gray-400 mt-3">
          PDF, JPG, PNG, TIFF • Max 50MB per file • Up to 20 files
        </p>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6 bg-white rounded-xl shadow-sm border p-6">
          <h3 className="font-semibold text-gray-800 mb-4">
            {files.length} file(s) ready for analysis
          </h3>
          <div className="space-y-3">
            {files.map(fileItem => (
              <div key={fileItem.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <FileText className="w-5 h-5 text-blue-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{fileItem.name}</p>
                  <p className="text-xs text-gray-500">{formatSize(fileItem.size)}</p>
                </div>
                <button
                  onClick={() => removeFile(fileItem.id)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis Progress */}
      {isAnalyzing && (
        <div className="mt-6 bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center gap-3 mb-4">
            <Loader className="w-5 h-5 text-blue-600 animate-spin" />
            <span className="font-medium text-gray-800">AI Analysis in Progress...</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-1000"
              style={{ width: `${analysisProgress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600">{currentStep}</p>
          <p className="text-xs text-gray-400 mt-2">
            This takes 1-3 minutes depending on number of reports
          </p>
        </div>
      )}

      {/* Start Button */}
      {!isAnalyzing && (
        <div className="mt-6 flex justify-end">
          <button
            onClick={startAnalysis}
            disabled={files.length === 0 || !patientInfo.name}
            className={`px-8 py-3 rounded-xl font-semibold text-white transition-all
              ${files.length === 0 || !patientInfo.name
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 shadow-lg hover:shadow-xl'
              }`}
          >
            🚀 Start AI Analysis ({files.length} files)
          </button>
        </div>
      )}
    </div>
  );
}
