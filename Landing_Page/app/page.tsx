'use client'

import { FormEvent, useEffect, useRef, useState } from 'react'
import { ArrowDownRight, ArrowUpRight, Check, Compass, Copy, Layers3, LoaderCircle, LogIn, Mail, Menu, MoveUpRight, Sparkles, Terminal, UserRound, X } from 'lucide-react'

const logo = '/logo-without-text-removebg-preview.png'
const themes = ['MARVEL-INSPIRED', 'CYBERPUNK NEON', 'SCANDINAVIAN MINIMAL', 'LUXURY FASHION', 'COZY ARTISAN', 'BOTANICAL', 'RETRO ARCADE']

function Reveal({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const node = ref.current
    if (!node) return
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        node.style.setProperty('--reveal-delay', `${delay}ms`)
        node.classList.add('is-visible')
        observer.disconnect()
      }
    }, { threshold: 0.1 })
    observer.observe(node)
    return () => observer.disconnect()
  }, [delay])
  return <div ref={ref} className={`reveal ${className}`}>{children}</div>
}

function MagneticButton({ children, href, onClick }: { children: React.ReactNode; href?: string; onClick?: () => void }) {
  const ref = useRef<HTMLAnchorElement & HTMLButtonElement>(null)
  const move = (event: React.MouseEvent) => {
    if (!ref.current || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const rect = ref.current.getBoundingClientRect()
    ref.current.style.setProperty('--mag-x', `${(event.clientX - rect.left - rect.width / 2) * 0.12}px`)
    ref.current.style.setProperty('--mag-y', `${(event.clientY - rect.top - rect.height / 2) * 0.12}px`)
  }
  const reset = () => {
    if (!ref.current) return
    ref.current.style.setProperty('--mag-x', '0px')
    ref.current.style.setProperty('--mag-y', '0px')
  }

  if (href) {
    return (
      <a ref={ref as any} href={href} onMouseMove={move} onMouseLeave={reset} className="magnetic-button button-primary">
        {children}
      </a>
    )
  }

  return (
    <button ref={ref as any} onClick={onClick} onMouseMove={move} onMouseLeave={reset} className="magnetic-button button-primary">
      {children}
    </button>
  )
}

function Starfield({ scrollY }: { scrollY: number }) {
  return (
    <div className="starfield" aria-hidden="true" style={{ transform: `translate3d(0, ${scrollY * 0.05}px, 0)` }}>
      <div className="stars stars-one" />
      <div className="stars stars-two" />
      <div className="stars stars-three" />
      <div className="star-nebula" />
    </div>
  )
}

function OrbitVisual({ scrollY }: { scrollY: number }) {
  return (
    <div className="orbit-visual" aria-hidden="true" style={{ transform: `translate3d(0, ${scrollY * 0.08}px, 0)` }}>
      <div className="orbit-halo" />
      <svg viewBox="0 0 620 620" className="orbit-svg">
        <defs>
          <linearGradient id="chrome" x1="0" x2="1">
            <stop stopColor="#5d666b" />
            <stop offset=".5" stopColor="#f4f6f5" />
            <stop offset="1" stopColor="#788187" />
          </linearGradient>
          <filter id="softGlow">
            <feGaussianBlur stdDeviation="9" />
          </filter>
          <path id="orbitPathA" d="M310 88a222 222 0 1 1 0 444a222 222 0 1 1 0-444" />
          <path id="orbitPathB" d="M310 182a285 128 -28 1 1 0 256a285 128 -28 1 1 0-256" />
        </defs>
        <circle className="orbit-line orbit-line-one" cx="310" cy="310" r="222" />
        <ellipse className="orbit-line orbit-line-two" cx="310" cy="310" rx="285" ry="128" transform="rotate(-28 310 310)" />
        <ellipse className="orbit-line orbit-line-three" cx="310" cy="310" rx="190" ry="290" transform="rotate(32 310 310)" />
        <path className="orbit-geometry" d="M88 310h444M150 189l320 242M184 70l252 480" />
        <circle className="orbit-ring" cx="310" cy="310" r="92" />
        <circle className="orbit-ring-inner" cx="310" cy="310" r="80" />
        <circle className="orbit-node orbit-node-one" r="7" fill="url(#chrome)">
          <animateMotion dur="14s" repeatCount="indefinite" rotate="auto"><mpath href="#orbitPathA" /></animateMotion>
        </circle>
        <circle className="orbit-node orbit-node-two" r="6" fill="#c6a76f">
          <animateMotion dur="19s" repeatCount="indefinite" rotate="auto" begin="-7s"><mpath href="#orbitPathB" /></animateMotion>
        </circle>
        <circle className="orbit-node orbit-node-three" r="5" fill="url(#chrome)">
          <animateMotion dur="23s" repeatCount="indefinite" rotate="auto" begin="-12s"><mpath href="#orbitPathA" /></animateMotion>
        </circle>
      </svg>
      <div className="orbit-logo">
        <img src={logo} alt="Project Infra Logo" />
      </div>
      <span className="orbit-caption caption-top">SYSTEM / ONLINE</span>
      <span className="orbit-caption caption-bottom">THE CREATIVE BRIEF<br />RECONSIDERED</span>
    </div>
  )
}

export default function Page() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const [scrollY, setScrollY] = useState(0)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState('')
  const [authOpen, setAuthOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('signup')
  const [authName, setAuthName] = useState('')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [authError, setAuthError] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  const [currentUser, setCurrentUser] = useState<{ name: string; email: string } | null>(null)
  const [copiedEmail, setCopiedEmail] = useState(false)
  const [activeTab, setActiveTab] = useState<'prompt' | 'infra'>('infra')

  const contactEmail = 'admin.team.infra@gmail.com'

  useEffect(() => {
    const handleScroll = () => {
      const currentY = window.scrollY
      setScrollY(currentY)
      setScrolled(currentY > 40)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    fetch('/api/auth/me').then((response) => response.json()).then((data) => setCurrentUser(data.user || null)).catch(() => undefined)
  }, [])

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFormError('')
    setSubmitting(true)
    try {
      const response = await fetch('/api/waitlist', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, email }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Could not join the list.')
      setSubmitted(true)
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'Could not join the list.')
    } finally {
      setSubmitting(false)
    }
  }

  const submitAuth = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setAuthError('')
    setAuthLoading(true)
    try {
      const response = await fetch(`/api/auth/${authMode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: authName, email: authEmail, password: authPassword }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'Authentication failed.')
      setCurrentUser(data.user)
      setAuthOpen(false)
      setAuthPassword('')
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Authentication failed.')
    } finally {
      setAuthLoading(false)
    }
  }

  const logout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' })
    setCurrentUser(null)
  }

  const copyContactEmail = () => {
    navigator.clipboard.writeText(contactEmail)
    setCopiedEmail(true)
    setTimeout(() => setCopiedEmail(false), 2500)
  }

  return (
    <main className="site-shell">
      <Starfield scrollY={scrollY} />
      <div className="scanline" aria-hidden="true" />
      <div className="mesh" aria-hidden="true" style={{ transform: `translate3d(0, ${scrollY * 0.1}px, 0)` }} />

      {/* Floating Translucent Scroll-Aware Header */}
      <header className={`header-nav-wrapper ${scrolled ? 'is-scrolled' : ''}`}>
        <nav className="nav container">
          <a href="#top" className="wordmark" aria-label="Infra home">
            <img src={logo} alt="Project Infra logo" />
            <span>INFRA / FORMA</span>
          </a>
          <div className={`nav-links ${menuOpen ? 'nav-open' : ''}`}>
            <a href="#process" onClick={() => setMenuOpen(false)}>Method</a>
            <a href="#output" onClick={() => setMenuOpen(false)}>Artifacts</a>
            <a href="#difference" onClick={() => setMenuOpen(false)}>Difference</a>
            <a href="#note" onClick={() => setMenuOpen(false)}>Founder's Note</a>
            <a href="#contact" onClick={() => setMenuOpen(false)}>Contact</a>
            {currentUser ? <button className="nav-account" onClick={logout}><UserRound size={14} /> {currentUser.name}</button> : <button className="nav-account" onClick={() => { setAuthMode('login'); setAuthOpen(true); setMenuOpen(false) }}><LogIn size={14} /> Sign in</button>}
            <a href="#access" onClick={() => setMenuOpen(false)} className="nav-cta">
              Join list <ArrowUpRight size={14} />
            </a>
          </div>
          <button
            className="menu-toggle"
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </nav>
      </header>

      {/* Hero Section */}
      <section id="top" className="hero container">
        <div className="hero-kicker">
          <span className="live-dot" /> DESIGN DIRECTION, STRUCTURED <span className="kicker-line" />
        </div>
        <div className="hero-layout">
          <div className="hero-copy-column">
            <h1>Stop staring<br /><em>at the blank canvas.</em></h1>
          <p className="hero-copy">Forma by Infra turns a short brief, a visual reference, or a live URL into a sharper, more buildable product direction.</p>
            <div className="hero-actions">
              <MagneticButton href="#access">Meet Forma <ArrowUpRight size={16} /></MagneticButton>
              <a href="#process" className="text-link">Explore the method <ArrowDownRight size={16} /></a>
            </div>
          </div>
          <OrbitVisual scrollY={scrollY} />
        </div>
        <div className="hero-index">01 <span>/</span> 07</div>
      </section>

      {/* Ticker Bar */}
      <div className="ticker-wrap" aria-label="Themes Project Infra can handle">
        <div className="ticker">
          {[...themes, ...themes].map((theme, index) => (
            <span key={`${theme}-${index}`}><i /> {theme}</span>
          ))}
        </div>
      </div>

      {/* Section 01: Method (Spacious Frozen Glass Cards Grid) */}
      <section id="process" className="section container process-section-v2">
        <Reveal className="process-header-v2">
          <span className="eyebrow">01 / THE METHOD</span>
          <h2>From a feeling<br />to a <em>framework.</em></h2>
          <p className="process-subtitle">Less prompting. More direction. A structured path from initial creative instinct to production-ready design decisions.</p>
        </Reveal>

        <div className="process-grid-v2">
          {[
            { n: '01', icon: Compass, title: 'Describe the feeling', copy: 'Tell us what you are building and the visual world it should inhabit. Specify mood, tone, or reference points.' },
            { n: '02', icon: Layers3, title: 'Get the blueprint', copy: 'Receive a complete, structured point of view: exact typography pairings, color hex tokens, motion specs, and layout systems.' },
            { n: '03', icon: MoveUpRight, title: 'Start with conviction', copy: 'Skip the blank-canvas inertia. Build from a cohesive design direction instead of endless guess-and-check prompts.' }
          ].map(({ n, icon: Icon, title, copy }, i) => (
            <Reveal className="process-card-v2 glass-panel" delay={i * 120} key={n}>
              <div className="card-badge-row">
                <span className="step-tag">{n}</span>
                <div className="icon-glow-box"><Icon size={22} strokeWidth={1.5} /></div>
              </div>
              <h3>{title}</h3>
              <p>{copy}</p>
            </Reveal>
          ))}
        </div>
      </section>

      {/* Section 02: Artifacts */}
      <section id="output" className="section output-section">
        <div className="container">
          <Reveal className="output-heading">
            <div>
          <span className="eyebrow accent">02 / FORMA OUTPUT — BUILT TO SHIP</span>
              <h2>Specific enough<br />to <em>build from.</em></h2>
            </div>
            <p>Not a generic mock. A practical design system with real parameters, rationale, and front-end-ready code.</p>
          </Reveal>
          <div className="output-grid">
            {[
              { cls: 'dark-card', id: '001', title: <>Comics, but<br /><em>not childish.</em></>, rows: [['PALETTE', 'Signal / Ink / Paper'], ['TYPE', 'Condensed grotesk + mono'], ['MOTION', 'Snappy / 180ms / ease-out']] },
              { cls: 'cream-card', id: '002', title: <>Quiet luxury<br /><em>for objects.</em></>, rows: [['NAVIGATION', 'Floating, minimal, left-weighted'], ['LAYOUT', 'Wide margins / editorial rhythm'], ['DETAIL', 'Hairline rules / high contrast']] },
              { cls: 'olive-card', id: '003', title: <>Grow slow.<br /><em>Stay curious.</em></>, rows: [['ACCENT', 'Living green / #B7D46A'], ['BACKGROUND', 'Warm, textured, open'], ['TRANSITION', 'Organic / 600ms / soft']] }
            ].map((card, i) => (
              <Reveal className={`spec-card glass-panel ${card.cls}`} delay={i * 100} key={card.id}>
                <div className="card-top"><span>BRIEF / {card.id}</span><span>{card.id} — 03</span></div>
                <h3>{card.title}</h3>
                <div className="spec-list">
                  {card.rows.map(([label, value]) => (
                    <div key={label}><span>{label}</span><b>{value}</b></div>
                  ))}
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Section 03: The Difference (Interactive Showcase) */}
      <section id="difference" className="section difference-section-v2 container">
        <Reveal className="difference-intro-v2">
          <span className="eyebrow">03 / THE DIFFERENCE</span>
          <h2>Images are easy.<br /><em>Direction is rare.</em></h2>
          <p>Generic prompt tools output flat pixel surfaces to react to. Infra gives you the decision architecture underneath — real hex tokens, verified timing curves, typography pairings, and layout choices.</p>
        </Reveal>

        <Reveal className="showcase-card-v2 glass-panel" delay={150}>
          <div className="showcase-tabs">
            <button
              className={`tab-btn ${activeTab === 'prompt' ? 'active' : ''}`}
              onClick={() => setActiveTab('prompt')}
            >
              <Sparkles size={15} /> Unstructured Image Prompting
            </button>
            <button
              className={`tab-btn ${activeTab === 'infra' ? 'active' : ''}`}
              onClick={() => setActiveTab('infra')}
            >
              <Terminal size={15} /> Infra Structured Direction Engine
            </button>
          </div>

          <div className="showcase-content">
            {activeTab === 'prompt' ? (
              <div className="showcase-pane prompt-pane">
                <div className="pane-header">
                  <span className="pane-tag">OUTPUT: FLAT MOCKUP IMAGE</span>
                  <span className="status-dot red" />
                </div>
                <div className="prompt-mock-box">
                  <code>"Design a modern luxury website layout with gold accents and dark vibe..."</code>
                  <div className="mock-result-stub">
                    <p className="stub-note">⚠️ Result: A flat PNG image file. Zero CSS variables, no font pairings, no layout grid, no animation curves, no code handoff.</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="showcase-pane infra-pane">
                <div className="pane-header">
                  <span className="pane-tag">OUTPUT: PRODUCTION DESIGN SYSTEM TOKENS</span>
                  <span className="status-dot green" />
                </div>
                <div className="infra-code-box">
                  <pre>
                    {`// Project Infra Direction Engine Token Spec
{
  "theme": "Quiet Luxury Editorial",
  "palette": {
    "background": "#06080C",
    "surface": "rgba(255, 255, 255, 0.05)",
    "gold": "#D4AF37",
    "silver": "#E2E8E6"
  },
  "typography": {
    "display": "Playfair Display / Georgia",
    "body": "Inter / System Sans",
    "mono": "JetBrains Mono"
  },
  "motion": {
    "transition": "600ms cubic-bezier(0.16, 1, 0.3, 1)"
  }
}`}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </Reveal>
      </section>

      {/* Section 04: Founder's Note */}
      <section id="note" className="section founder-section container">
        <Reveal className="founder-header">
          <span className="eyebrow">04 / FOUNDER'S NOTE</span>
          <h2>Built out of <em>necessity.</em></h2>
        </Reveal>

        <Reveal className="founder-card glass-panel" delay={120}>
          <div className="founder-quote">
            <p>
              "We started Infra because modern website creation had split into two frustrating extremes: overwhelming blank canvases, or AI prompt generators that stop at an un-customizable picture."
            </p>
            <p>
              "Forma bridges the gap between creative instinct and production implementation, giving teams an opinionated, high-craft foundation to build from day one. See better. Design smarter."
            </p>
          </div>
          <div className="founder-footer">
            <div className="founder-info">
              <div className="founder-avatar-box">
                <img src={logo} alt="Project Infra Mark" />
              </div>
              <div>
                <strong className="founder-name">Infra / Forma</strong>
                <span className="founder-title">Design Systems & Engineering</span>
              </div>
            </div>
            <div className="signature-tag">INFRA / 2026</div>
          </div>
        </Reveal>
      </section>

      {/* Section 05: Contact Section */}
      <section id="contact" className="section contact-section container">
        <Reveal className="contact-header">
          <span className="eyebrow">05 / GET IN TOUCH</span>
          <h2>Have questions or <em>ideas?</em></h2>
            <p className="contact-desc">We are building Forma for designers, developers, founders, and teams who want better decisions before they write the first line of UI.</p>
        </Reveal>

        <Reveal className="contact-card glass-panel" delay={120}>
          <div className="contact-info-row">
            <div className="contact-icon-badge">
              <Mail size={24} />
            </div>
            <div className="contact-text-group">
              <span className="contact-label">DIRECT EMAIL ADDRESS</span>
              <a href={`mailto:${contactEmail}`} className="contact-email-link">
                {contactEmail}
              </a>
            </div>
          </div>

          <div className="contact-actions-row">
            <button className="copy-btn" onClick={copyContactEmail}>
              {copiedEmail ? <Check size={16} className="text-gold" /> : <Copy size={16} />}
              {copiedEmail ? 'Email Copied!' : 'Copy Email Address'}
            </button>
            <a href={`mailto:${contactEmail}`} className="send-mail-btn">
              Send Email Direct <ArrowUpRight size={16} />
            </a>
          </div>

          <div className="contact-meta-strip">
            <span>⚡ AVERAGE RESPONSE TIME: &lt; 24 HOURS</span>
            <span>OPEN FOR FEEDBACK & IDEAS</span>
          </div>
        </Reveal>
      </section>

      {/* Section 06: Access / Early Access Signup (Logo Removed as requested) */}
      <section id="access" className="access-section">
        <div className="container access-inner-clean">
          <Reveal>
            <span className="eyebrow accent">06 / EARLY ACCESS</span>
            <h2>Build from<br /><em>a point of view.</em></h2>
            <p>Join the Forma early-access list. We will send the first invite when the model is ready for your workflow.</p>
            <form onSubmit={submit} className="signup-form glass-panel">
              {submitted ? (
                <div className="success"><Check size={18} /> You are on the list. We will be in touch.</div>
              ) : (
                <>
                  <input aria-label="Your name" type="text" placeholder="Your name" value={name} onChange={(e) => setName(e.target.value)} required />
                  <input
                    aria-label="Email address"
                    type="email"
                    placeholder="Your email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                  <button type="submit" disabled={submitting}>{submitting ? <><LoaderCircle size={16} className="spin" /> Saving...</> : <>Request access <ArrowUpRight size={16} /></>}</button>
                </>
              )}
            </form>
            {formError && <p className="form-error">{formError}</p>}
            <small>No spam. Just a note when it is ready.</small>
          </Reveal>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer container">
        <a href="#top" className="wordmark">
          <img src={logo} alt="Project Infra logo" />
          <span>INFRA / FORMA</span>
        </a>
        <a href={`mailto:${contactEmail}`} className="footer-email">{contactEmail}</a>
        <span>© 2026</span>
      </footer>

      {authOpen && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.currentTarget === event.target) setAuthOpen(false) }}>
          <section className="auth-modal glass-panel" role="dialog" aria-modal="true" aria-labelledby="auth-title">
            <button className="modal-close" aria-label="Close authentication dialog" onClick={() => setAuthOpen(false)}><X size={18} /></button>
            <span className="eyebrow accent">INFRA / FORMA</span>
            <h2 id="auth-title">{authMode === 'signup' ? 'Save your place.' : 'Welcome back.'}</h2>
            <p>{authMode === 'signup' ? 'Create an account and get the first Forma invite.' : 'Sign in to keep your early-access details in one place.'}</p>
            <form onSubmit={submitAuth} className="auth-form">
              {authMode === 'signup' && <input aria-label="Name" type="text" placeholder="Name" value={authName} onChange={(e) => setAuthName(e.target.value)} required />}
              <input aria-label="Email" type="email" placeholder="Email address" value={authEmail} onChange={(e) => setAuthEmail(e.target.value)} required />
              <input aria-label="Password" type="password" placeholder="Password (8+ characters)" value={authPassword} onChange={(e) => setAuthPassword(e.target.value)} minLength={8} required />
              {authError && <p className="form-error">{authError}</p>}
              <button type="submit" className="auth-submit" disabled={authLoading}>{authLoading ? <><LoaderCircle size={16} className="spin" /> Working...</> : authMode === 'signup' ? 'Create account' : 'Sign in'}</button>
            </form>
            <button className="auth-switch" onClick={() => { setAuthMode(authMode === 'signup' ? 'login' : 'signup'); setAuthError('') }}>{authMode === 'signup' ? 'Already have an account? Sign in' : 'New to Forma? Create an account'}</button>
          </section>
        </div>
      )}
    </main>
  )
}
