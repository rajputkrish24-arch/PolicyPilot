import React from 'react';

function ConflictAlert({ conflict }) {
  if (!conflict.conflict && conflict.conflict_type === 'none') {
    return null;
  }

  const isTrueConflict = conflict.conflict;
  const isOverlap = conflict.conflict_type === 'benefit_overlap';
  const priority = conflict.priority || 'Medium';
  const hasAI = conflict.ai_explanation || conflict.ai_recommendation;

  // Color coding based on priority and type
  const getAlertStyles = () => {
    if (priority === 'High') return 'bg-red-100 border-red-400 text-red-900';
    if (priority === 'Low') return 'bg-green-50 border-green-300 text-green-800';
    if (isTrueConflict) return 'bg-red-50 border-red-300 text-red-800';
    if (isOverlap) return 'bg-blue-50 border-blue-300 text-blue-800';
    return 'bg-yellow-50 border-yellow-300 text-yellow-800';
  };

  const getIcon = () => {
    if (priority === 'High') return '🚨';
    if (priority === 'Low') return '✅';
    if (isTrueConflict) return '⚠';
    if (isOverlap) return 'ℹ';
    return '⚡';
  };

  const getTitle = () => {
    if (priority === 'High') return 'High Priority Conflict';
    if (priority === 'Low') return 'Low Priority Issue';
    if (isTrueConflict) return 'Conflict Detected';
    if (isOverlap) return 'Benefit Overlap';
    return 'Notice';
  };

  const alertStyles = getAlertStyles();
  const icon = getIcon();
  const title = getTitle();

  return (
    <div className={`rounded-lg border p-4 ${alertStyles}`}>
      <div className="flex items-start space-x-3">
        <span className="text-xl">{icon}</span>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-sm">{title}</h4>
            {hasAI && (
              <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                AI Enhanced
              </span>
            )}
          </div>
          
          <p className="text-sm mt-1">{conflict.message}</p>
          
          {/* AI Explanation */}
          {conflict.ai_explanation && (
            <div className="mt-3 p-3 bg-white/50 rounded-lg border-l-4 border-purple-300">
              <p className="text-xs font-semibold text-purple-700 mb-1">AI Analysis:</p>
              <p className="text-sm text-gray-700">{conflict.ai_explanation}</p>
            </div>
          )}
          
          {/* AI Recommendation */}
          {conflict.ai_recommendation && (
            <div className="mt-2 p-3 bg-purple-50 rounded-lg">
              <p className="text-xs font-semibold text-purple-700 mb-1">Recommendation:</p>
              <p className="text-sm text-gray-700">{conflict.ai_recommendation}</p>
            </div>
          )}
          
          {/* Schemes involved */}
          {conflict.schemes_involved && conflict.schemes_involved.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {conflict.schemes_involved.map((scheme, idx) => (
                <span
                  key={idx}
                  className={`text-xs px-2 py-1 rounded-full ${
                    priority === 'High' ? 'bg-red-100 text-red-700' :
                    priority === 'Low' ? 'bg-green-100 text-green-700' :
                    isTrueConflict ? 'bg-red-100' : 'bg-blue-100'
                  }`}
                >
                  {scheme}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ConflictAlert;
