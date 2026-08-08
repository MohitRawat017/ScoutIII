export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-inner">
        <div className="footer-brand">
          <p className="footer-name">Scoutii</p>
          <p className="footer-tag">Amazon research, answered calmly.</p>
        </div>
        <p className="footer-credit">Data: SerpApi · Reasoning: Google Gemini · Orchestration: LangGraph</p>
      </div>
      <div className="container footer-bottom">
        <span>© {new Date().getFullYear()} Scoutii</span>
        <span>Every claim is traceable to fetched data.</span>
      </div>
    </footer>
  );
}
