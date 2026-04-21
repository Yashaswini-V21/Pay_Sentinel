import { useState, useEffect } from 'react'
import { Link } from '@tanstack/react-router'
import { Logo } from './Logo'
import { Menu, X, ArrowRight } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export function SiteHeader() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  // Track scroll for a cinematic blur transition
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { label: 'Platform', href: '#how' },
    { label: 'Intelligence', href: '#features' },
    { label: 'Enterprise', href: '#pricing' },
  ]

  return (
    <header 
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-500 border-b ${
        scrolled 
          ? 'bg-background/70 backdrop-blur-3xl border-primary/20 shadow-[0_4px_30px_rgba(0,0,0,0.3)]' 
          : 'bg-transparent border-transparent'
      }`}
    >
      {/* Stark Tech glowing accent line at the bottom of the header */}
      <div className={`absolute bottom-0 left-0 h-[1px] w-full bg-gradient-to-r from-transparent via-primary/50 to-transparent transition-opacity duration-700 ${scrolled ? 'opacity-100' : 'opacity-0'}`} />

      <div className="max-w-[1400px] mx-auto h-20 px-6 md:px-12 flex items-center justify-between">
        
        {/* Logo / Brand - Stark Style */}
        <Link to="/" className="flex items-center gap-4 group cursor-pointer z-10 p-2 -ml-2">
          <div className="relative flex items-center justify-center transition-transform duration-500 group-hover:scale-110">
            {/* Animated Hexagon/Tech Border */}
            <div className="absolute inset-0 rounded-lg border border-primary/30 rotate-45 group-hover:rotate-90 transition-transform duration-700" />
            <div className="absolute inset-0 rounded-lg border border-accent/20 -rotate-45 group-hover:-rotate-90 transition-transform duration-700" />
            <Logo className="w-7 h-7 text-white relative z-10 drop-shadow-[0_0_15px_rgba(255,255,255,0.8)]" />
          </div>
          <div className="flex flex-col">
            <span className="heading-font font-black text-xl tracking-[0.15em] uppercase text-white shadow-primary/20 drop-shadow-md">
              Pay<span className="text-primary font-light">Sentinel</span>
            </span>
            <span className="font-mono text-[9px] text-primary/70 tracking-[0.3em] uppercase opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform -translate-y-1 group-hover:translate-y-0">
              SYS.SECURE.LINK
            </span>
          </div>
        </Link>

        {/* Desktop Nav - Minimal Hover Lines */}
        <nav className="hidden md:flex items-center gap-10 absolute left-1/2 transform -translate-x-1/2">
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="relative text-xs font-mono tracking-widest uppercase text-muted-foreground hover:text-white transition-colors duration-300 py-2 group"
            >
              {item.label}
              <span className="absolute bottom-0 left-0 w-0 h-[2px] bg-primary transition-all duration-300 group-hover:w-full" />
            </a>
          ))}
        </nav>

        {/* CTA Area - Holographic UI styling */}
        <div className="hidden md:flex items-center gap-6 z-10">
          <a href="#" className="font-mono text-xs tracking-widest uppercase text-muted-foreground hover:text-accent transition-colors">
            [ Portal Login ]
          </a>
          <Link 
            to="/dashboard" 
            className="group relative inline-flex items-center justify-center gap-3 overflow-hidden bg-primary/10 border border-primary/30 px-6 py-2.5 backdrop-blur-md transition-all duration-500 hover:border-primary hover:bg-primary/20 hover:shadow-[0_0_25px_rgba(139,92,246,0.5)]"
          >
            <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/50" />
            <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/50" />
            <span className="relative z-10 font-mono text-xs font-bold tracking-[0.2em] uppercase text-white">
              Launch System
            </span>
            <ArrowRight size={14} className="text-primary group-hover:translate-x-1 transition-transform group-hover:text-white" />
          </Link>
        </div>

        {/* Mobile Menu Button - Tech Icon */}
        <button
          className="md:hidden z-50 p-2 text-white hover:text-primary transition-colors focus:outline-none"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X size={28} /> : <Menu size={28} />}
        </button>
      </div>

      {/* Cyberpunk Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div 
            initial={{ clipPath: 'inset(0 0 100% 0)' }}
            animate={{ clipPath: 'inset(0 0 0% 0)' }}
            exit={{ clipPath: 'inset(0 0 100% 0)' }}
            transition={{ duration: 0.5, ease: [0.76, 0, 0.24, 1] }}
            className="fixed inset-0 z-40 bg-background/95 backdrop-blur-3xl flex flex-col justify-center"
          >
            {/* Cyber Grid Background */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none" />

            <nav className="flex flex-col items-start gap-8 px-12 relative z-10">
              {navItems.map((item, idx) => (
                <motion.a
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + (idx * 0.1) }}
                  key={item.href}
                  href={item.href}
                  className="group relative text-4xl md:text-6xl font-black heading-font text-transparent bg-clip-text bg-gradient-to-r from-white to-white/50 hover:to-primary transition-all duration-300 uppercase tracking-tighter"
                  onClick={() => setMobileOpen(false)}
                >
                  {item.label}
                  <span className="absolute -left-6 top-1/2 -translate-y-1/2 w-3 h-3 border border-primary rotate-45 opacity-0 group-hover:opacity-100 transition-opacity" />
                </motion.a>
              ))}
              
              <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                  className="flex flex-col gap-6 mt-12 w-full border-t border-white/10 pt-12"
              >
                  <Link to="/dashboard" className="font-mono text-sm tracking-widest text-primary hover:text-white uppercase flex items-center gap-4">
                    <span className="w-8 h-[1px] bg-primary" /> Boot Dashboard System
                  </Link>
                  <button className="font-mono text-sm tracking-widest text-muted-foreground hover:text-white uppercase flex items-center gap-4 text-left">
                    <span className="w-8 h-[1px] bg-muted-foreground" /> Access Client Portal
                  </button>
              </motion.div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
