import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyzeProfile } from '../services/api';

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
  'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
  'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya',
  'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim',
  'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand',
  'West Bengal', 'Delhi', 'Chandigarh',
];

const OCCUPATIONS = [
  'Farmer', 'Student', 'Business Owner', 'Daily Wage Worker',
  'Government Employee', 'Private Employee', 'Unemployed', 'Senior Citizen',
  'Woman', 'Person with Disability', 'Other',
];

const CATEGORIES = [
  'General', 'OBC', 'SC', 'ST', 'EWS', 'EWS/LIG', 'BPL',
];

function EligibilityForm() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [profile, setProfile] = useState({
    age: '',
    income: '',
    state: '',
    occupation: '',
    category: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = {
        age: parseInt(profile.age),
        income: parseInt(profile.income),
        state: profile.state,
        occupation: profile.occupation,
        category: profile.category || undefined,
      };

      const results = await analyzeProfile(payload);
      // Store results in sessionStorage for Results page
      sessionStorage.setItem('analysisResults', JSON.stringify(results));
      sessionStorage.setItem('citizenProfile', JSON.stringify(profile));
      navigate('/results');
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-xl p-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        Check Your Eligibility
      </h2>
      <p className="text-gray-500 mb-6">
        Enter your details to discover government schemes you qualify for.
      </p>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Age */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Age <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            name="age"
            value={profile.age}
            onChange={handleChange}
            min="0"
            max="120"
            required
            placeholder="e.g., 45"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
          />
        </div>

        {/* Annual Income */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Annual Income (Rs) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            name="income"
            value={profile.income}
            onChange={handleChange}
            min="0"
            required
            placeholder="e.g., 150000"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
          />
        </div>

        {/* State */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            State <span className="text-red-500">*</span>
          </label>
          <select
            name="state"
            value={profile.state}
            onChange={handleChange}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors bg-white"
          >
            <option value="">Select your state</option>
            {INDIAN_STATES.map((state) => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>

        {/* Occupation */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Occupation <span className="text-red-500">*</span>
          </label>
          <select
            name="occupation"
            value={profile.occupation}
            onChange={handleChange}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors bg-white"
          >
            <option value="">Select your occupation</option>
            {OCCUPATIONS.map((occ) => (
              <option key={occ} value={occ}>{occ}</option>
            ))}
          </select>
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Category (Optional)
          </label>
          <select
            name="category"
            value={profile.category}
            onChange={handleChange}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors bg-white"
          >
            <option value="">Select category</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all ${
            loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700 active:scale-[0.98] shadow-lg hover:shadow-xl'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center space-x-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>Analyzing...</span>
            </span>
          ) : (
            'Find Eligible Schemes'
          )}
        </button>
      </form>
    </div>
  );
}

export default EligibilityForm;
