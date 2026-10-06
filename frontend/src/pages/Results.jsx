import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import SchemeCard from '../components/SchemeCard';
import ConflictAlert from '../components/ConflictAlert';
import AIConflictDashboard from '../components/AIConflictDashboard';

function Results() {
  const [results, setResults] = useState(null);
  const [profile, setProfile] = useState(null);
  const [resolvedConflicts, setResolvedConflicts] = useState([]);

  const handleConflictResolve = (conflictIndex, schemeName, decision) => {
    setResolvedConflicts(prev => [...prev, { conflictIndex, schemeName, decision }]);
  };

  useEffect(() => {
    // Load results from sessionStorage
    const storedResults = sessionStorage.getItem('analysisResults');
    const storedProfile = sessionStorage.getItem('citizenProfile');

    if (storedResults) {
      setResults(JSON.parse(storedResults));
    }
    if (storedProfile) {
      setProfile(JSON.parse(storedProfile));
    }
  }, []);

  // No results yet
  if (!results) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <div className="bg-white rounded-2xl shadow-lg p-12">
          <div className="text-6xl mb-4">🔍</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-3">
            No Results Yet
          </h2>
          <p className="text-gray-500 mb-6">
            Please fill in your profile details first to check scheme eligibility.
          </p>
          <Link
            to="/analyze"
            className="inline-block bg-primary-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
          >
            Check Eligibility →
          </Link>
        </div>
      </div>
    );
  }

  const eligibleSchemes = results.eligible_schemes || [];
  const conflicts = results.conflicts || [];
  const eligible = eligibleSchemes.filter((s) => s.status === 'Eligible');
  const notEligible = eligibleSchemes.filter((s) => s.status === 'Not Eligible');
  const aiSummary = results.ai_summary || '';
  const aiEnabled = results.ai_enabled || false;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* AI Summary Banner */}
      {aiSummary && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-6 mb-8">
          <div className="flex items-start space-x-3">
            <span className="text-2xl">🤖</span>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <h3 className="font-bold text-purple-800">AI Analysis</h3>
                <span className="text-xs bg-purple-200 text-purple-800 px-2 py-0.5 rounded-full">Powered by Mistral</span>
              </div>
              <p className="text-sm text-gray-700">{aiSummary}</p>
            </div>
          </div>
        </div>
      )}

      {/* AI Enabled Badge */}
      {aiEnabled && !aiSummary && (
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full">🤖 AI Enhanced Results</span>
        </div>
      )}

      {/* Profile Summary */}
      {profile && (
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <h2 className="text-lg font-bold text-gray-800 mb-3">Your Profile</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500">Age</p>
              <p className="text-lg font-bold text-gray-800">{profile.age}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500">Income</p>
              <p className="text-lg font-bold text-gray-800">₹{Number(profile.income).toLocaleString()}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500">State</p>
              <p className="text-lg font-bold text-gray-800">{profile.state}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500">Occupation</p>
              <p className="text-lg font-bold text-gray-800">{profile.occupation}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500">Category</p>
              <p className="text-lg font-bold text-gray-800">{profile.category || 'N/A'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-green-700">{eligible.length}</p>
          <p className="text-sm text-green-600 font-medium">Eligible</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-red-700">{notEligible.length}</p>
          <p className="text-sm text-red-600 font-medium">Not Eligible</p>
        </div>
      </div>

      {/* Conflict Alerts */}
      {conflicts.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">⚠ Conflict Alerts</h2>
          <div className="space-y-3">
            {conflicts.map((conflict, idx) => (
              <ConflictAlert key={idx} conflict={conflict} />
            ))}
          </div>
        </div>
      )}

      {/* AI Conflict Dashboard */}
      <AIConflictDashboard 
        conflicts={conflicts} 
        eligibleSchemes={eligibleSchemes}
        profile={profile}
        onResolve={handleConflictResolve}
      />

      {/* Eligible Schemes */}
      {eligible.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            ✅ Eligible Schemes ({eligible.length})
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {eligible.map((scheme, idx) => (
              <SchemeCard key={idx} scheme={scheme} />
            ))}
          </div>
        </div>
      )}

      {/* Not Eligible Schemes */}
      {notEligible.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            ❌ Not Eligible ({notEligible.length})
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {notEligible.map((scheme, idx) => (
              <SchemeCard key={idx} scheme={scheme} />
            ))}
          </div>
        </div>
      )}

      {/* AI Application Roadmap */}
      {resolvedConflicts.length > 0 && (
        <div className="mb-8 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl p-6">
          <h2 className="text-xl font-bold text-emerald-800 mb-4">
            🗺️ Your AI-Generated Application Roadmap
          </h2>
          <div className="space-y-3">
            {resolvedConflicts
              .filter(r => r.decision === 'apply')
              .map((resolved, idx) => {
                const scheme = eligibleSchemes.find(s => 
                  s.scheme_name.includes(resolved.schemeName) || 
                  resolved.schemeName.includes(s.scheme_name)
                );
                return (
                  <div key={idx} className="flex items-start space-x-3 bg-white rounded-lg p-3 shadow-sm">
                    <span className="flex-shrink-0 w-8 h-8 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center font-bold text-sm">
                      {idx + 1}
                    </span>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800">{resolved.schemeName}</p>
                      {scheme && (
                        <div className="mt-1 text-sm text-gray-600">
                          <p className="text-xs text-gray-500">Documents needed:</p>
                          <p className="truncate">{scheme.documents_required}</p>
                        </div>
                      )}
                    </div>
                    <span className="text-emerald-600 text-sm font-medium">Ready to Apply</span>
                  </div>
                );
              })}
          </div>
          <p className="text-sm text-emerald-700 mt-4 italic">
            💡 Tip: Start with Priority 1 scheme. You can apply for multiple schemes, but resolve any 
            remaining conflicts first.
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="text-center py-8">
        <Link
          to="/analyze"
          className="inline-block bg-primary-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors mr-4"
        >
          Check Another Profile
        </Link>
        <Link
          to="/"
          className="inline-block bg-gray-200 text-gray-700 font-semibold px-6 py-3 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Back to Home
        </Link>
      </div>
    </div>
  );
}

export default Results;
