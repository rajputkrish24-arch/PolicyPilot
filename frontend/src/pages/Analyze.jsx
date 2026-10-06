import React from 'react';
import EligibilityForm from '../components/EligibilityForm';

function Analyze() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Scheme Eligibility Checker
        </h1>
        <p className="text-gray-500">
          Fill in your details below and we'll find government schemes you're eligible for.
        </p>
      </div>

      <EligibilityForm />

      {/* Info Cards */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-blue-50 rounded-lg p-5 border border-blue-100">
          <h3 className="font-semibold text-blue-800 mb-2">🔒 Privacy First</h3>
          <p className="text-sm text-blue-600">
            Your data is processed locally and never stored on external servers.
          </p>
        </div>
        <div className="bg-green-50 rounded-lg p-5 border border-green-100">
          <h3 className="font-semibold text-green-800 mb-2">🤖 AI-Powered</h3>
          <p className="text-sm text-green-600">
            Uses RAG + rule-based engine for accurate eligibility matching.
          </p>
        </div>
        <div className="bg-purple-50 rounded-lg p-5 border border-purple-100">
          <h3 className="font-semibold text-purple-800 mb-2">⚡ Conflict Detection</h3>
          <p className="text-sm text-purple-600">
            Automatically detects conflicts between scheme eligibility rules.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Analyze;
