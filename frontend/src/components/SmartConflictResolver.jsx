import React, { useState } from 'react';

function SmartConflictResolver({ conflicts, eligibleSchemes, onResolve }) {
  const [acceptedRecommendations, setAcceptedRecommendations] = useState([]);
  const [showDetails, setShowDetails] = useState(null);

  if (!conflicts || conflicts.length === 0) return null;

  // Get only real conflicts
  const realConflicts = conflicts.filter(
    c => c.conflict && c.conflict_type !== 'none'
  );

  if (realConflicts.length === 0) return null;

  const getConflictIcon = (type) => {
    switch (type) {
      case 'income_threshold': return '💰';
      case 'age_restriction': return '👤';
      case 'mutual_exclusivity': return '⚔️';
      case 'benefit_overlap': return '🎁';
      default: return '⚠️';
    }
  };

  const getConflictTitle = (type) => {
    switch (type) {
      case 'income_threshold': return 'Income Mismatch';
      case 'age_restriction': return 'Age Conflict';
      case 'mutual_exclusivity': return 'Cannot Apply to Both';
      case 'benefit_overlap': return 'Similar Benefits';
      default: return 'Scheme Conflict';
    }
  };

  const handleAcceptRecommendation = (conflictIndex, schemeName) => {
    setAcceptedRecommendations(prev => [...prev, { conflictIndex, schemeName }]);
    if (onResolve) {
      onResolve(conflictIndex, schemeName, 'apply');
    }
  };

  const handleRejectRecommendation = (conflictIndex) => {
    // User wants to see all options
    setShowDetails(conflictIndex);
  };

  const handleManualChoice = (conflictIndex, schemeName) => {
    setAcceptedRecommendations(prev => [...prev, { conflictIndex, schemeName }]);
    if (onResolve) {
      onResolve(conflictIndex, schemeName, 'apply');
    }
    setShowDetails(null);
  };

  // Find scheme details by name
  const getSchemeDetails = (schemeName) => {
    return eligibleSchemes.find(s => 
      s.scheme_name.toLowerCase().includes(schemeName.toLowerCase()) ||
      schemeName.toLowerCase().includes(s.scheme_name.toLowerCase())
    );
  };

  // Get AI's top recommendation
  const getAIRecommendation = (conflict) => {
    if (conflict.ai_recommendation) {
      // Extract scheme name from recommendation
      const schemes = conflict.schemes_involved;
      const rec = conflict.ai_recommendation.toLowerCase();
      
      for (const scheme of schemes) {
        if (rec.includes(scheme.toLowerCase()) || 
            rec.includes(scheme.split('(')[0].trim().toLowerCase())) {
          return scheme;
        }
      }
    }
    // Default to first scheme
    return conflict.schemes_involved[0];
  };

  const isResolved = (idx) => acceptedRecommendations.some(r => r.conflictIndex === idx);
  const getResolution = (idx) => acceptedRecommendations.find(r => r.conflictIndex === idx);

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden mb-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">🤖</span>
            <div>
              <h2 className="font-bold text-xl">Smart Conflict Resolution</h2>
              <p className="text-amber-100 text-sm">
                {realConflicts.length} conflict{realConflicts.length > 1 ? 's' : ''} detected • 
                AI will recommend the best option
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">{realConflicts.length}</p>
            <p className="text-xs text-amber-100">to resolve</p>
          </div>
        </div>
      </div>

      {/* Conflicts List */}
      <div className="divide-y divide-gray-100">
        {realConflicts.map((conflict, idx) => {
          const aiRecScheme = getAIRecommendation(conflict);
          const aiRecDetails = getSchemeDetails(aiRecScheme);
          const resolved = isResolved(idx);
          const resolution = getResolution(idx);

          return (
            <div key={idx} className={`p-5 transition-all ${resolved ? 'bg-green-50' : 'hover:bg-gray-50'}`}>
              {/* Conflict Header */}
              <div className="flex items-start space-x-4">
                <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                  resolved ? 'bg-green-100' : 'bg-amber-100'
                }`}>
                  {resolved ? '✓' : getConflictIcon(conflict.conflict_type)}
                </div>

                <div className="flex-1">
                  {/* Title & Status */}
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-bold text-gray-800">
                      {getConflictTitle(conflict.conflict_type)}
                    </h3>
                    {conflict.ai_enhanced && (
                      <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                        🤖 AI Enhanced
                      </span>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 mb-3">{conflict.message}</p>

                  {resolved ? (
                    // RESOLVED STATE
                    <div className="bg-green-100 rounded-lg p-4 border border-green-200">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-green-600 text-xl">✓</span>
                        <span className="font-semibold text-green-800">Resolved</span>
                      </div>
                      <p className="text-green-700">
                        You chose to apply for: <strong>{resolution?.schemeName}</strong>
                      </p>
                      {resolution?.schemeName && getSchemeDetails(resolution.schemeName)?.ai_tip && (
                        <p className="text-sm text-green-600 mt-2">
                          💡 {getSchemeDetails(resolution.schemeName).ai_tip}
                        </p>
                      )}
                    </div>
                  ) : showDetails === idx ? (
                    // DETAILED OPTIONS STATE
                    <div className="mt-4 space-y-3">
                      <p className="font-semibold text-gray-700">Choose which scheme to apply for:</p>
                      
                      {conflict.schemes_involved.map((schemeName, sIdx) => {
                        const scheme = getSchemeDetails(schemeName);
                        const isAIRec = schemeName === aiRecScheme;
                        
                        return (
                          <div key={sIdx} className={`border rounded-lg p-4 ${
                            isAIRec ? 'border-purple-300 bg-purple-50' : 'border-gray-200'
                          }`}>
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-2">
                                  <h4 className="font-semibold text-gray-800">{schemeName}</h4>
                                  {isAIRec && (
                                    <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                                      🤖 AI Recommended
                                    </span>
                                  )}
                                </div>
                                {scheme && (
                                  <div className="text-sm text-gray-600 space-y-1">
                                    <p><strong>Benefits:</strong> {scheme.benefits?.substring(0, 100)}...</p>
                                    <p><strong>Documents:</strong> {scheme.documents_required}</p>
                                  </div>
                                )}
                              </div>
                              <button
                                onClick={() => handleManualChoice(idx, schemeName)}
                                className="ml-4 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
                              >
                                Select
                              </button>
                            </div>
                          </div>
                        );
                      })}

                      <button
                        onClick={() => setShowDetails(null)}
                        className="text-gray-500 text-sm hover:text-gray-700"
                      >
                        ← Back to AI Recommendation
                      </button>
                    </div>
                  ) : (
                    // AI RECOMMENDATION STATE (Default)
                    <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                      {/* AI Analysis */}
                      {conflict.ai_explanation && (
                        <div className="mb-3">
                          <p className="text-sm text-purple-800">
                            <span className="font-semibold">🤖 Analysis:</span> {conflict.ai_explanation}
                          </p>
                        </div>
                      )}

                      {/* AI Recommendation */}
                      <div className="bg-white rounded-lg p-3 mb-3">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-purple-600">💡</span>
                          <span className="font-semibold text-gray-800">AI Recommendation</span>
                        </div>
                        <p className="text-gray-700 mb-2">
                          Apply for <strong className="text-purple-700">{aiRecScheme}</strong>
                        </p>
                        {conflict.ai_recommendation && (
                          <p className="text-sm text-gray-600">{conflict.ai_recommendation}</p>
                        )}
                        {aiRecDetails?.ai_tip && (
                          <p className="text-sm text-purple-600 mt-2">🎯 {aiRecDetails.ai_tip}</p>
                        )}
                      </div>

                      {/* Action Buttons */}
                      <div className="flex space-x-3">
                        <button
                          onClick={() => handleAcceptRecommendation(idx, aiRecScheme)}
                          className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center space-x-2"
                        >
                          <span>✓</span>
                          <span>Accept AI Recommendation</span>
                        </button>
                        <button
                          onClick={() => handleRejectRecommendation(idx)}
                          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                        >
                          See All Options
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Progress Footer */}
      {acceptedRecommendations.length > 0 && (
        <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-bold">
                ✓ {acceptedRecommendations.length} of {realConflicts.length} conflicts resolved
              </p>
              <p className="text-sm text-green-100">
                Your personalized roadmap is being generated...
              </p>
            </div>
            <div className="text-3xl">
              {Math.round((acceptedRecommendations.length / realConflicts.length) * 100)}%
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-3 bg-green-700 rounded-full h-2">
            <div 
              className="bg-white rounded-full h-2 transition-all duration-500"
              style={{ 
                width: `${(acceptedRecommendations.length / realConflicts.length) * 100}%` 
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default SmartConflictResolver;
