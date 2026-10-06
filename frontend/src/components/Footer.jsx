import React from 'react';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-900 text-white">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Project Info */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">📋</span>
              <h3 className="text-xl font-bold">PolicyPilot</h3>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">
              AI-Powered Government Scheme Discovery Platform. 
              A Minor/Major Project demonstrating practical application of 
              Machine Learning and Web Technologies.
            </p>
            <div className="flex items-center space-x-2 text-sm text-slate-500">
              <span>📅 Academic Year: {currentYear}-{currentYear + 1}</span>
            </div>
          </div>

          {/* College Details */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-slate-200">Institution</h4>
            <div className="space-y-2 text-sm text-slate-400">
              <p className="font-medium text-slate-300">[Your College Name]</p>
              <p>[Department Name]</p>
              <p>[University Name]</p>
              <p className="pt-2">📍 [College Address, City]</p>
              <p>📧 [college@email.edu.in]</p>
            </div>
          </div>

          {/* Project Team */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-slate-200">Project Team</h4>
            <div className="space-y-2 text-sm text-slate-400">
              <div className="flex justify-between">
                <span>👨‍💻 [Your Name]</span>
                <span className="text-slate-500">Roll No: [XX]</span>
              </div>
              <div className="flex justify-between">
                <span>👨‍💻 [Team Member 2]</span>
                <span className="text-slate-500">Roll No: [XX]</span>
              </div>
              <div className="flex justify-between">
                <span>👨‍💻 [Team Member 3]</span>
                <span className="text-slate-500">Roll No: [XX]</span>
              </div>
              <div className="pt-2 border-t border-slate-700">
                <p className="text-slate-300">👨‍🏫 Guide: [Professor Name]</p>
                <p className="text-slate-500 text-xs">[Designation]</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tech Stack Used */}
        <div className="mt-10 pt-8 border-t border-slate-800">
          <h4 className="text-sm font-semibold text-slate-500 mb-4 text-center">
            TECHNOLOGIES USED
          </h4>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <span className="px-3 py-1 bg-slate-800 rounded-full text-slate-300">React.js</span>
            <span className="px-3 py-1 bg-slate-800 rounded-full text-slate-300">Tailwind CSS</span>
            <span className="px-3 py-1 bg-slate-800 rounded-full text-slate-300">Python FastAPI</span>
            <span className="px-3 py-1 bg-slate-800 rounded-full text-slate-300">Ollama AI</span>
            <span className="px-3 py-1 bg-slate-800 rounded-full text-slate-300">Mistral LLM</span>
            <span className="px-3 py-1 bg-slate-800 rounded-full text-slate-300">FAISS</span>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="bg-slate-950 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-2 md:space-y-0 text-sm text-slate-500">
            <p>
              © {currentYear} PolicyPilot. Submitted in partial fulfillment of 
              [Degree Name] requirements.
            </p>
            <p className="flex items-center space-x-1">
              <span>Made with</span>
              <span className="text-red-500">❤️</span>
              <span>for Digital India</span>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
