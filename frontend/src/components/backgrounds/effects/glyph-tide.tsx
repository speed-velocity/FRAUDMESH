import type { CSSProperties } from "react";

type GlyphTideProps = { className?: string; style?: CSSProperties };

/** Decorative, non-interactive tide of evidence-network glyphs for the landing hero. */
export function GlyphTide({ className = "", style }: GlyphTideProps) {
  return <div className={`glyph-tide ${className}`.trim()} aria-hidden="true" style={style}>
    <svg viewBox="0 0 1200 360" preserveAspectRatio="none" focusable="false">
      <path className="glyph-tide-line glyph-tide-line-a" d="M-40 276 C120 178 210 332 382 238 S650 150 820 244 S1060 344 1240 194" />
      <path className="glyph-tide-line glyph-tide-line-b" d="M-40 316 C122 218 226 350 398 270 S666 182 840 270 S1080 366 1240 226" />
      <path className="glyph-tide-line glyph-tide-line-c" d="M-40 236 C116 142 226 292 392 208 S654 112 832 210 S1072 300 1240 156" />
      <g className="glyph-tide-glyphs">
        <circle cx="166" cy="222" r="7" /><circle cx="166" cy="222" r="19" />
        <circle cx="508" cy="174" r="7" /><circle cx="508" cy="174" r="19" />
        <circle cx="874" cy="242" r="7" /><circle cx="874" cy="242" r="19" />
        <path d="M166 222 L508 174 L874 242" />
        <path d="M508 174 L508 92 M874 242 L874 134" />
      </g>
    </svg>
  </div>;
}
