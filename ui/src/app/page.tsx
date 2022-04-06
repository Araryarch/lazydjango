'use client'

import { useState } from 'react'
import { Code2, RefreshCw, Database, Box, Server, Shield, Layers, Cog, LayoutList, Table2 } from 'lucide-react'
import ResourcePage from '@/components/ResourcePage'
import ServerPanel from '@/components/ServerPanel'
import ProjectInfo from '@/components/ProjectInfo'
import AuthSetup from '@/components/AuthSetup'
import StaticSetup from '@/components/StaticSetup'
import MiddlewareCreator from '@/components/MiddlewareCreator'
import DatabaseTab from '@/components/DatabaseTab'

type Tab = 'resource' | 'server' | 'project' | 'auth' | 'static' | 'middleware' | 'database'

const tabs = [
  { id: 'resource', label: 'RESOURCE', icon: Box },
  { id: 'server', label: 'SERVER', icon: Server },
  { id: 'database', label: 'DATABASE', icon: Table2 },
  { id: 'project', label: 'PROJECT', icon: Database },
  { id: 'auth', label: 'AUTH', icon: Shield },
  { id: 'static', label: 'STATIC', icon: Cog },
  { id: 'middleware', label: 'MIDDLEWARE', icon: Cog },
]

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('resource')
  const [projectPath, setProjectPath] = useState('.')
  const [apiUrl] = useState(typeof window !== 'undefined' ? window.location.origin : 'http://localhost:6767')
  const [refreshKey, setRefreshKey] = useState(0)

  const refresh = () => setRefreshKey(k => k + 1)

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg)', color: 'var(--text)' }}>
      {/* Header */}
      <header className="border-b px-6 py-4" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Code2 className="w-6 h-6" style={{ color: 'var(--accent)' }} />
            <span className="text-lg font-bold tracking-wider">LAZYDjango</span>
          </div>
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={projectPath}
              onChange={(e) => setProjectPath(e.target.value)}
              className="w-48 text-sm"
              placeholder="Project Path"
            />
            <button onClick={refresh} className="p-2" title="Refresh">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-52 border-r min-h-[calc(100vh-65px)]" style={{ background: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
          <nav className="p-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as Tab)}
                  style={{
                    background: isActive ? 'var(--accent)' : 'transparent',
                    color: isActive ? 'var(--bg)' : 'var(--text-secondary)',
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-left text-xs tracking-wider mb-1 font-medium"
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'var(--bg-tertiary)'
                      e.currentTarget.style.color = 'var(--text)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'transparent'
                      e.currentTarget.style.color = 'var(--text-secondary)'
                    }
                  }}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1">
          {activeTab === 'resource' && <ResourcePage key={refreshKey} />}
          {activeTab === 'server' && <ServerPanel key={refreshKey} apiUrl={apiUrl} projectPath={projectPath} />}
          {activeTab === 'database' && <DatabaseTab key={refreshKey} apiUrl={apiUrl} projectPath={projectPath} />}
          {activeTab === 'project' && <ProjectInfo key={refreshKey} apiUrl={apiUrl} projectPath={projectPath} />}
          {activeTab === 'auth' && <AuthSetup key={refreshKey} apiUrl={apiUrl} projectPath={projectPath} />}
          {activeTab === 'static' && <StaticSetup key={refreshKey} apiUrl={apiUrl} projectPath={projectPath} />}
          {activeTab === 'middleware' && <MiddlewareCreator key={refreshKey} apiUrl={apiUrl} projectPath={projectPath} />}
        </main>
      </div>
    </div>
  )
}
