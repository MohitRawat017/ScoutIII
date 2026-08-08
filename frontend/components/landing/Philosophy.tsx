import Reveal from "@/components/Reveal";

const PILLARS = [
  {
    num: "01",
    title: "Grounded, not guessed",
    body: "Every price, rating, and review claim in a report traces back to fetched Amazon data via SerpApi. The model never invents numbers.",
  },
  {
    num: "02",
    title: "Fast by design",
    body: "Classification and tool-calling run on Gemini Flash; deep analysis on Gemini Pro. Most queries go from question to report in under a minute.",
  },
  {
    num: "03",
    title: "Yours to use",
    body: "Reports come back as clean Markdown — paste them into documents, decks, or your own research notes without re-formatting.",
  },
];

export default function Philosophy() {
  return (
    <section className="section philosophy" id="philosophy">
      <div className="container">
        <div className="philosophy-grid">
          <Reveal>
            <p className="eyebrow">the agent</p>
            <h2 className="section-title">Evidence, not vibes</h2>
            <p className="section-intro">
              Scoutii reads the whole category so you don&apos;t have to open forty product pages.
            </p>
          </Reveal>
          <div>
            {PILLARS.map((pillar, i) => (
              <Reveal key={pillar.num} delay={i * 90}>
                <div className="philosophy-pillar">
                  <span className="pillar-num" aria-hidden="true">{pillar.num}</span>
                  <div>
                    <h3 className="pillar-title">{pillar.title}</h3>
                    <p className="pillar-body">{pillar.body}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
