# Achievable Goals for Minime App Proposal

This document outlines achievable goals based on the PROPOSAL.md, focusing on the pivot to a self-marketing personal profile app. Goals are structured into MVP (core functionality) and Stretch (advanced features) phases, ensuring they are realistic for a capstone project timeline.

## Achievable Goals

### MVP (Minimum Viable Product): Basic Personalized Profile Display
The MVP focuses on creating a functional, static version of the app adapted to a personal profile, emphasizing frontend user interaction without complex backend or AI.

- **Goal 1: Set up project structure and basic web app foundation**
  - Create HTML, CSS, and JavaScript files for a simple web page.
  - Implement a responsive layout using basic CSS or a lightweight framework (e.g., Bootstrap).
  - Ensure the app runs locally in a browser.

- **Goal 2: Display static personal profile content**
  - Hardcode profile data (e.g., name, bio, interests, skills) into the app.
  - Organize content into sections like "About Me," "Skills," and "Interests" for a marketing-focused profile.
  - Add basic styling to make the profile visually appealing and shareable.

- **Goal 3: Add minimal user interaction for profile viewing**
  - Include navigation or tabs to switch between profile sections.
  - Ensure the profile is printable or exportable as a simple PDF/image for sharing.

*Verification*: The app loads in a browser, displays complete profile information, and is usable without errors.

### Stretch Goals: Interactive Profile Creation with AI Enhancement
Stretch goals build on the MVP by adding user input, data persistence, and AI features, while keeping the focus on self-marketing rather than mental health.

- **Goal 1: Implement user input forms**
  - Add forms for users to enter profile data (e.g., text fields for bio, dropdowns for skills).
  - Validate inputs to ensure data quality (e.g., required fields, character limits).

- **Goal 2: Add data storage and retrieval**
  - Use local storage (e.g., browser localStorage) to save and load user inputs.
  - Allow users to edit and update their profiles persistently.

- **Goal 3: Integrate AI for profile suggestions**
  - Connect to an AI service (e.g., via API) to generate suggestions based on user inputs (e.g., improved bio wording).
  - Ensure AI output aligns with self-marketing (e.g., professional tone, highlight strengths).

*Verification*: Users can input data, save it, and receive AI-generated enhancements; app remains stable and focused on marketing profiles.

## Requirements

This section identifies what is needed to achieve the goals, addressing uncertainties from the proposal (e.g., AI libraries, APIs, integration concepts).

### Libraries and Frameworks
- **Frontend Basics**: HTML5, CSS3, JavaScript (ES6+). No advanced frameworks needed for MVP; consider React or Vue.js for stretch if interactivity increases.
- **AI Integration**: OpenAI API (or similar, like Google's Gemini) for text generation. Build on class examples; use libraries like `openai` (Python) or fetch API (JavaScript) for requests.
- **Styling/UI**: Bootstrap or Tailwind CSS for responsive design.
- **Data Storage**: Browser localStorage for MVP; consider IndexedDB or a simple backend (e.g., Node.js with Express) for stretch.

### APIs
- **AI/Text Generation**: OpenAI API or a free alternative (e.g., Hugging Face API) for generating profile suggestions. Requires API key and understanding of rate limits.
- **Personality/Profile APIs**: Optional for stretch; APIs from services like 16personalities.com or custom profilers to enhance AI inputs. Research free/public APIs to avoid costs.

### Skills and Concepts to Learn
- **Web Development Fundamentals**: HTML/CSS/JS basics, responsive design, form handling. Build on any prior knowledge.
- **AI Integration**: How to make API calls, handle responses, and integrate AI outputs into UI. Review class materials and online docs (e.g., OpenAI documentation).
- **Frontend-Backend Basics**: For stretch, basic server-side logic (e.g., Node.js) to handle data if localStorage isn't sufficient.
- **Data Persistence**: Local storage concepts; basic database if expanding.
- **Security/Privacy**: Handling user data ethically, especially with AI (avoid sensitive info).

### Other Resources
- **Tools**: VS Code for development, Git for version control, browser dev tools for testing.
- **Learning Materials**: MDN Web Docs for web basics, OpenAI API tutorials, freeCodeCamp for JS/AI integration.
- **Testing**: Manual testing in browsers; consider unit tests for forms/AI logic.
- **Timeline/Resources**: Aim for 4-6 weeks for MVP, additional 4-6 for stretch, depending on learning curve.

This outline ensures goals are aligned with the proposal's pivot, keeping the app as a self-marketing tool. Adjust based on progress and feedback.