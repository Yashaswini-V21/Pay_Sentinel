import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, AlertTriangle, Clock, ChevronDown, Bell, Settings } from 'lucide-react'
import { RiskBadge } from '../components/RiskBadge'
import { KpiCard } from '../components/KpiCard'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'

// Mock transaction data
function generateMockTransactions() {
  const merchants = ['Amazon', 'Flipkart', 'Instamojo', 'Razorpay', 'PhonePe', 'Google Play']
  const statuses = ['safe', 'warn', 'fraud'] as const
  const reasons = ['Unusual amount', 'Late night txn', 'New sender', 'High frequency', 'Location anomaly', 'Normal']

  return Array.from({ length: 8 }, (_, i) => {
    const status = Math.random() > 0.9 ? 'fraud' : Math.random() > 0.7 ? 'warn' : 'safe'
    return {
      id: `TXN${String(i + 1).padStart(6, '0')}`,
      merchant: merchants[Math.floor(Math.random() * merchants.length)],
      amount: Math.floor(Math.random() * 50000),
      time: new Date(Date.now() - Math.random() * 3600000).toLocaleTimeString(),
      status,
      reason: reasons[Math.floor(Math.random() * reasons.length)],
      sender: `UPI_${Math.random().toString(36).substring(7)}`,
      score: Math.round(Math.random() * 100),
    }
  })
}

export default function Dashboard() {
  const [transactions, setTransactions] = useState(generateMockTransactions())
  const [expandedTxnId, setExpandedTxnId] = useState<string | null>(null)
  const [dateRange, setDateRange] = useState('today')

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setTransactions((prev) => {
        const newTxn = generateMockTransactions()[0]
        return [newTxn, ...prev.slice(0, 7)]
      })
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const kpis = [
    { title: 'Live Transactions', value: '12,847', delta: '+8.2%', trend: 'up' },
    { title: 'Flagged Today', value: '127', delta: '+23.1%', trend: 'up' },
    { title: 'Risk Score', value: '23%', delta: '-2.4%', trend: 'down' },
    { title: 'Avg Response', value: '2.3ms', delta: '-0.4ms', trend: 'down' },
  ]

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <div className="sticky top-0 z-40 border-b border-border bg-card/50 backdrop-blur">
        <div className="container-main h-16 flex items-center justify-between px-4 md:px-0">
          <div>
            <h1 className="text-xl font-bold">Dashboard</h1>
            <p className="text-xs text-muted-foreground">Real-time fraud monitoring</p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-3 py-1.5 rounded-lg text-xs font-medium hidden md:block"
              style={{
                background: 'oklch(0.11 0.015 260)',
                border: '1px solid oklch(0.22 0.015 260 / 30%)',
                color: 'oklch(0.97 0.01 250)',
              }}
            >
              <option>Last 24h</option>
              <option>Last 7d</option>
              <option>Last 30d</option>
            </select>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 rounded-lg"
              style={{
                background: 'oklch(0.11 0.015 260)',
                border: '1px solid oklch(0.22 0.015 260 / 30%)',
              }}
            >
              <Bell className="w-4 h-4 text-muted-foreground" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 rounded-lg"
              style={{
                background: 'oklch(0.11 0.015 260)',
                border: '1px solid oklch(0.22 0.015 260 / 30%)',
              }}
            >
              <Settings className="w-4 h-4 text-muted-foreground" />
            </motion.button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="py-8 px-4 md:px-0">
        <div className="container-main">
          {/* KPI Cards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid md:grid-cols-4 gap-4 mb-8"
          >
            {kpis.map((kpi, i) => (
              <KpiCard key={kpi.title} {...kpi} delay={i * 0.1} />
            ))}
          </motion.div>

          {/* Tabs Section */}
          <Tabs defaultValue="live-feed">
            <TabsList className="mb-6 glass p-1">
              <TabsTrigger value="live-feed" className="text-sm">
                Live Feed
              </TabsTrigger>
              <TabsTrigger value="anomalies" className="text-sm">
                Anomalies
              </TabsTrigger>
              <TabsTrigger value="trends" className="text-sm">
                Trends
              </TabsTrigger>
              <TabsTrigger value="alerts" className="text-sm">
                Alerts
              </TabsTrigger>
            </TabsList>

            {/* Live Feed Tab */}
            <TabsContent value="live-feed" className="space-y-3">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ staggerChildren: 0.05 }}
                className="space-y-3"
              >
                {transactions.map((txn, idx) => (
                  <motion.div
                    key={txn.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    onClick={() => setExpandedTxnId(expandedTxnId === txn.id ? null : txn.id)}
                    className="p-4 rounded-lg cursor-pointer transition-all glass hover:glass-elevated"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
                          <span className="font-mono text-xs text-muted-foreground">{txn.id}</span>
                          <span className="text-sm font-semibold">{txn.merchant}</span>
                          <RiskBadge type={txn.status} />
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3 text-sm">
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Amount</p>
                            <p className="font-semibold">₹{txn.amount.toLocaleString()}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Time</p>
                            <p className="font-mono text-xs">{txn.time}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Score</p>
                            <p className="font-semibold">{txn.score}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Reason</p>
                            <p className="text-xs">{txn.reason}</p>
                          </div>
                        </div>

                        {/* Expanded Details */}
                        {expandedTxnId === txn.id && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="mt-4 pt-4 border-t border-border"
                          >
                            <div className="grid md:grid-cols-2 gap-4 text-sm mb-4">
                              <div>
                                <p className="text-xs text-muted-foreground mb-2">Sender UPI</p>
                                <p className="font-mono text-xs bg-muted/50 p-2 rounded">{txn.sender}</p>
                              </div>
                              <div>
                                <p className="text-xs text-muted-foreground mb-2">Anomaly Factors</p>
                                <p className="text-xs space-y-1">
                                  • {txn.reason}
                                  <br />• High frequency pattern detected
                                  <br />• Similar to 3 previous transactions
                                </p>
                              </div>
                            </div>

                            <div className="flex gap-2">
                              <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-4 py-2 text-sm font-semibold rounded-lg"
                                style={{
                                  background: 'oklch(0.72 0.18 155)',
                                  color: 'oklch(0.08 0.012 260)',
                                }}
                              >
                                Whitelist
                              </motion.button>
                              <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-4 py-2 text-sm font-semibold rounded-lg"
                                style={{
                                  background: 'oklch(0.11 0.015 260)',
                                  border: '1px solid oklch(0.22 0.015 260 / 30%)',
                                  color: 'oklch(0.97 0.01 250)',
                                }}
                              >
                                Block Sender
                              </motion.button>
                            </div>
                          </motion.div>
                        )}
                      </div>

                      <motion.div
                        animate={{ rotate: expandedTxnId === txn.id ? 180 : 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                      </motion.div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            </TabsContent>

            {/* Anomalies Tab */}
            <TabsContent value="anomalies" className="p-8 text-center glass">
              <AlertTriangle className="w-12 h-12 text-warning mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground">Chart integration ready</p>
            </TabsContent>

            {/* Trends Tab */}
            <TabsContent value="trends" className="p-8 text-center glass">
              <TrendingUp className="w-12 h-12 text-accent mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground">Real-time trends dashboard</p>
            </TabsContent>

            {/* Alerts Tab */}
            <TabsContent value="alerts" className="p-8 text-center glass">
              <Clock className="w-12 h-12 text-warning mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground">Alert history and logs</p>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  )
}
