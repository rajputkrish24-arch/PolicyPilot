import React from 'react';

function SchemeCard({ scheme }) {
  const statusColors = {
    Eligible: 'bg-green-100 text-green-800 border-green-300',
    'Not Eligible': 'bg-red-100 text-red-800 border-red-300',
  };

  const statusIcons = {
    Eligible: '✓',
    'Not Eligible': '✗',
  };

  const statusColor = statusColors[scheme.status] || 'bg-gray-100 text-gray-800 border-gray-300';
  const statusIcon = statusIcons[scheme.status] || '?';

  return (
    <div className={`bg-white rounded-xl shadow-md border-l-4 p-6 hover:shadow-lg transition-shadow ${
      scheme.status === 'Eligible' ? 'border-l-green-500' :
      'border-l-red-500'
    }`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-bold text-gray-800 flex-1 pr-3">
          {scheme.scheme_name}
        </h3>
        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${statusColor}`}>
          {statusIcon} {scheme.status}
        </span>
      </div>

      {/* Reason */}
      <div className="mb-4">
        <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
          {scheme.reason}
        </p>
      </div>

      {/* AI Tip */}
      {scheme.ai_tip && (
        <div className="mb-3 p-3 bg-purple-50 rounded-lg border-l-4 border-purple-300">
          <p className="text-xs font-semibold text-purple-700 mb-1">🤖 AI Tip:</p>
          <p className="text-sm text-gray-700">{scheme.ai_tip}</p>
        </div>
      )}

      {/* Benefits */}
      {scheme.benefits && scheme.benefits !== 'Not available' && (
        <div className="mb-3">
          <h4 className="text-sm font-semibold text-gray-700 mb-1">Benefits</h4>
          <p className="text-sm text-gray-600">{scheme.benefits}</p>
        </div>
      )}

      {/* Documents Required */}
      {scheme.documents_required && scheme.documents_required !== 'Not available' && (
        <div className="mb-3">
          <h4 className="text-sm font-semibold text-gray-700 mb-1">Documents Required</h4>
          <p className="text-sm text-gray-600">{scheme.documents_required}</p>
        </div>
      )}

      {/* Application Steps */}
      {scheme.application_steps && scheme.application_steps !== 'Not available' && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-1">How to Apply</h4>
          <p className="text-sm text-gray-600">{scheme.application_steps}</p>
        </div>
      )}
    </div>
  );
}

export default SchemeCard;
