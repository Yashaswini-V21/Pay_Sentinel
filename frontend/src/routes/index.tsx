import { motion } from 'framer-motion'
import { Link } from '@tanstack/react-router'
import { Play, Shield, Volume2, TrendingUp, Upload, Smartphone, Star, ArrowRight } from 'lucide-react'
import { RiskBadge } from '@/components/RiskBadge'
import { BilingualText } from '@/components/BilingualText'

export default function Landing() {
  return (
    <div className="w-full overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-20">
        {/* Aurora background */}
        <div className="absolute inset-0 aurora-glow opacity-30" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--primary)_0%,_transparent_50%)] opacity-5" />

        <div className="container-main relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Text */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              {/* Badge */}
              <motion.div
                className="inline-block mb-8"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 }}
              >
                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30 w-fit">
                  <span className="w-2 h-2 bg-accent rounded-full animate-pulse" />
                  <span className="text-xs font-semibold text-primary">
                    🟢 Live · Built for Bengaluru merchants
                  </span>
                </div>
              </motion.div>

              {/* Heading */}
              <h1 className="mb-6 text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
                UPI fraud detection that speaks{' '}
                <span className="text-gradient">your language</span>
              </h1>

              {/* Subheading */}
              <p className="text-lg text-muted-foreground mb-4 max-w-lg">
                Explainable AI for small merchants. Detect suspicious transactions instantly. Get alerts in English or Kannada.
              </p>
              <BilingualText
                en="Trusted by kirana stores, cafés & clinics"
                kn="ಕಿರಾಣ ಅಂಗಡಿ, ಕಾಫೆ ಮತ್ತು ಕ್ಲಿನಿಕ್ ಮೂಲಕ ವಿಶ್ವಸ್ತ"
                className="text-sm text-muted-foreground mb-8"
                block
              />

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <Link to="/dashboard" className="btn-primary inline-flex items-center justify-center gap-2">
                  Open Dashboard
                  <ArrowRight size={16} />
                </Link>
                <button className="btn-secondary inline-flex items-center justify-center gap-2">
                  <Play size={16} />
                  Watch 60s demo
                </button>
              </div>
            </motion.div>

            {/* Right: Animated mockup */}
            <motion.div
              className="relative hidden lg:block h-96"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              {/* Dashboard mockup */}
              <div className="glass p-6 rounded-2xl border border-border h-full overflow-hidden">
                <div className="space-y-4">
                  <div className="h-8 bg-muted rounded animate-pulse" />
                  <div className="grid grid-cols-2 gap-3">
                    <div className="h-12 bg-muted rounded animate-pulse" />
                    <div className="h-12 bg-muted rounded animate-pulse" />
                  </div>
                  <div className="space-y-2">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-6 bg-muted rounded animate-pulse" />
                    ))}
                  </div>
                </div>
              </div>

              {/* Floating alert cards */}
              <motion.div
                className="absolute -top-4 -left-12 glass p-4 rounded-lg border border-destructive/50 bg-destructive/5 max-w-xs shadow-lg"
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-destructive rounded-full animate-pulse" />
                  <div>
                    <p className="text-xs font-semibold">High risk</p>
                    <p className="text-sm font-mono">₹49,500 @ 2 AM</p>
                  </div>
                </div>
              </motion.div>

              <motion.div
                className="absolute bottom-8 -right-8 glass p-4 rounded-lg border border-accent/50 bg-accent/5 max-w-xs shadow-lg"
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 3, repeat: Infinity, delay: 1 }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-accent rounded-full" />
                  <div>
                    <p className="text-xs font-semibold">Safe</p>
                    <p className="text-sm font-mono">₹150 - Regular vendor</p>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Bento */}
      <section id="features" className="py-24 border-t border-border">
        <div className="container-main">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="mb-4">Powerful features</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to protect your business from UPI fraud
            </p>
          </motion.div>

          {/* 6-card Bento grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Card 1: Isolation Forest */}
            <motion.div
              className="glass p-8 rounded-2xl border border-border lg:col-span-2 lg:row-span-2"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <Shield className="w-8 h-8 text-primary mb-4" />
              <h3 className="text-xl font-bold mb-3">Isolation Forest ML</h3>
              <p className="text-muted-foreground mb-4">
                Unsupervised anomaly detection. No fraud labels needed.
              </p>
              <div className="bg-card/50 rounded-lg p-4 text-xs font-mono text-accent">
                <p>Model: scikit-learn IsolationForest</p>
                <p>Accuracy: 94% on test set</p>
              </div>
            </motion.div>

            {/* Card 2: SHAP */}
            <motion.div
              className="glass p-6 rounded-2xl border border-border"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
            >
              <TrendingUp className="w-6 h-6 text-primary mb-3" />
              <h3 className="font-bold mb-2">SHAP Explainability</h3>
              <p className="text-sm text-muted-foreground">
                Understand why each transaction flagged
              </p>
            </motion.div>

            {/* Card 3: Kannada Alerts */}
            <motion.div
              className="glass p-6 rounded-2xl border border-border"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              <Volume2 className="w-6 h-6 text-accent mb-3" />
              <h3 className="font-bold mb-2">Voice Alerts</h3>
              <p className="text-sm text-muted-foreground">
                Kannada voice alerts via gTTS
              </p>
            </motion.div>

            {/* Card 4: Fingerprinting */}
            <motion.div
              className="glass p-6 rounded-2xl border border-border"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              <Shield className="w-6 h-6 text-primary mb-3" />
              <h3 className="font-bold mb-2">Fingerprinting</h3>
              <p className="text-sm text-muted-foreground">
                Learn each merchant's behavior pattern
              </p>
            </motion.div>

            {/* Card 5: CSV Import */}
            <motion.div
              className="glass p-6 rounded-2xl border border-border"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
            >
              <Upload className="w-6 h-6 text-primary mb-3" />
              <h3 className="font-bold mb-2">One-click Import</h3>
              <p className="text-sm text-muted-foreground">
                CSV from PhonePe, GPay, Paytm
              </p>
            </motion.div>

            {/* Card 6: Offline */}
            <motion.div
              className="glass p-6 rounded-2xl border border-border"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
            >
              <Smartphone className="w-6 h-6 text-accent mb-3" />
              <h3 className="font-bold mb-2">Offline PWA</h3>
              <p className="text-sm text-muted-foreground">
                Works on weak connections
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="py-24 border-t border-border">
        <div className="container-main">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="mb-4">How it works</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Three simple steps to protect your business
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-12">
            {[
              { num: '01', title: 'Upload transactions', desc: 'Import your UPI transaction history' },
              { num: '02', title: 'AI detects anomalies', desc: 'Machine learning identifies suspicious patterns' },
              { num: '03', title: 'Get instant alerts', desc: 'Receive Kannada voice alerts for high-risk transactions' },
            ].map((step, i) => (
              <motion.div
                key={i}
                className="relative"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                {i < 2 && (
                  <div className="hidden md:block absolute top-12 left-[60%] w-[40%] h-1 bg-gradient-to-r from-primary to-primary/0" />
                )}
                <div className="mb-6">
                  <div className="text-5xl font-bold text-primary/30 font-mono mb-4">
                    {step.num}
                  </div>
                  <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                  <p className="text-muted-foreground">{step.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 border-t border-border">
        <div className="container-main">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="mb-4">Transparent pricing</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Start free. Scale as you grow.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { name: 'Free', price: '₹0', features: ['Up to 100 transactions/month', 'Kannada + English', 'Basic ML detection'] },
              { name: 'Pro', price: '₹299', sub: '/month', features: ['Unlimited transactions', 'Advanced SHAP explanations', 'Voice alerts', 'Email support'], highlight: true },
              { name: 'Business', price: '₹999', sub: '/month', features: ['Everything in Pro', 'API access', 'Priority support', 'Custom integrations'] },
            ].map((plan, i) => (
              <motion.div
                key={i}
                className={`glass p-8 rounded-2xl border ${
                  plan.highlight
                    ? 'glow-border lg:scale-105'
                    : 'border-border'
                }`}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                {plan.highlight && (
                  <div className="bg-primary/20 text-primary text-xs font-semibold px-3 py-1 rounded-full w-fit mb-4">
                    Most popular
                  </div>
                )}
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  {plan.sub && <span className="text-muted-foreground">{plan.sub}</span>}
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f, fi) => (
                    <li key={fi} className="text-sm text-muted-foreground flex items-start gap-3">
                      <Star size={14} className="text-accent mt-1 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <button className={plan.highlight ? 'btn-primary w-full' : 'btn-secondary w-full'}>
                  Get started
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="py-16 border-t border-border">
        <div className="container-main glass p-12 rounded-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold">Suspicious transaction?</h2>
          <p className="text-lg text-muted-foreground mb-6">
            Call National Cyber Crime Helpline <span className="text-primary font-bold">1930</span> or visit{' '}
            <a href="https://cybercrime.gov.in" target="_blank" rel="noreferrer" className="text-primary hover:underline">
              cybercrime.gov.in
            </a>
          </p>
          <Link to="/dashboard" className="btn-primary">
            Start free today
          </Link>
        </div>
      </section>
    </div>
  )
}
