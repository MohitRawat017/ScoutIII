"use client";

import { useCallback, useState } from "react";

import Hero from "@/components/landing/Hero";
import IntentCards from "@/components/landing/IntentCards";
import Philosophy from "@/components/landing/Philosophy";
import SampleQueries from "@/components/landing/SampleQueries";
import ChatWorkspace from "@/components/chat/ChatWorkspace";

export default function Home() {
  const [draftQuery, setDraftQuery] = useState("");

  // scroll to the chat input and focus it (used by the hero CTA)
  const goToChat = useCallback(() => {
    document.getElementById("chat")?.scrollIntoView({ behavior: "smooth" });
    window.setTimeout(() => {
      (document.getElementById("query-input") as HTMLInputElement | null)?.focus();
    }, 550);
  }, []);

  // fill the input with a suggested query, then land there
  const fillQuery = useCallback(
    (query: string) => {
      setDraftQuery(query);
      goToChat();
    },
    [goToChat]
  );

  return (
    <main>
      <Hero onStart={goToChat} />
      <IntentCards onSelect={fillQuery} />
      <Philosophy />
      <SampleQueries onSelect={fillQuery} />
      <section className="section chat" id="chat">
        <div className="container">
          <div className="chat-head">
            <p className="eyebrow">try it</p>
            <h2 className="section-title">Start a research query</h2>
            <p className="section-intro">
              Type a question about any Amazon category — we&apos;ll search, aggregate, and
              return a grounded market report in under a minute.
            </p>
          </div>
          <ChatWorkspace draft={draftQuery} onDraftChange={setDraftQuery} />
        </div>
      </section>
    </main>
  );
}
