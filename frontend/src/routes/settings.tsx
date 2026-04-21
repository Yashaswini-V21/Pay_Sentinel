import { motion } from 'framer-motion'
import { Save } from 'lucide-react'
import { BilingualText } from '@/components/BilingualText'

export default function Settings() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-16 z-40 border-b border-border bg-card/50 backdrop-blur">
        <div className="container-main h-14 flex items-center">
          <h1 className="text-xl font-bold">Settings</h1>
        </div>
      </div>

      {/* Content */}
      <div className="container-main py-8 max-w-2xl">
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* ML Tuning */}
          <div className="glass p-6 rounded-lg border border-border">
            <h2 className="text-lg font-bold mb-4">ML Model Tuning</h2>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Contamination Rate</label>
                <input
                  type="range"
                  min="0.01"
                  max="0.20"
                  step="0.01"
                  defaultValue="0.05"
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Expected % of anomalies (default: 5%)
                </p>
              </div>
            </div>
          </div>

          {/* Operating Hours */}
          <div className="glass p-6 rounded-lg border border-border">
            <h2 className="text-lg font-bold mb-4">Operating Hours</h2>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Start time</label>
                <input type="time" defaultValue="08:00" className="px-3 py-2 rounded-lg bg-muted border border-border w-full text-sm" />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">End time</label>
                <input type="time" defaultValue="21:00" className="px-3 py-2 rounded-lg bg-muted border border-border w-full text-sm" />
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                <button
                  key={day}
                  className="px-3 py-2 rounded-lg bg-muted border border-border text-xs font-medium hover:bg-card transition-colors"
                >
                  {day}
                </button>
              ))}
            </div>
          </div>

          {/* Voice & Language */}
          <div className="glass p-6 rounded-lg border border-border">
            <h2 className="text-lg font-bold mb-4">Voice & Language</h2>
            <div className="space-y-4">
              <BilingualText
                en="Select alert language"
                kn="ಎಚ್ಚರಿಕೆ ಭಾಷೆ ಆಯ್ಕೆ ಮಾಡಿ"
                className="block"
                block
              />
              <div className="space-y-2">
                {[
                  { id: 'en', label: 'English' },
                  { id: 'kn', label: 'Kannada (ಕನ್ನಡ)' },
                  { id: 'both', label: 'Both languages' },
                ].map((opt) => (
                  <label key={opt.id} className="flex items-center gap-3">
                    <input
                      type="radio"
                      name="language"
                      defaultChecked={opt.id === 'both'}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">{opt.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div className="glass p-6 rounded-lg border border-border">
            <h2 className="text-lg font-bold mb-4">Notifications</h2>
            <div className="space-y-3">
              {[
                { label: 'Browser push', id: 'push' },
                { label: 'WhatsApp', id: 'whatsapp' },
                { label: 'SMS', id: 'sms' },
              ].map((notif) => (
                <label key={notif.id} className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    defaultChecked={notif.id === 'push'}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-sm">{notif.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Save Button */}
          <div className="sticky bottom-0 left-0 right-0 glass-elevated border-t border-border p-4">
            <button className="btn-primary w-full flex items-center justify-center gap-2">
              <Save size={16} />
              Save changes
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
