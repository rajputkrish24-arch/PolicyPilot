import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-700 via-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-5xl font-extrabold mb-6 tracking-tight">
              PolicyPilot
            </h1>
            <p className="text-xl text-primary-100 mb-4 max-w-2xl mx-auto">
              AI-Powered Government Scheme Discovery Platform
            </p>
            <p className="text-lg text-primary-200 mb-10 max-w-3xl mx-auto">
              Discover government welfare schemes you are eligible for. 
              Simply enter your profile details and our AI engine will match 
              you with the right schemes, benefits, and application steps.
            </p>
            <Link
              to="/analyze"
              className="inline-block bg-white text-primary-700 font-bold px-8 py-4 rounded-xl text-lg hover:bg-primary-50 active:scale-[0.98] transition-all shadow-xl hover:shadow-2xl"
            >
              Check Your Eligibility →
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="text-center p-6 rounded-xl bg-gray-50 hover:shadow-md transition-shadow">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">📋</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Enter Your Profile
              </h3>
              <p className="text-gray-500">
                Provide your age, income, state, occupation, and category details.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center p-6 rounded-xl bg-gray-50 hover:shadow-md transition-shadow">
              <div className="w-16 h-16 bg-accent-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🤖</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                AI Analysis
              </h3>
              <p className="text-gray-500">
                Our RAG-powered engine searches schemes and checks eligibility using AI + rules.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center p-6 rounded-xl bg-gray-50 hover:shadow-md transition-shadow">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">✅</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Get Results
              </h3>
              <p className="text-gray-500">
                View eligible schemes, benefits, documents needed, and conflict alerts.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-primary-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <p className="text-3xl font-bold text-primary-700">10+</p>
              <p className="text-sm text-gray-600">Schemes Covered</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-primary-700">Free</p>
              <p className="text-sm text-gray-600">100% Open Source</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-primary-700">Local</p>
              <p className="text-sm text-gray-600">AI Runs Locally</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-primary-700">Fast</p>
              <p className="text-sm text-gray-600">Instant Results</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Ready to discover schemes you qualify for?
          </h2>
          <Link
            to="/analyze"
            className="inline-block bg-primary-600 text-white font-semibold px-8 py-3 rounded-lg hover:bg-primary-700 transition-colors shadow-lg"
          >
            Start Now →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm">
            PolicyPilot — Built with 100% Free & Open-Source Tools | College Project
          </p>
        </div>
      </footer>
    </div>
  );
}

export default Home;
