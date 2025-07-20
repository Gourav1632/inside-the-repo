# Into the Repo

**Into the Repo** is an AI-powered developer onboarding platform that streamlines the process of understanding large GitHub repositories. It automatically analyzes codebases to generate interactive architecture maps, highlight key code insights, and deliver personalized onboarding tutorials.

🚀 **Live Demo:** [https://into-the-repo.vercel.app](https://into-the-repo.vercel.app)

## 🌟 Features

- 🔍 **Codebase Analysis:** Parses large codebases (100K+ lines) using Tree-sitter for AST-level understanding.
- 🧠 **AI-Powered Summarization:** Extracts and ranks critical files with >90% accuracy based on Git history frequency analysis.
- 🗺️ **Architecture Mapping:** Auto-generates visual maps showing code structure and dependencies.
- 📚 **Onboarding Tutorials:** Generates personalized, step-by-step tutorials for developers new to a codebase.
- ⚡ **High Performance:** All insights rendered in under 5 seconds via an optimized FastAPI backend with Server-Sent Events (SSE).

## 🛠 Tech Stack

- **Frontend:** Next.js, TypeScript, React Flow, IndexedDB
- **Backend:** FastAPI, Python
- **Code Parsing:** Tree-sitter
- **APIs:** GitHub API, Gemini API
- **Streaming:** Server-Sent Events (SSE)

## 📦 Installation

```bash
# Clone the repo
https://github.com/Gourav1632/into-the-repo.git

# Install frontend dependencies
cd frontend
npm install

# Start the frontend
npm run dev

# Install backend dependencies
cd ../backend
pip install -r requirements.txt

# Start the backend
uvicorn main:app --reload
```

## 🚀 Usage
1. Enter a GitHub repository URL.
2. The app will fetch and parse the codebase.
3. Visual insights, code summaries, and tutorials will be generated instantly.

## 🧩 Future Improvements
- Multi-language support
- Plugin system for custom onboarding flows
- Exporting documentation to markdown/PDF

## 🙌 Acknowledgments
- Tree-sitter for AST parsing
- GitHub API
- OpenAI/Gemini APIs for AI capabilities

---

Built with ❤️ by [Gourav Kumar](https://gouavkumar.netlify.app)
