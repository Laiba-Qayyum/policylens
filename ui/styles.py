STYLE = """<style>
@keyframes pl-rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pl-pulse {
  0%, 100% { opacity: 0.45; transform: translateX(0); }
  50% { opacity: 1; transform: translateX(4px); }
}
@keyframes pl-glow {
  0%, 100% { opacity: 0.55; transform: scale(1); }
  50% { opacity: 0.9; transform: scale(1.12); }
}
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0b2a4a 0%, #0e4a5a 100%); }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #e6f2f5; }
.pl-brand { font-size: 1.7rem; font-weight: 700; color: #ffffff; margin-bottom: 14px; }
[data-baseweb="tab-list"] { gap: 8px; }
[data-baseweb="tab"] { border-radius: 999px; padding: 6px 18px; }
[data-baseweb="tab"][aria-selected="true"] { background: #0f766e; color: #ffffff; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none; }
[data-testid="stBaseButton-primary"] {
  background: linear-gradient(90deg, #0f766e, #14b8a6);
  border: none;
  color: #ffffff;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
[data-testid="stBaseButton-primary"]:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(20, 184, 166, 0.35);
}
[data-testid="stBaseButton-primary"]:focus-visible {
  outline: 2px solid #5eead4;
  outline-offset: 2px;
}
[data-testid="stBaseButton-primary"]:disabled { opacity: 0.5; }
[data-testid="stTextInput"] input:focus { box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.5); }
.pl-head { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.pl-welcome { margin: 0; font-size: 2rem; font-weight: 700; }
.pl-sub { margin: 4px 0 0; opacity: 0.75; }
.pl-chips { display: flex; gap: 10px; align-items: center; }
.pl-chip { padding: 6px 14px; border-radius: 999px; background: rgba(128, 128, 128, 0.15); }
.pl-pill { padding: 6px 14px; border-radius: 999px; font-size: 0.9rem; }
.pl-pill.ok { background: rgba(34, 197, 94, 0.18); color: #22c55e; }
.pl-pill.bad { background: rgba(239, 68, 68, 0.18); color: #ef4444; }
.pl-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 14px 0; }
@media (max-width: 900px) { .pl-grid { grid-template-columns: repeat(2, 1fr); } }
.pl-card, .pl-panel {
  padding: 16px 18px;
  border-radius: 14px;
  background: rgba(128, 128, 128, 0.10);
  border: 1px solid rgba(128, 128, 128, 0.18);
  animation: pl-rise 0.5s ease both;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.pl-card:hover, .pl-panel:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}
.pl-grid .pl-card:nth-child(2) { animation-delay: 0.08s; }
.pl-grid .pl-card:nth-child(3) { animation-delay: 0.16s; }
.pl-grid .pl-card:nth-child(4) { animation-delay: 0.24s; }
.pl-icon {
  width: 38px; height: 38px; border-radius: 10px; margin-bottom: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.pl-icon.t1 { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
.pl-icon.t2 { background: rgba(20, 184, 166, 0.2); color: #2dd4bf; }
.pl-icon.t3 { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.pl-icon.t4 { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
.pl-num { font-size: 2rem; font-weight: 700; line-height: 1.1; }
.pl-label { opacity: 0.75; }
.pl-panel-title { font-weight: 700; margin-bottom: 10px; }
.pl-table { width: 100%; border-collapse: collapse; }
.pl-table th { text-align: left; opacity: 0.6; font-weight: 600; padding: 6px 8px; }
.pl-table td { padding: 8px; border-top: 1px solid rgba(128, 128, 128, 0.18); }
.pl-panel > .pl-ring-label { opacity: 0.75; padding: 8px 0; }
.pl-ring-wrap { position: relative; width: 150px; height: 150px; margin: 8px auto; }
.pl-ring {
  width: 150px; height: 150px; border-radius: 50%;
  background: conic-gradient(#14b8a6 calc(var(--pct) * 1%), rgba(128, 128, 128, 0.25) 0);
  -webkit-mask: radial-gradient(farthest-side, transparent 66%, #000 67%);
  mask: radial-gradient(farthest-side, transparent 66%, #000 67%);
}
.pl-ring-wrap .pl-ring-label {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 1.8rem; font-weight: 700;
}
.pl-ring-caption { text-align: center; opacity: 0.75; }
.pl-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 14px;
  margin-bottom: 8px;
  border-radius: 10px;
  background: rgba(128, 128, 128, 0.08);
  animation: pl-rise 0.4s ease both;
  transition: transform 0.2s ease, background 0.2s ease;
}
.pl-row:hover { transform: translateX(4px); background: rgba(128, 128, 128, 0.16); }
.pl-row span:last-child { opacity: 0.7; white-space: nowrap; }
.pl-row:nth-child(2) { animation-delay: 0.05s; }
.pl-row:nth-child(3) { animation-delay: 0.10s; }
.pl-row:nth-child(4) { animation-delay: 0.15s; }
.pl-row:nth-child(5) { animation-delay: 0.20s; }
.pl-row:nth-child(n+6) { animation-delay: 0.25s; }
.pl-hero {
  position: relative;
  overflow: hidden;
  min-height: 560px;
  padding: 40px;
  border-radius: 18px;
  color: #ffffff;
  background: linear-gradient(160deg, #0b2a4a 0%, #0e3b5c 55%, #0f766e 130%);
  box-shadow: 0 12px 32px rgba(11, 42, 74, 0.35);
}
.pl-hero::before {
  content: "";
  position: absolute;
  width: 340px;
  height: 340px;
  right: -90px;
  top: -90px;
  background: radial-gradient(circle, rgba(20, 184, 166, 0.5), transparent 65%);
  animation: pl-glow 6s ease-in-out infinite;
}
.pl-hero > * { position: relative; }
.pl-hero-brand { font-size: 1.3rem; font-weight: 700; letter-spacing: 0.02em; margin-bottom: 40px; }
.pl-hero-title { font-size: 2.4rem; line-height: 1.15; margin: 0 0 14px; color: #ffffff; }
.pl-hero-text { max-width: 440px; opacity: 0.85; margin-bottom: 24px; }
.pl-flow { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin: 24px 0; }
.pl-step {
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.10);
  border: 1px solid rgba(255, 255, 255, 0.18);
  animation: pl-rise 0.6s ease both;
}
.pl-flow .pl-step:nth-child(3) { animation-delay: 0.2s; }
.pl-flow .pl-step:nth-child(5) { animation-delay: 0.4s; }
.pl-arrow { color: #5eead4; animation: pl-pulse 1.8s ease-in-out infinite; }
.pl-trust {
  margin-top: 28px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.18);
  opacity: 0.85;
  font-size: 0.95rem;
}
.pl-form-title { font-size: 1.7rem; margin: 8px 0 4px; }
.pl-address {
  padding: 8px 12px;
  margin-bottom: 12px;
  border-radius: 10px;
  background: rgba(20, 184, 166, 0.12);
  border: 1px solid rgba(20, 184, 166, 0.3);
}
@media (max-width: 800px) {
  .pl-hero { min-height: 0; padding: 28px; }
  .pl-hero-title { font-size: 1.8rem; }
  .pl-head { flex-direction: column; align-items: flex-start; }
}
@media (prefers-reduced-motion: reduce) {
  .pl-card, .pl-panel, .pl-row, .pl-step, .pl-arrow, .pl-hero::before {
    animation: none;
    transition: none;
  }
  [data-testid="stBaseButton-primary"] { transition: none; }
}
</style>"""
