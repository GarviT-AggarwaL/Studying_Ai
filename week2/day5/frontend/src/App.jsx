import { useEffect, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_BACKEND_URL;

function App() {
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);

  const [messages, setMessages] = useState([
    {
      role: "ai",
      text: "Hi! I'm Garvit's AI assistant. Ask me anything about my skills, projects, education or experience.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // Load resume/profile
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await fetch(`${API_URL}/profile`);

        if (!response.ok) {
          throw new Error("Failed to load profile");
        }

        const data = await response.json();
        setProfile(data);
      } catch (error) {
        console.error("Profile loading error:", error);
      } finally {
        setProfileLoading(false);
      }
    };

    loadProfile();
  }, []);

  // Send question to FastAPI
  const sendMessage = async () => {
    const question = input.trim();

    if (!question || loading) {
      return;
    }

    // Add user message
    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: question,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "ai",
          text: data.answer,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((previous) => [
        ...previous,
        {
          role: "ai",
          text: "Sorry, I couldn't connect to the AI assistant.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Suggested question
  const askQuestion = (question) => {
    setInput(question);

    document.getElementById("ai")?.scrollIntoView({
      behavior: "smooth",
    });
  };

  if (profileLoading) {
    return (
      <div className="loading-screen">
        Loading portfolio...
      </div>
    );
  }

  return (
    <div className="portfolio">

      {/* Navigation */}
      <nav className="navbar">
        <div className="logo">
          GARVIT<span>.</span>
        </div>

        <div className="nav-links">
          <a href="#about">About</a>
          <a href="#skills">Skills</a>
          <a href="#experience">Experience</a>
          <a href="#projects">Projects</a>
          <a href="#ai">AI Assistant</a>
        </div>
      </nav>

      {/* Hero */}
      <main className="hero">

        <div className="hero-content">

          <p className="eyebrow">
            ARTIFICIAL INTELLIGENCE · MACHINE LEARNING
          </p>

          <h1>
            Building intelligent
            <br />
            <span>systems that matter.</span>
          </h1>

          <p className="hero-description">
            Hi, I'm {profile?.name || "Garvit Aggarwal"} — an AI/ML
            developer passionate about building practical intelligent
            applications using Python, Machine Learning and Generative AI.
          </p>

          <div className="hero-buttons">
            <a href="#projects" className="primary-btn">
              View My Work →
            </a>

            <a href="#ai" className="secondary-btn">
              Ask My AI ✦
            </a>
          </div>

        </div>

        {/* AI Preview Card */}
        <div className="ai-card">

          <div className="ai-card-header">
            <div className="ai-status"></div>

            <span>GARVIT AI</span>

            <span className="online">
              ONLINE
            </span>
          </div>

          <div className="ai-message">

            <div className="ai-avatar">
              ✦
            </div>

            <div>
              <p className="ai-name">
                Garvit's AI
              </p>

              <p>
                Hi! I know about Garvit's skills, projects,
                education and experience.
              </p>
            </div>

          </div>

          <button
            className="suggestion"
            onClick={() =>
              askQuestion("Tell me about Garvit's projects.")
            }
          >
            Ask me about my projects →
          </button>

          <button
            className="suggestion"
            onClick={() =>
              askQuestion(
                "What are Garvit's strongest technical skills?"
              )
            }
          >
            What are my strongest skills? →
          </button>

        </div>

      </main>

      {/* About */}
      <section id="about" className="section">

        <p className="section-label">
          01 — ABOUT
        </p>

        <h2>
          Turning curiosity into
          <br />
          working systems.
        </h2>

        <p className="section-text">
          I enjoy taking ideas from concept to implementation —
          from machine learning models and computer vision systems
          to AI-powered applications.
        </p>

      </section>

      {/* Skills */}
      <section id="skills" className="section">

        <p className="section-label">
          02 — SKILLS
        </p>

        <h2>
          Technical toolkit.
        </h2>

        <div className="skills">

          {profile?.skills?.map((skill, index) => (
            <div key={index}>
              {skill}
            </div>
          ))}

        </div>

      </section>

      {/* Experience */}
      <section id="experience" className="section">

        <p className="section-label">
          03 — EXPERIENCE
        </p>

        <h2>
          Where I've worked.
        </h2>

        <div className="experience-list">

          {profile?.experience?.map((job, index) => (

            <div
              className="experience-card"
              key={index}
            >

              <div className="experience-top">

                <div>
                  <h3>{job.role}</h3>

                  <p className="company">
                    {job.company}
                  </p>
                </div>

                <span className="duration">
                  {job.duration}
                </span>

              </div>

              <p className="experience-description">
                {job.description}
              </p>

              <div className="tags">

                {job.skills_used?.map(
                  (skill, skillIndex) => (
                    <span key={skillIndex}>
                      {skill}
                    </span>
                  )
                )}

              </div>

            </div>

          ))}

        </div>

      </section>

      {/* Education */}
      <section className="section">

        <p className="section-label">
          04 — EDUCATION
        </p>

        <h2>
          Education.
        </h2>

        <div className="education-list">

          {profile?.education?.map(
            (education, index) => (
              <div
                className="education-card"
                key={index}
              >
                {education}
              </div>
            )
          )}

        </div>

      </section>

      {/* Projects */}
      <section id="projects" className="section">

        <p className="section-label">
          05 — PROJECTS
        </p>

        <h2>
          Things I've built.
        </h2>

        <div className="project-grid">

          {profile?.projects?.map(
            (project, index) => (

              <div
                className="project-card"
                key={index}
              >

                <div className="project-number">
                  {String(index + 1).padStart(2, "0")}
                </div>

                <h3>
                  {project.name}
                </h3>

                <p>
                  {project.description ||
                    "Project details available through my AI assistant."}
                </p>

                <div className="tags">

                  {project.technologies?.map(
                    (technology, techIndex) => (
                      <span key={techIndex}>
                        {technology}
                      </span>
                    )
                  )}

                </div>

                {(project.github || project.demo) && (

                  <div className="project-links">

                    {project.github && (
                      <a
                        href={project.github}
                        target="_blank"
                        rel="noreferrer"
                      >
                        GitHub ↗
                      </a>
                    )}

                    {project.demo && (
                      <a
                        href={project.demo}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Live Demo ↗
                      </a>
                    )}

                  </div>

                )}

              </div>

            )
          )}

        </div>

      </section>

      {/* Certifications */}
      <section className="section">

        <p className="section-label">
          06 — CERTIFICATIONS
        </p>

        <h2>
          Continuous learning.
        </h2>

        <div className="certifications">

          {profile?.certifications?.map(
            (certification, index) => (

              <div
                className="certification"
                key={index}
              >
                <span>✦</span>
                {certification}
              </div>

            )
          )}

        </div>

      </section>

      {/* AI Assistant */}
      <section id="ai" className="ai-section">

        <p className="section-label">
          07 — AI ASSISTANT
        </p>

        <h2>
          Don't just read my resume.
          <br />
          Ask it.
        </h2>

        <p>
          Ask my AI assistant about my skills,
          projects, education and experience.
        </p>

        <div className="chat-box">

          <div className="chat-header">

            <div className="chat-title">

              <div className="ai-status"></div>

              <div>
                <strong>Garvit AI</strong>
                <small>
                  AI Portfolio Assistant
                </small>
              </div>

            </div>

            <span className="online">
              ● ONLINE
            </span>

          </div>

          <div className="messages">

            {messages.map((message, index) => (

              <div
                key={index}
                className={`message ${message.role}`}
              >

                <div className="message-label">
                  {message.role === "ai"
                    ? "GARVIT AI"
                    : "YOU"}
                </div>

                <div className="message-text">
                  {message.text}
                </div>

              </div>

            ))}

            {loading && (
              <div className="message ai">

                <div className="message-label">
                  GARVIT AI
                </div>

                <div className="typing">
                  Thinking...
                </div>

              </div>
            )}

          </div>

          <div className="suggested-questions">

            <button
              onClick={() =>
                askQuestion(
                  "What are Garvit's strongest technical skills?"
                )
              }
            >
              Strongest skills?
            </button>

            <button
              onClick={() =>
                askQuestion(
                  "Tell me about Garvit's projects."
                )
              }
            >
              Projects?
            </button>

            <button
              onClick={() =>
                askQuestion(
                  "Tell me about Garvit's experience."
                )
              }
            >
              Experience?
            </button>

          </div>

          <div className="chat-input">

            <input
              type="text"
              placeholder="Ask something about Garvit..."
              value={input}
              onChange={(e) =>
                setInput(e.target.value)
              }
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  sendMessage();
                }
              }}
            />

            <button
              onClick={sendMessage}
              disabled={loading}
            >
              →
            </button>

          </div>

        </div>

      </section>

      {/* Contact */}
      <section className="contact-section">

        <p className="section-label">
          08 — CONTACT
        </p>

        <h2>
          Let's build something
          <br />
          intelligent.
        </h2>

        <p>
          Interested in working together or discussing
          an AI/ML opportunity?
        </p>

        <div className="contact-buttons">

          <a
            href={`mailto:${profile?.email}`}
            className="primary-btn"
          >
            Email Me →
          </a>

        </div>

      </section>

      {/* Footer */}
      <footer>

        <div>
          GARVIT.
        </div>

        <p>
          AI/ML Developer · Building with intelligence.
        </p>

      </footer>

    </div>
  );
}

export default App;