STYLE = """<style>
@keyframes pl-rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0b2a4a 0%, #0e4a5a 100%); }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #e6f2f5; }
.pl-brand { font-size: 1.7rem; font-weight: 700; color: #ffffff; margin-bottom: 14px; }
[data-baseweb="tab-list"] { gap: 8px; }
[data-baseweb="tab"] { border-radius: 999px; padding: 6px 18px; }
[data-baseweb="tab"][aria-selected="true"] { background: #0f766e; color: #ffffff; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none; }
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
@media (prefers-reduced-motion: reduce) {
  .pl-card, .pl-panel, .pl-row { animation: none; transition: none; }
}
</style>"""
