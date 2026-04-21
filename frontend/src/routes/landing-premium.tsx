import { motion } from 'framer-motion'
import { Check, Shield, Lock, Zap, BarChart3, Volume2, ArrowRight } from 'lucide-react'
import { FraudShieldGraphic, TransactionFlowGraphic, RiskMeterGraphic, DataPointsGraphic, MerchantShieldGraphic } from '../components/AnimatedGraphics'
import { Link } from '@tanstack/react-router'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: 'easeOut' },
  },
}

export default function Landing() {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden">

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden pt-20">
          <div className="absolute inset-0 bg-background" />

          {/* Stark Tech Grid Background */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:3rem_3rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)]" />

          {/* Ambient Glows */}
          <div className="absolute top-1/4 left-1/4 w-[40vw] h-[40vw] bg-primary/10 rounded-full blur-[100px] pointer-events-none mix-blend-screen" />
          <div className="absolute bottom-1/4 right-1/4 w-[30vw] h-[30vw] bg-accent/10 rounded-full blur-[100px] pointer-events-none mix-blend-screen" />

          {/* HUD Tech Lines & Markers */}
          <div className="absolute left-10 top-1/2 -translate-y-1/2 hidden lg:flex flex-col gap-6 opacity-30">
            {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="w-1 h-8 border-l-2 border-primary/40 relative">
                    <span className="absolute -left-6 top-1/2 -translate-y-1/2 font-mono text-[8px] tracking-[0.2em] transform -rotate-90">0{i}</span>
                </div>
            ))}
          </div>

          <div className="container-main relative z-10 grid lg:grid-cols-2 gap-12 items-center px-4 md:px-8">
            <motion.div
              initial="hidden"
              animate="visible"
              variants={containerVariants}
              className="mt-12 lg:mt-0 relative"
            >
              {/* Corner brackets */}
              <div className="absolute -top-8 -left-8 w-16 h-16 border-t-2 border-l-2 border-primary/30 opacity-50 hidden md:block" />
              <div className="absolute -bottom-8 -left-8 w-16 h-16 border-b-2 border-l-2 border-primary/30 opacity-50 hidden md:block" />

              <motion.div variants={itemVariants} className="flex items-center gap-3 mb-8">
                <div className="flex bg-primary/10 border border-primary/20 rounded-none px-4 py-1.5 backdrop-blur-md relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-r from-primary/0 via-primary/20 to-primary/0 translate-x-[-100%] animate-[shimmer_2s_infinite]" />
                  <span className="relative z-10 text-primary uppercase tracking-[0.2em] font-mono text-xs font-semibold flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />
                    System Status: SECURE
                  </span>
                </div>
              </motion.div>

              <motion.h1 variants={itemVariants} className="text-5xl md:text-7xl lg:text-[5.5rem] font-black tracking-tighter leading-[1.05] mb-8 font-heading uppercase">
                <span className="block text-white filter drop-shadow-[0_0_15px_rgba(255,255,255,0.2)]">Detect Fraud.</span>
                <span className="relative inline-block mt-2">
                    <span className="absolute -inset-2 bg-primary/20 blur-xl rounded-full opacity-50" />
                    <span className="relative bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x underline decoration-4 decoration-accent/40 underline-offset-[12px]">
                        Save Revenue.
                    </span>
                </span>
              </motion.h1>

              <motion.p variants={itemVariants} className="text-lg md:text-xl text-muted-foreground mb-12 max-w-xl font-mono tracking-wide leading-relaxed border-l-2 border-white/10 pl-6 relative">
                <span className="absolute -left-[3px] top-0 w-1 h-6 bg-primary" />
                Advanced AI-driven transaction monitoring built exclusively for the dense Indian UPI ecosystem. <br className="hidden md:block"/>
                <span className="text-white/70">Sub-5ms Inference. Localized Intelligence.</span>
              </motion.p>

              <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-6">
                <Link to="/dashboard" className="group relative w-full sm:w-auto text-center">
                    {/* Glowing effect behind button */}
                    <div className="absolute -inset-1 bg-gradient-to-r from-primary to-accent rounded-sm opacity-60 blur-md group-hover:opacity-100 transition duration-500" />
                    <button className="relative w-full sm:w-auto bg-black border border-white/20 text-white font-mono uppercase tracking-[0.15em] text-sm font-bold px-10 py-5 transition-transform duration-300 transform group-hover:scale-[1.02] flex items-center justify-center gap-3">
                        INITIALIZE SCAN 
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter" className="text-primary group-hover:translate-x-1 group-hover:text-accent transition-all duration-300">
                            <path d="M5 12h14M12 5l7 7-7 7"/>
                        </svg>
                    </button>
                </Link>
                <button className="group w-full sm:w-auto relative px-10 py-5 bg-white/5 border border-white/10 font-mono text-sm tracking-[0.1em] text-white hover:bg-white/10 transition-colors uppercase flex items-center justify-center gap-3">
                  <div className="w-2 h-2 rounded-full border border-current opacity-70" />
                  View Architecture
                </button>
              </motion.div>

              <motion.div variants={itemVariants} className="mt-16 flex flex-wrap items-center gap-8 font-mono text-xs tracking-widest uppercase text-muted-foreground border-t border-white/5 pt-8">
                  <div className="flex items-center gap-2">
                      <span className="w-[1px] h-4 bg-primary" />
                      Y-Combinator <span className="text-white">W26</span>
                  </div>
                  <div className="flex items-center gap-2">
                      <span className="w-[1px] h-4 bg-accent" />
                      Hackathon <span className="text-white">Finalist</span>
                  </div>
              </motion.div>
            </motion.div>

            {/* Right: Premium 3D Graphics */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="relative h-[600px] flex items-center justify-center w-full mt-10 md:mt-0"
            >
              <div className="relative w-[130%] -right-[15%] max-w-2xl h-full flex items-center justify-center pointer-events-none">
                {/* Complex glowing backdrop */}
                <motion.div
                  className="absolute inset-0 rounded-full blur-[100px]"
                  style={{
                    background: 'radial-gradient(circle, oklch(0.62 0.22 270 / 0.45) 0%, transparent 60%)',
                  }}
                  animate={{ scale: [1, 1.2, 1], opacity: [0.6, 0.9, 0.6] }}
                  transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
                />

                <motion.div
                    className="relative z-10 w-full h-full flex flex-col items-center justify-center drop-shadow-[0_45px_65px_rgba(139,92,246,0.6)]"
                    animate={{ y: [-15, 15, -15] }}
                    transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
                >
                    <img src="/images/shield_3d.png" alt="3D Cybersecurity Shield" className="w-[85%] h-auto object-contain filter drop-shadow-[0_0_20px_rgba(255,255,255,0.7)]" />
                    
                    {/* Floating HUD elements around the shield */}
                    <motion.div 
                        animate={{ y: [0, -10, 0] }}
                        transition={{ duration: 3, repeat: Infinity, delay: 0.5 }}
                        className="absolute bottom-16 -left-4 glass p-4 rounded-xl border border-accent/50 shadow-lg text-left"
                    >
                        <p className="text-[10px] uppercase text-muted-foreground font-bold mb-1 tracking-wider">Risk Level</p>
                        <div className="text-xl font-bold flex items-center gap-2">
                            <span className="w-2.5 h-2.5 rounded-full bg-accent animate-pulse"></span>
                            SECURE
                        </div>
                    </motion.div>

                    <motion.div 
                        animate={{ y: [0, 15, 0] }}
                        transition={{ duration: 4, repeat: Infinity, delay: 1 }}
                        className="absolute top-24 -right-8 glass p-4 rounded-xl border border-primary/50 shadow-lg text-right"
                    >
                        <p className="text-[10px] uppercase text-muted-foreground font-bold mb-1 tracking-wider">AI Inference</p>
                        <div className="text-xl font-bold text-primary">2.4ms</div>
                    </motion.div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Statistics Section */}
        <section className="py-24 px-4 md:px-0 relative border-t border-border/40 bg-gradient-to-b from-transparent to-background/50">
          <motion.div
            className="container-main grid md:grid-cols-4 gap-6"
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: '-100px' }}
          >
            {[
              { number: '654', label: 'Synthetic Transactions Trained', suffix: '+' },
              { number: '33', label: 'Anomalies Detected Accurately', suffix: '' },
              { number: '2.3', label: 'Average Detection Time', suffix: 'ms' },
              { number: '100', label: 'Bilingual Support', suffix: '%' },
            ].map((stat) => (
              <motion.div
                key={stat.number}
                variants={itemVariants}
                className="relative group p-8 rounded-3xl overflow-hidden glass hover:bg-white/[0.02] transition-colors border border-white/5"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <motion.div
                  className="relative z-10"
                  animate={{ y: [0, -5, 0] }}
                  transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: Math.random() * 2 }}
                >
                  <p className="text-5xl font-bold font-mono tracking-tighter bg-gradient-to-br from-white to-white/60 bg-clip-text text-transparent mb-3 drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
                    {stat.number}
                    <span className="text-3xl text-primary">{stat.suffix}</span>
                  </p>
                  <p className="text-sm font-medium text-muted-foreground uppercase tracking-widest">{stat.label}</p>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* How It Works - Graphics Section */}
        <section className="py-32 px-4 md:px-0 relative" id="how">
          <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-primary/5 rounded-full blur-[120px] pointer-events-none" />
          
          <div className="container-main relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center max-w-3xl mx-auto mb-20"
            >
              <h2 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">
                How <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">PaySentinel</span> Works
              </h2>
              <p className="text-xl text-muted-foreground">An elegant pipeline transforming raw merchant transactions into intelligible security alerts via milliseconds of AI processing.</p>
            </motion.div>

            <motion.div
              className="grid lg:grid-cols-3 gap-8"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-100px' }}
            >
              {[
                { 
                  title: 'Real-Time Analysis', 
                  desc: 'Every UPI transaction flows through our ML pipeline in milliseconds',
                  graphic: <TransactionFlowGraphic />,
                  delay: 0
                },
                { 
                  title: 'Risk Scoring', 
                  desc: 'Isolation Forest + SHAP compute explainable fraud probability scores',
                  graphic: <RiskMeterGraphic value={32} />,
                  delay: 0.2
                },
                { 
                  title: 'Voice Alerts', 
                  desc: 'Bilingual Kannada & English voice notifications instantly delivered',
                  graphic: <DataPointsGraphic />,
                  delay: 0.4
                }
              ].map((step, idx) => (
                <motion.div 
                  key={step.title}
                  variants={itemVariants} 
                  className="flex flex-col group relative"
                >
                  <div className="absolute inset-0 rounded-[2.5rem] bg-gradient-to-b from-white/[0.08] to-transparent pointer-events-none" />
                  <div className="glass p-8 rounded-[2.5rem] h-72 flex items-center justify-center border border-white/10 group-hover:border-primary/30 transition-colors duration-500 overflow-hidden relative">
                    <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <div className="relative z-10 transform group-hover:scale-105 transition-transform duration-500">
                        {step.graphic}
                    </div>
                  </div>
                  <div className="pt-8 px-4 text-center">
                    <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 text-primary font-bold font-mono text-sm mb-4">
                      {idx + 1}
                    </div>
                    <h3 className="text-2xl font-bold mb-3">{step.title}</h3>
                    <p className="text-base text-muted-foreground leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Features Section - Premium Bento */}
        <section className="py-32 px-4 md:px-0 relative border-t border-white/5 bg-[#05050A]" id="features">
          <div className="absolute top-1/2 left-0 w-[600px] h-[600px] bg-accent/5 rounded-full blur-[100px] pointer-events-none" />
          
          <div className="container-main relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-20"
            >
              <h2 className="text-5xl md:text-6xl font-bold tracking-tight mb-6">
                Packed with <br className="hidden md:block"/>
                <span className="bg-gradient-to-r from-white via-white/80 to-white/40 bg-clip-text text-transparent">Advanced Features</span>
              </h2>
            </motion.div>

            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-100px' }}
            >
              {[
                {
                  icon: Zap,
                  title: 'Lightning Fast',
                  desc: 'Sub-5ms fraud detection latency built for high-throughput networks.',
                  gradient: 'from-primary/20 to-primary/5',
                  iconColor: 'text-primary'
                },
                {
                  icon: BarChart3,
                  title: 'Explainable AI',
                  desc: 'SHAP values explicitly illuminate the reasoning behind every generated risk score.',
                  gradient: 'from-accent/20 to-accent/5',
                  iconColor: 'text-accent'
                },
                {
                  icon: Lock,
                  title: 'Smart Fingerprinting',
                  desc: 'Machine learning adapts to unique merchant behaviors, reducing false positives.',
                  gradient: 'from-white/10 to-transparent',
                  iconColor: 'text-white'
                },
                {
                  icon: Volume2,
                  title: 'Bilingual Alerts',
                  desc: 'Audible Kannada & English voice notifications bridging the digital divide for shop owners.',
                  gradient: 'from-white/10 to-transparent',
                  iconColor: 'text-white'
                },
                {
                  icon: Shield,
                  title: 'Live Dashboard',
                  desc: 'Real-time transaction monitoring, beautiful analytics, and 1-click PDF reports.',
                  gradient: 'from-primary/20 to-primary/5',
                  iconColor: 'text-primary'
                },
                {
                  icon: Check,
                  title: 'Production Ready',
                  desc: 'Built with elite frontend architecture and robust backend security protocols.',
                  gradient: 'from-accent/20 to-accent/5',
                  iconColor: 'text-accent'
                },
              ].map((feature, idx) => (
                <motion.div
                  key={feature.title}
                  variants={itemVariants}
                  whileHover={{ y: -5 }}
                  className={`relative overflow-hidden p-8 rounded-[2rem] border border-white/10 bg-gradient-to-br ${feature.gradient} group cursor-pointer backdrop-blur-md`}
                >
                  <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity duration-500 group-hover:scale-150 transform origin-top-right">
                      <feature.icon className="w-32 h-32 text-white" />
                  </div>
                  
                  <motion.div
                    className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center mb-8 border border-white/10 backdrop-blur-xl group-hover:scale-110 transition-transform duration-300 shadow-xl"
                  >
                    <feature.icon className={`w-6 h-6 ${feature.iconColor}`} />
                  </motion.div>
                  <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-base text-muted-foreground leading-relaxed max-w-[90%]">{feature.desc}</p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Merchant Protection Section */}
        <section className="py-32 px-4 md:px-0 relative border-t border-white/5 overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_var(--primary)_0%,_transparent_40%)] opacity-10" />
          
          <div className="container-main relative z-10">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="grid gap-16 lg:grid-cols-[1fr_1.2fr] items-center"
            >
              <motion.div
                initial={{ opacity: 0, x: -40 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2 }}
                className="order-2 lg:order-1"
              >
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/20 mb-6 backdrop-blur-sm">
                    <span className="text-accent font-semibold text-xs uppercase tracking-widest">Built For Bharat</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight leading-tight">
                  Designed for <br/>
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-emerald-300">Indian Merchants</span>
                </h2>
                <p className="text-xl text-muted-foreground mb-10 leading-relaxed">
                  Small UPI merchants face massive fraud losses. PaySentinel provides affordable, highly accessible AI protection tailored specifically for local shop owners.
                </p>
                <div className="grid gap-6">
                  {[
                    { title: 'Bengaluru-first approach', desc: 'Optimized for the dense Indian UPI ecosystem.' },
                    { title: 'Kannada + English interface', desc: 'Breaking language barriers for tech accessibility.' },
                    { title: 'Voice alerts for offline merchants', desc: 'No need to constantly look at screens.' },
                  ].map((item) => (
                    <div key={item.title} className="flex gap-4">
                      <div className="shrink-0 w-12 h-12 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
                        <Check className="w-5 h-5 text-accent" />
                      </div>
                      <div>
                        <h4 className="text-lg font-bold mb-1">{item.title}</h4>
                        <p className="text-muted-foreground">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 40 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3 }}
                className="order-1 lg:order-2 relative h-[500px]"
              >
                {/* A visually premium glassmorphic container for the illustration */}
                <div className="absolute inset-0 bg-gradient-to-tl from-white/5 to-transparent rounded-[3rem] border border-white/10 backdrop-blur-xl shadow-2xl flex items-center justify-center overflow-hidden">
                    <div className="absolute -top-32 -right-32 w-96 h-96 bg-accent/20 rounded-full blur-[80px]" />
                    <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-primary/20 rounded-full blur-[80px]" />
                    <div className="w-[85%] relative z-10 transition-transform duration-700 hover:scale-105">
                        <MerchantShieldGraphic />
                    </div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Pricing Section - Premium */}
        <section className="py-32 px-4 md:px-0 relative border-t border-white/5 bg-background overflow-hidden" id="pricing">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-[120px] pointer-events-none" />
          <div className="container-main relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-20 max-w-3xl mx-auto"
            >
              <h2 className="text-5xl md:text-6xl font-bold mb-6 tracking-tight">
                Simple, Transparent <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Pricing</span>
              </h2>
              <p className="text-xl text-muted-foreground">Premium fraud detection accessibility scaled for your enterprise size.</p>
            </motion.div>

            <motion.div
              className="grid md:grid-cols-3 gap-8 items-center max-w-6xl mx-auto"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-100px' }}
            >
              {[
                {
                  name: 'Starter Tier',
                  price: '₹2,999',
                  desc: 'Perfect for small local merchants.',
                  features: ['Up to 1,000 txns/day', 'Standard AI inference', 'Email support', 'Basic analytics export'],
                  accent: false,
                },
                {
                  name: 'Professional',
                  price: '₹9,999',
                  desc: 'Highest protection for growing chains.',
                  features: ['Up to 10,000 txns/day', 'Sub-10ms Inference AI', 'Voice alerts (Kannada/English)', 'Premium SHAP Analytics', '24/7 dedicated support'],
                  accent: true,
                },
                {
                  name: 'Enterprise',
                  price: 'Custom',
                  desc: 'Bespoke integration for large networks.',
                  features: ['Unlimited transactions', 'Direct API access', 'White-labeled reports', 'SLA guaranteed uptime', 'Custom ML model tuning'],
                  accent: false,
                },
              ].map((plan, idx) => (
                <motion.div
                  key={plan.name}
                  variants={itemVariants}
                  whileHover={{ y: -10, transition: { duration: 0.3 } }}
                  className={`relative p-10 rounded-[2.5rem] border backdrop-blur-xl ${
                    plan.accent 
                        ? 'border-primary shadow-[0_20px_60px_rgba(139,92,246,0.15)] bg-gradient-to-b from-primary/10 to-transparent scale-105 z-10' 
                        : 'border-white/10 bg-white/[0.02] hover:bg-white/[0.04]'
                  }`}
                >
                  {plan.accent && (
                    <div className="absolute top-0 right-10 transform -translate-y-1/2">
                        <div className="inline-block px-4 py-1.5 rounded-full text-xs font-bold bg-primary text-white shadow-[0_0_20px_rgba(139,92,246,0.5)]">
                            MOST POPULAR
                        </div>
                    </div>
                  )}

                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <p className="text-sm text-muted-foreground mb-8">{plan.desc}</p>

                  <div className="flex items-baseline gap-2 mb-10">
                    <p className="text-5xl font-bold font-mono tracking-tighter">
                      {plan.price}
                    </p>
                    {plan.price !== 'Custom' && <span className="text-lg text-muted-foreground font-medium">/mo</span>}
                  </div>

                  <ul className="space-y-4 mb-10 border-t border-white/10 pt-8">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3 text-sm">
                        <div className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${plan.accent ? 'bg-primary/20 text-primary' : 'bg-white/10 text-white'}`}>
                            <Check className="w-3 h-3" />
                        </div>
                        <span className={plan.accent ? 'text-foreground font-medium' : 'text-muted-foreground'}>{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <button
                    className={`w-full py-4 rounded-xl font-bold transition-all duration-300 ${
                        plan.accent 
                        ? 'bg-primary text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_30px_rgba(139,92,246,0.5)]' 
                        : 'bg-white/5 text-foreground hover:bg-white/10 border border-white/10'
                    }`}
                  >
                    Get Started Today
                  </button>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* CTA Banner */}
        <section className="py-32 px-4 md:px-0 relative border-t border-white/5">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="container-main relative"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-primary to-accent opacity-20 rounded-[3rem] blur-xl" />
            
            <div className="relative z-10 px-6 py-24 md:p-24 rounded-[3rem] border border-white/20 text-center overflow-hidden bg-background/80 backdrop-blur-2xl">
              <div className="absolute top-0 right-0 w-96 h-96 rounded-full blur-[100px] bg-accent/30 mix-blend-screen pointer-events-none" />
              <div className="absolute bottom-0 left-0 w-96 h-96 rounded-full blur-[100px] bg-primary/30 mix-blend-screen pointer-events-none" />

              <h2 className="text-5xl md:text-7xl font-bold mb-8 tracking-tight">
                Ready to <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Stop Fraud?</span>
              </h2>
              <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed">
                Join Bengaluru merchants protecting their livelihoods with PaySentinel. <br/>
                <span className="text-accent underline decoration-accent/30 decoration-2 underline-offset-4">BluePrint 2026 Hackathon Finalist.</span>
              </p>
              
              <div className="flex justify-center">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="group relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-full bg-white text-base font-bold text-background px-10 py-5 transition-all duration-300 hover:shadow-[0_0_40px_rgba(255,255,255,0.4)]"
                  >
                    <span className="absolute inset-0 bg-gradient-to-r from-primary to-accent opacity-0 transition-opacity duration-300 group-hover:opacity-20" />
                    <span className="relative z-10 flex items-center gap-2">Start Your Free Trial <ArrowRight size={20} /></span>
                  </motion.button>
              </div>
            </div>
          </motion.div>
        </section>
      </main>
    </div>
  )
}
