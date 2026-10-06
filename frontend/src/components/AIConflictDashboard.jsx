import React, { useState } from 'react';

function AIConflictDashboard({ conflicts, eligibleSchemes, profile, onResolve }) {
  const [selectedDecisions, setSelectedDecisions] = useState({});
  const [showComparison, setShowComparison] = useState({});
  const [resolvedConflicts, setResolvedConflicts] = useState([]);

  if (!conflicts || conflicts.length === 0) return null;

  const realConflicts = conflicts.filter(
    c => c.conflict && c.conflict_type !== 'none'
  );

  if (realConflicts.length === 0) return null;

  const getSchemeDetails = (schemeName) => {
    return eligibleSchemes.find(s => 
      s.scheme_name.toLowerCase().includes(schemeName.toLowerCase()) ||
      schemeName.toLowerCase().includes(s.scheme_name.toLowerCase())
    );
  };

  const getAIReasoning = (conflict, recommendedScheme) => {
    const reasons = [];
    const scheme = getSchemeDetails(recommendedScheme);
    
    if (!scheme) return ["AI analyzed your profile and found this scheme most suitable"];

    // Income-based reasoning
    if (conflict.conflict_type === 'income_threshold') {
      if (profile?.income > 100000) {
        reasons.push(`✓ Your income (₹${Number(profile.income).toLocaleString()}) exceeds BPL limits, making universal schemes like ${recommendedScheme.split('(')[0]} ideal`);
      } else {
        reasons.push(`✓ Your income level qualifies for both, but ${recommendedScheme.split('(')[0]} offers better long-term benefits`);
      }
    }

    // Age-based reasoning
    if (conflict.conflict_type === 'age_restriction') {
      const age = profile?.age || 0;
      if (scheme.max_age && age > scheme.max_age) {
        reasons.push(`✓ Your age (${age}) exceeds the limit for other schemes`);
      } else {
        reasons.push(`✓ Your age (${age} years) is perfect for this scheme's target group`);
      }
    }

    // Occupation-based
    if (profile?.occupation) {
      const occ = profile.occupation.toLowerCase();
      if (occ.includes('government') || occ.includes('employee')) {
        reasons.push(`✓ As a ${profile.occupation}, you have statutory benefits - this scheme complements them perfectly`);
      } else if (occ.includes('business') || occ.includes('self')) {
        reasons.push(`✓ Business owners get maximum benefit from this scheme's flexible terms`);
      }
    }

    // Add scheme-specific benefits
    if (scheme.benefits) {
      const benefitKeywords = ['insurance', 'pension', 'loan', 'subsidy', 'cash'];
      for (const keyword of benefitKeywords) {
        if (scheme.benefits.toLowerCase().includes(keyword)) {
          reasons.push(`✓ Provides ${keyword} benefit - crucial for your financial security`);
          break;
        }
      }
    }

    return reasons.length > 0 ? reasons : ["AI analyzed your profile and found this scheme most suitable"];
  };

  const getAdvantages = (scheme, vsScheme) => {
    const advantages = [];
    const s1 = getSchemeDetails(scheme);
    const s2 = getSchemeDetails(vsScheme);

    if (!s1) return [];

    // Compare income limits
    if (s1.metadata?.max_income && s2?.metadata?.max_income) {
      if (s1.metadata.max_income > s2.metadata.max_income) {
        advantages.push({
          icon: '💰',
          title: 'Higher Income Limit',
          desc: `₹${Number(s1.metadata.max_income).toLocaleString()} vs ₹${Number(s2.metadata.max_income).toLocaleString()}`,
          benefit: 'No income pressure, apply freely'
        });
      }
    }

    // Compare age limits
    if (s1.max_age && s2?.max_age) {
      if (s1.max_age > s2.max_age) {
        advantages.push({
          icon: '👤',
          title: 'Broader Age Range',
          desc: `Up to ${s1.max_age} years vs ${s2.max_age} years`,
          benefit: 'Longer eligibility window'
        });
      }
    }

    // Universal applicability
    if (!s1.metadata?.max_income || s1.metadata.max_income > 90000000) {
      advantages.push({
        icon: '🌐',
        title: 'Universal Scheme',
        desc: 'No strict eligibility criteria',
        benefit: 'Easy approval, minimal documentation'
      });
    }

    // Insurance benefit
    if (s1.benefits?.toLowerCase().includes('insurance')) {
      advantages.push({
        icon: '🛡️',
        title: 'Insurance Coverage',
        desc: s1.benefits.split('.')[0],
        benefit: 'Financial protection for family'
      });
    }

    // Low cost
    if (s1.benefits?.toLowerCase().includes('rs') && s1.benefits?.toLowerCase().includes('per year')) {
      const match = s1.benefits.match(/Rs\s*(\d+)/);
      if (match && parseInt(match[1]) < 500) {
        advantages.push({
          icon: '💵',
          title: 'Affordable Premium',
          desc: `Just ₹${match[1]} per year`,
          benefit: 'Low cost, high coverage'
        });
      }
    }

    return advantages;
  };

  const getAIRecommendation = (conflict) => {
    if (conflict.ai_recommendation) {
      const schemes = conflict.schemes_involved;
      const rec = conflict.ai_recommendation.toLowerCase();
      
      for (const scheme of schemes) {
        const schemeShort = scheme.split('(')[0].trim().toLowerCase();
        if (rec.includes(schemeShort) || scheme.toLowerCase().includes(schemeShort)) {
          return scheme;
        }
      }
    }
    return conflict.schemes_involved[0];
  };

  const handleDecision = (conflictIndex, schemeName) => {
    setSelectedDecisions(prev => ({ ...prev, [conflictIndex]: schemeName }));
    setResolvedConflicts(prev => [...prev, conflictIndex]);
    if (onResolve) {
      onResolve(conflictIndex, schemeName, 'apply');
    }
  };

  const toggleComparison = (conflictIndex) => {
    setShowComparison(prev => ({
      ...prev,
      [conflictIndex]: !prev[conflictIndex]
    }));
  };

  return (
    <div className="space-y-6 mb-8">
      {realConflicts.map((conflict, idx) => {
        const aiRec = getAIRecommendation(conflict);
        const otherSchemes = conflict.schemes_involved.filter(s => s !== aiRec);
        const isResolved = resolvedConflicts.includes(idx);
        const isComparisonOpen = showComparison[idx];
        
        const aiReasons = getAIReasoning(conflict, aiRec);
        const advantages = getAdvantages(aiRec, otherSchemes[0]);
        const aiRecDetails = getSchemeDetails(aiRec);

        return (
          <div key={idx} className={`bg-white rounded-2xl shadow-lg border-2 overflow-hidden transition-all ${
            isResolved ? 'border-green-400' : 'border-amber-400'
          }`}>
            {/* Header */}
            <div className={`p-5 ${
              isResolved 
                ? 'bg-gradient-to-r from-green-500 to-emerald-500' 
                : 'bg-gradient-to-r from-amber-500 to-orange-500'
            } text-white`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-3xl">{isResolved ? '✅' : '⚠️'}</span>
                  <div>
                    <h3 className="font-bold text-xl">
                      Conflict #{idx + 1}: {conflict.conflict_type === 'income_threshold' ? 'Income Mismatch' : 
                                         conflict.conflict_type === 'age_restriction' ? 'Age Conflict' :
                                         conflict.conflict_type === 'mutual_exclusivity' ? 'Mutual Exclusivity' :
                                         conflict.conflict_type === 'benefit_overlap' ? 'Benefit Overlap' : 'Scheme Conflict'}
                    </h3>
                    <p className="text-amber-100 text-sm">{conflict.message}</p>
                  </div>
                </div>
                {conflict.ai_enhanced && (
                  <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
                    🤖 AI Analyzed
                  </span>
                )}
              </div>
            </div>

            {isResolved ? (
              // RESOLVED STATE
              <div className="p-6 bg-green-50">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-2xl">
                    🎉
                  </div>
                  <div>
                    <p className="font-bold text-green-800 text-lg">Conflict Resolved!</p>
                    <p className="text-green-600">
                      You selected: <strong>{selectedDecisions[idx]}</strong>
                    </p>
                  </div>
                </div>
                
                {getSchemeDetails(selectedDecisions[idx])?.ai_tip && (
                  <div className="bg-white rounded-lg p-4 border border-green-200 mb-4">
                    <p className="text-purple-700">
                      <span className="font-semibold">🤖 AI Tip:</span>{' '}
                      {getSchemeDetails(selectedDecisions[idx]).ai_tip}
                    </p>
                  </div>
                )}

                {/* Ready to Apply Button */}
                {(() => {
                  const scheme = getSchemeDetails(selectedDecisions[idx]);
                  return scheme?.url ? (
                    <a
                      href={scheme.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center space-x-2 w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-6 rounded-xl font-bold text-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg transform hover:scale-[1.02]"
                    >
                      <span>🚀</span>
                      <span>Ready to Apply — Visit Official Portal</span>
                      <span className="text-blue-200">→</span>
                    </a>
                  ) : null;
                })()}

                {(() => {
                  const scheme = getSchemeDetails(selectedDecisions[idx]);
                  return scheme?.application_steps ? (
                    <div className="mt-4 bg-white rounded-lg p-4 border border-green-200">
                      <p className="font-semibold text-gray-700 mb-2">📋 Application Steps:</p>
                      <p className="text-sm text-gray-600">{scheme.application_steps}</p>
                    </div>
                  ) : null;
                })()}
              </div>
            ) : (
              // UNRESOLVED - AI RECOMMENDATION
              <div className="p-6">
                {/* AI's Top Choice */}
                <div className="mb-6">
                  <div className="flex items-center space-x-2 mb-3">
                    <span className="text-2xl">🏆</span>
                    <h4 className="font-bold text-lg text-gray-800">AI's Top Recommendation</h4>
                    <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-xs font-semibold">
                      Best for Your Profile
                    </span>
                  </div>

                  <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-5 border border-purple-200">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h5 className="font-bold text-xl text-purple-900">{aiRec}</h5>
                        {aiRecDetails && (
                          <p className="text-gray-600 mt-1">{aiRecDetails.benefits?.substring(0, 120)}...</p>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-purple-600">
                          {advantages.length}
                        </div>
                        <div className="text-xs text-gray-500">Advantages</div>
                      </div>
                    </div>

                    {/* Why AI Chose This */}
                    <div className="mb-4">
                      <p className="font-semibold text-gray-700 mb-2">🤖 Why AI Chose This for You:</p>
                      <ul className="space-y-2">
                        {aiReasons.map((reason, rIdx) => (
                          <li key={rIdx} className="flex items-start space-x-2 text-sm">
                            <span className="text-green-600 mt-0.5">✓</span>
                            <span className="text-gray-700">{reason.replace('✓ ', '')}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Advantages Grid */}
                    {advantages.length > 0 && (
                      <div className="mb-4">
                        <p className="font-semibold text-gray-700 mb-3">✨ What You Gain:</p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {advantages.map((adv, aIdx) => (
                            <div key={aIdx} className="bg-white rounded-lg p-3 shadow-sm border border-purple-100">
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="text-xl">{adv.icon}</span>
                                <span className="font-semibold text-sm text-gray-800">{adv.title}</span>
                              </div>
                              <p className="text-xs text-gray-600 ml-7">{adv.desc}</p>
                              <p className="text-xs text-green-600 font-medium ml-7 mt-1">
                                → {adv.benefit}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Quick Apply Button */}
                    <button
                      onClick={() => handleDecision(idx, aiRec)}
                      className="w-full bg-purple-600 text-white py-3 rounded-xl font-semibold hover:bg-purple-700 transition-all flex items-center justify-center space-x-2 shadow-lg"
                    >
                      <span>✓</span>
                      <span>Select {aiRec.split('(')[0].trim()}</span>
                      <span className="text-purple-200">— Recommended by AI</span>
                    </button>
                  </div>
                </div>

                {/* Other Options Toggle */}
                <div className="border-t border-gray-200 pt-4">
                  <button
                    onClick={() => toggleComparison(idx)}
                    className="flex items-center justify-between w-full text-gray-600 hover:text-gray-800"
                  >
                    <span className="font-medium">
                      {isComparisonOpen ? '▼' : '▶'} See Other Options & Full Comparison
                    </span>
                    <span className="text-sm text-gray-400">
                      {conflict.schemes_involved.length} schemes total
                    </span>
                  </button>

                  {isComparisonOpen && (
                    <div className="mt-4 space-y-4">
                      <p className="text-sm text-gray-500 mb-3">
                        Compare all eligible schemes side-by-side:
                      </p>
                      
                      {otherSchemes.map((schemeName, sIdx) => {
                        const scheme = getSchemeDetails(schemeName);
                        return (
                          <div key={sIdx} className="border border-gray-200 rounded-xl p-4 bg-gray-50">
                            <div className="flex items-start justify-between mb-3">
                              <h5 className="font-semibold text-gray-800">{schemeName}</h5>
                              <button
                                onClick={() => handleDecision(idx, schemeName)}
                                className="px-4 py-2 bg-gray-600 text-white rounded-lg text-sm hover:bg-gray-700"
                              >
                                Select This Instead
                              </button>
                            </div>
                            {scheme && (
                              <div className="text-sm text-gray-600 space-y-1">
                                <p><strong>Benefits:</strong> {scheme.benefits}</p>
                                <p><strong>Documents:</strong> {scheme.documents_required}</p>
                                {scheme.ai_tip && (
                                  <p className="text-purple-600">🤖 {scheme.ai_tip}</p>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Overall Progress */}
      {resolvedConflicts.length > 0 && (
        <div className="bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="font-bold text-xl">🎉 Great Progress!</h3>
              <p className="text-emerald-100">
                {resolvedConflicts.length} of {realConflicts.length} conflicts resolved
              </p>
            </div>
            <div className="text-4xl font-bold">
              {Math.round((resolvedConflicts.length / realConflicts.length) * 100)}%
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="bg-emerald-700 rounded-full h-3">
            <div 
              className="bg-white rounded-full h-3 transition-all duration-700"
              style={{ width: `${(resolvedConflicts.length / realConflicts.length) * 100}%` }}
            />
          </div>
          
          {resolvedConflicts.length === realConflicts.length && (
            <div className="mt-6 bg-white rounded-2xl p-6 text-gray-800">
              <div className="flex items-center space-x-3 mb-6">
                <span className="text-3xl">🗺️</span>
                <div>
                  <h3 className="font-bold text-xl text-gray-800">Your Application Roadmap</h3>
                  <p className="text-gray-500 text-sm">All conflicts resolved! Here's your action plan:</p>
                </div>
              </div>

              <div className="space-y-4">
                {resolvedConflicts.map((conflictIdx, idx) => {
                  const schemeName = selectedDecisions[conflictIdx];
                  const scheme = getSchemeDetails(schemeName);
                  const priority = idx + 1;

                  return (
                    <div key={idx} className="flex items-start space-x-4 bg-gray-50 rounded-xl p-4 border border-gray-200">
                      {/* Step Number */}
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                        {priority}
                      </div>

                      {/* Scheme Info */}
                      <div className="flex-1">
                        <h4 className="font-bold text-gray-800">{schemeName}</h4>
                        {scheme?.benefits && (
                          <p className="text-sm text-gray-600 mt-1">{scheme.benefits.substring(0, 80)}...</p>
                        )}
                        {scheme?.documents_required && (
                          <p className="text-xs text-gray-500 mt-2">
                            <span className="font-semibold">Documents:</span> {scheme.documents_required.split(',')[0]}...
                          </p>
                        )}
                      </div>

                      {/* Ready to Apply Button */}
                      {scheme?.url ? (
                        <a
                          href={scheme.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-shrink-0 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-2 rounded-lg font-semibold text-sm hover:from-green-600 hover:to-emerald-700 transition-all shadow-md flex items-center space-x-1"
                        >
                          <span>🚀</span>
                          <span>Ready to Apply</span>
                        </a>
                      ) : (
                        <span className="flex-shrink-0 text-gray-400 text-sm">No portal link</span>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Summary */}
              <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-200">
                <p className="text-purple-800">
                  <span className="font-semibold">💡 Pro Tip:</span> Apply in the order shown above. 
                  Each scheme's benefits are independent, so applying to all maximizes your coverage!
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AIConflictDashboard;
