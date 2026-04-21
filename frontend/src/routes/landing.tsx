import { useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, Lock, AlertTriangle, TrendingUp, Activity, Zap, Check, ChevronRight } from 'lucide-react'
import { SiteHeader } from '../components/SiteHeader'
import { SiteFooter } from '../components/SiteFooter'
import { RiskBadge } from '../components/RiskBadge'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100, damping: 15 } },
}

const float = {
  animate: { y: [0, -20, 0], transition: { duration: 4, repeat: Infinity } },
}

export function Landing() {
  const [hoveredPlan, setHoveredPlan] = useState<string | null>(null)

  const features = [
    {
      icon: Shield,
      title: 'ML Anomaly Detection',
      desc: 'Isolation Forest algorithms detect fraud patterns missed by rules',
    },
    {
      icon: Zap,
      title: 'Ultra-low Latency',
      desc: 'Sub-10ms inference + instant merchant alerts via Kannada voice',
    },
    {
      icon: Activity,
      title: 'Explainable AI',
      desc: 'SHAP integration shows why each transaction was flagged',
    },
    {
      icon: Lock,
      title: 'Merchant Fingerprinting',
      desc: 'Learn normal patterns for each UPI merchant account',
    },
    {
      icon: TrendingUp,
      title: 'Real-time Dashboard',
      desc: 'Live monitoring of flagged transactions & fraud trends',
    },
    {
      icon: AlertTriangle,
      title: 'Bilingual Alerts',
      desc: 'Critical fraud alerts in English + ಕನ್ನಡ (Kannada)',
    },
  ]

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      price: '₹2,999',
      period: '/month',
      desc: 'For small merchants',
      features: ['Up to 1000 transactions/day', '24h fraud history', 'Email alerts', 'Basic reports'],
      cta: 'Get Started',
    },
    {
      id: 'pro',
      name: 'Professional',
      price: '₹9,999',
      period: '/month',
      desc: 'For growing businesses',
      features: ['Up to 10K transactions/day', 'Unlimited history', 'Voice + SMS alerts', 'Advanced analytics', 'API access'],
      cta: 'Start Free Trial',
      highlighted: true,
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 'Custom',
      period: 'contact sales',
      desc: 'For large networks',
      features: ['Unlimited transactions', 'Dedicated support', 'Custom integrations', 'On-premise option'],
      cta: 'Contact Us',
    },
  ]

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <SiteHeader />

      {/* Hero Section */}
      <section className="flex-1 pt-20 pb-16 md:pt-32 md:pb-24 px-4">
        <div className="container-main max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="mb-12 text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
              className="inline-block mb-6 px-4 py-2 rounded-full"
              style={{
                background: 'linear-gradient(135deg, oklch(0.62 0.22 270 / 0.1), oklch(0.72 0.18 155 / 0.1))',
                border: '1px solid oklch(0.62 0.22 270 / 0.2)',
              }}
            >
              <span className="text-sm font-semibold text-accent">✨ v2.0: Kannada Voice Alerts</span>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Real-time{' '}
              <span
                className="text-gradient"
                style={{
                  backgroundImage: 'linear-gradient(135deg, oklch(0.62 0.22 270), oklch(0.72 0.18 155))',
                }}
              >
                Payment Intelligence
              </span>{' '}
              for Modern Apps
            </h1>

            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
              Unsupervised machine learning to detect anomalies, prevent chargebacks, and secure your transactions with
              millisecond latency.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 rounded-lg font-semibold text-white transition-all"
                style={{
                  background: 'linear-gradient(135deg, oklch(0.62 0.22 270), oklch(0.72 0.18 155))',
                  boxShadow: '0 0 30px oklch(0.62 0.22 270 / 0.3)',
                }}
              >
                Start Protecting Now →
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 rounded-lg font-semibold border transition-all"
                style={{
                  borderColor: 'oklch(0.22 0.015 260 / 50%)',
                  background: 'oklch(0.11 0.015 260 / 30%)',
                }}
              >
                View Documentation
              </motion.button>
            </div>
          </motion.div>

          {/* Animated Hero Graphic */}
          <motion.div
            className="relative h-96 md:h-[500px] mt-16 rounded-2xl overflow-hidden"
            style={{
              background:
                'radial-gradient(circle at 30% 50%, oklch(0.62 0.22 270 / 0.1), transparent 50%), radial-gradient(circle at 70% 50%, oklch(0.72 0.18 155 / 0.1), transparent 50%)',
              border: '1px solid oklch(0.22 0.015 260 / 30%)',
            }}
          >
            {/* Floating fraud alert cards */}
            {[0, 1, 2].map((i) => (
              <motion.div
                key={`card-${i}`}
                className="absolute w-64 p-4 rounded-lg"
                style={{
                  background: 'oklch(0.11 0.015 260 / 80%)',
                  border: '1px solid oklch(0.22 0.015 260 / 50%)',
                  backdropFilter: 'blur(10px)',
                }}
                animate={{
                  y: [0, -50, 0],
                  x: [0, Math.cos((i * Math.PI * 2) / 3) * 30, 0],
                }}
                transition={{
                  duration: 6,
                  delay: i * 1,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
                style={{
                  top: `${20 + i * 25}%`,
                  left: `${15 + i * 35}%`,
                }}
              >
                <div className="flex items-start gap-3 mb-2">
                  {i === 0 && <AlertTriangle className="w-5 h-5 text-destructive mt-1 flex-shrink-0" />}
                  {i === 1 && <Shield className="w-5 h-5 text-accent mt-1 flex-shrink-0" />}
                  {i === 2 && <Check className="w-5 h-5 text-accent mt-1 flex-shrink-0" />}
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-mono text-muted-foreground">
                      {['HIGH RISK', 'NORMAL', 'VERIFIED'][i]}
                    </p>
                    <p className="text-sm font-semibold mt-1">₹{Math.random() * 10000 | 0}</p>
                  </div>
                </div>
                <RiskBadge type={['fraud', 'warn', 'safe'][i] as 'fraud' | 'warn' | 'safe'} />
              </motion.div>
            ))}

            {/* Center pulse circle */}
            <motion.div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 rounded-full"
              style={{
                background: 'radial-gradient(circle, oklch(0.62 0.22 270 / 0.2), transparent)',
              }}
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.5, 0.1, 0.5],
              }}
              transition={{ duration: 3, repeat: Infinity }}
            />
          </motion.div>
        </div>
      </section>

      {/* Features Bento */}
      <section className="py-24 px-4 border-t border-border">
        <div className="container-main">
          <motion.div
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: '-100px' }}
            className="grid md:grid-cols-3 gap-6"
          >
            {features.map(({ icon: Icon, title, desc }) => (
              <motion.div key={title} variants={item} className="group p-6 rounded-xl glass hover:glass-elevated transition-all">
                <Icon className="w-10 h-10 text-accent mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-lg font-bold mb-2">{title}</h3>
                <p className="text-sm text-muted-foreground">{desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-24 px-4 bg-muted/20">
        <div className="container-main">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Simple, Transparent Pricing</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Choose the plan that fits your merchant network
            </p>
          </motion.div>

          <motion.div
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: '-100px' }}
            className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto"
          >
            {plans.map((plan) => (
              <motion.div
                key={plan.id}
                variants={item}
                onHoverStart={() => setHoveredPlan(plan.id)}
                onHoverEnd={() => setHoveredPlan(null)}
                className="relative p-8 rounded-2xl transition-all"
                style={{
                  background: plan.highlighted ? 'linear-gradient(135deg, oklch(0.62 0.22 270 / 0.1), oklch(0.72 0.18 155 / 0.1))' : 'oklch(0.11 0.015 260)',
                  border: plan.highlighted ? '2px solid oklch(0.62 0.22 270 / 0.4)' : '1px solid oklch(0.22 0.015 260 / 30%)',
                  transform: hoveredPlan === plan.id ? 'translateY(-8px)' : 'translateY(0)',
                }}
              >
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-accent text-background text-xs font-bold">
                    POPULAR
                  </div>
                )}
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <p className="text-sm text-muted-foreground mb-6">{plan.desc}</p>

                <div className="mb-6">
                  <span className="text-5xl font-bold">{plan.price}</span>
                  <span className="text-muted-foreground ml-2">{plan.period}</span>
                </div>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-full py-3 rounded-lg font-semibold mb-8 transition-all"
                  style={{
                    background: plan.highlighted ? 'oklch(0.62 0.22 270)' : 'oklch(0.11 0.015 260)',
                    color: plan.highlighted ? 'white' : 'oklch(0.97 0.01 250)',
                    border: plan.highlighted ? 'none' : '1px solid oklch(0.22 0.015 260 / 50%)',
                  }}
                >
                  {plan.cta}
                </motion.button>

                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm">
                      <Check className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="py-16 px-4 border-t border-border">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="container-main max-w-3xl mx-auto text-center p-12 rounded-2xl"
          style={{
            background: 'linear-gradient(135deg, oklch(0.62 0.22 270 / 0.1), oklch(0.72 0.18 155 / 0.1))',
            border: '1px solid oklch(0.62 0.22 270 / 0.2)',
          }}
        >
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Stop Fraud?</h2>
          <p className="text-muted-foreground mb-8">Join 500+ merchants protecting their UPI transactions</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-4 rounded-lg font-semibold text-white inline-flex items-center gap-2"
            style={{
              background: 'linear-gradient(135deg, oklch(0.62 0.22 270), oklch(0.72 0.18 155))',
            }}
          >
            Get Started Free <ChevronRight className="w-4 h-4" />
          </motion.button>
        </motion.div>
      </section>

      <SiteFooter />
    </div>
  )
}

export default Landing
