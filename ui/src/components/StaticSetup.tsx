'use client'

import { useState } from 'react'
import { Layers, Play } from 'lucide-react'

interface StaticSetupProps {
  apiUrl: string
  projectPath: string
  onSuccess?: () => void
}

export default function StaticSetup({ apiUrl, projectPath, onSuccess }: StaticSetupProps) {
  const [framework, setFramework] = useState('tailwind')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)

  const setupStatic = async () => {
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch(`${apiUrl}/api/static/setup/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ framework, project_path: projectPath })
      })
      const data = await res.json()
      setResult(data)
      if (data.success) onSuccess?.()
    } catch (e) {
      setResult({ success: false, message: 'Failed to connect to API' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-4 pb-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <Layers className="w-5 h-5" style={{ color: 'var(--accent)' }} />
        <span className="text-sm tracking-wider font-bold">STATIC FILES SETUP</span>
      </div>

      <div className="mb-4">
        <label className="block text-xs tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>CSS FRAMEWORK</label>
        <div className="grid grid-cols-2 gap-2">
          <button onClick={() => setFramework('tailwind')} style={{ background: framework === 'tailwind' ? 'var(--accent)' : 'transparent', color: framework === 'tailwind' ? 'var(--bg)' : 'var(--text-secondary)', borderColor: framework === 'tailwind' ? 'var(--accent)' : 'var(--border)' }} className="px-4 py-3 text-sm border">
            TAILWIND CSS
          </button>
          <button onClick={() => setFramework('bootstrap')} style={{ background: framework === 'bootstrap' ? 'var(--accent)' : 'transparent', color: framework === 'bootstrap' ? 'var(--bg)' : 'var(--text-secondary)', borderColor: framework === 'bootstrap' ? 'var(--accent)' : 'var(--border)' }} className="px-4 py-3 text-sm border">
            BOOTSTRAP
          </button>
        </div>
      </div>

      <button onClick={setupStatic} disabled={loading} className="flex items-center gap-2 text-sm font-bold" style={{ background: 'var(--accent)', color: 'var(--bg)' }}>
        <Play className="w-4 h-4" />
        {loading ? 'SETTING UP...' : 'SETUP STATIC'}
      </button>

      {result && (
        <div className="border mt-4 p-4" style={{ borderColor: result.success ? 'var(--success)' : 'var(--error)' }}>
          <span style={{ color: result.success ? 'var(--success)' : 'var(--error)' }}>{result.message}</span>
        </div>
      )}
    </div>
  )
}
