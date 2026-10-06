/**
 * api.js - API service for PolicyPilot frontend
 * Handles all HTTP requests to the FastAPI backend using Axios.
 */

import axios from 'axios';

// Base URL for the backend API
// Change this for production deployment
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Analyze citizen profile for scheme eligibility.
 * @param {Object} profile - { age, income, state, occupation, category }
 * @returns {Object} - { eligible_schemes, conflicts, total_schemes_checked }
 */
export async function analyzeProfile(profile) {
  try {
    const response = await axios.post(`${API_BASE}/analyze`, profile);
    return response.data;
  } catch (error) {
    console.error('Error analyzing profile:', error);
    throw new Error(
      error.response?.data?.detail || 'Failed to analyze profile. Please try again.'
    );
  }
}

/**
 * Get all available schemes.
 * @returns {Object} - { schemes: [...], total: number }
 */
export async function getAllSchemes() {
  try {
    const response = await axios.get(`${API_BASE}/schemes`);
    return response.data;
  } catch (error) {
    console.error('Error fetching schemes:', error);
    throw new Error('Failed to fetch schemes.');
  }
}

/**
 * Get details of a specific scheme.
 * @param {string} schemeName - Name of the scheme
 * @returns {Object} - Scheme details
 */
export async function getSchemeDetails(schemeName) {
  try {
    const response = await axios.get(`${API_BASE}/schemes/${encodeURIComponent(schemeName)}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching scheme details:', error);
    throw new Error('Failed to fetch scheme details.');
  }
}

/**
 * Check backend health.
 * @returns {Object} - { status, retriever, schemes_loaded }
 */
export async function healthCheck() {
  try {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'unhealthy' };
  }
}
