'use client'

import { useState } from 'react'
import { Lock, Play } from 'lucide-react'

interface AuthSetupProps {
  apiUrl: string
  projectPath: string
  onSuccess?: () => void
}

export default function AuthSetup({ apiUrl, projectPath, onSuccess }: AuthSetupProps) {
  const [appName, setAppName] = useState('users')
  const [accessLifetime, setAccessLifetime] = useState(60)
  const [refreshLifetime, setRefreshLifetime] = useState(7)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)

  const setupAuth = async () => {
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch(`${apiUrl}/api/auth/setup/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app_name: appName, access_token_lifetime: accessLifetime, refresh_token_lifetime: refreshLifetime, project_path: projectPath })
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
        <Lock className="w-5 h-5" style={{ color: 'var(--accent)' }} />
        <span className="text-sm tracking-wider font-bold">JWT AUTH SETUP</span>
      </div>

      <div className="mb-4">
        <label className="block text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>APP NAME</label>
        <input type="text" value={appName} onChange={(e) => setAppName(e.target.value)} className="w-full" />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>ACCESS TOKEN (MINUTES)</label>
          <input type="number" value={accessLifetime} onChange={(e) => setAccessLifetime(parseInt(e.target.value) || 60)} className="w-full" />
        </div>
        <div>
          <label className="block text-xs tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>REFRESH TOKEN (DAYS)</label>
          <input type="number" value={refreshLifetime} onChange={(e) => setRefreshLifetime(parseInt(e.target.value) || 7)} className="w-full" />
        </div>
      </div>

      <button onClick={setupAuth} disabled={loading} className="flex items-center gap-2 text-sm font-bold" style={{ background: 'var(--accent)', color: 'var(--bg)' }}>
        <Play className="w-4 h-4" />
        {loading ? 'SETTING UP...' : 'SETUP AUTH'}
      </button>

      {result && (
        <div className="border mt-4 p-4" style={{ borderColor: result.success ? 'var(--success)' : 'var(--error)' }}>
          <span style={{ color: result.success ? 'var(--success)' : 'var(--error)' }}>{result.message}</span>
        </div>
      )}
    </div>
  )
}
