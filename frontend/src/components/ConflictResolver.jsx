import React, { useState } from 'react';

function ConflictResolver({ conflicts, eligibleSchemes, onResolve }) {
  const [resolvedDecisions, setResolvedDecisions] = useState({});
  const [showComparison, setShowComparison] = useState(null);

  if (!conflicts || conflicts.length === 0) return null;

  // Filter real conflicts (not just notices)
  const realConflicts = conflicts.filter(
    c => c.conflict && c.conflict_type !== 'none'
  );

  if (realConflicts.length === 0) return null;

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High': return 'bg-red-100 text-red-800 border-red-300';
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'High': return '🚨';
      case 'Medium': return '⚡';
      case 'Low': return '✅';
      default: return 'ℹ️';
    }
  };

  const handleDecision = (conflictIndex, schemeName, decision) => {
    setResolvedDecisions(prev => ({
      ...prev,
      [`${conflictIndex}-${schemeName}`]: decision
    }));
    
    if (onResolve) {
      onResolve(conflictIndex, schemeName, decision);
    }
  };

  const compareSchemes = (schemes) => {
    const schemeDetails = eligibleSchemes.filter(s => 
      schemes.some(name => s.scheme_name.includes(name) || name.includes(s.scheme_name))
    );
    setShowComparison(schemeDetails);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden mb-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">🤖</span>
          <div>
            <h2 className="font-bold text-lg">AI Conflict Resolution Assistant</h2>
            <p className="text-sm text-indigo-100">
              {realConflicts.length} conflict{realConflicts.length > 1 ? 's' : ''} detected • 
              Let AI help you decide
            </p>
          </div>
        </div>
      </div>

      {/* Conflicts List */}
      <div className="divide-y divide-gray-100">
        {realConflicts.map((conflict, idx) => (
          <div key={idx} className="p-4 hover:bg-gray-50 transition-colors">
            {/* Conflict Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                <span className="text-xl">{getPriorityIcon(conflict.priority)}</span>
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getPriorityColor(conflict.priority)}`}>
                  {conflict.priority} Priority
                </span>
                {conflict.ai_enhanced && (
                  <span className="px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-700">
                    🤖 AI Analyzed
                  </span>
                )}
              </div>
              <button
                onClick={() => compareSchemes(conflict.schemes_involved)}
                className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
              >
                Compare Schemes →
              </button>
            </div>

            {/* Conflict Message */}
            <p className="text-gray-700 mb-3">{conflict.message}</p>

            {/* AI Explanation */}
            {conflict.ai_explanation && (
              <div className="mb-3 p-3 bg-purple-50 rounded-lg border-l-4 border-purple-400">
                <p className="text-sm font-semibold text-purple-800 mb-1">🤖 AI Analysis:</p>
                <p className="text-sm text-gray-700">{conflict.ai_explanation}</p>
              </div>
            )}

            {/* AI Recommendation */}
            {conflict.ai_recommendation && (
              <div className="mb-4 p-3 bg-green-50 rounded-lg border-l-4 border-green-400">
                <p className="text-sm font-semibold text-green-800 mb-1">💡 Recommended Action:</p>
                <p className="text-sm text-gray-700">{conflict.ai_recommendation}</p>
              </div>
            )}

            {/* Decision Buttons */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-600">Choose which scheme to apply for:</p>
              <div className="flex flex-wrap gap-2">
                {conflict.schemes_involved.map((scheme, sIdx) => {
                  const decisionKey = `${idx}-${scheme}`;
                  const decision = resolvedDecisions[decisionKey];
                  
                  return (
                    <div key={sIdx} className="flex items-center space-x-2">
                      <button
                        onClick={() => handleDecision(idx, scheme, 'apply')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                          decision === 'apply'
                            ? 'bg-green-600 text-white shadow-md'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                      >
                        ✓ Apply for {scheme.split('(')[0].trim()}
                      </button>
                      <button
                        onClick={() => handleDecision(idx, scheme, 'skip')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                          decision === 'skip'
                            ? 'bg-gray-600 text-white shadow-md'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        ✕ Skip
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Modal */}
      {showComparison && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-gray-800">Scheme Comparison</h3>
                <button
                  onClick={() => setShowComparison(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {showComparison.map((scheme, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-xl p-4">
                    <h4 className="font-bold text-lg text-indigo-700 mb-3">{scheme.scheme_name}</h4>
                    <div className="space-y-2 text-sm">
                      <p><strong>Benefits:</strong> {scheme.benefits}</p>
                      <p><strong>Documents:</strong> {scheme.documents_required}</p>
                      <p><strong>Status:</strong> 
                        <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                          scheme.status === 'Eligible' 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-red-100 text-red-700'
                        }`}>
                          {scheme.status}
                        </span>
                      </p>
                      {scheme.ai_tip && (
                        <div className="mt-3 p-2 bg-purple-50 rounded-lg">
                          <p className="text-purple-700">🤖 {scheme.ai_tip}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Footer */}
      {Object.keys(resolvedDecisions).length > 0 && (
        <div className="p-4 bg-indigo-50 border-t border-indigo-100">
          <p className="text-sm text-indigo-800">
            <strong>✓ Decisions recorded:</strong> {Object.keys(resolvedDecisions).length} scheme(s)
          </p>
          <p className="text-xs text-indigo-600 mt-1">
            These preferences can be used to generate your personalized application roadmap.
          </p>
        </div>
      )}
    </div>
  );
}

export default ConflictResolver;
