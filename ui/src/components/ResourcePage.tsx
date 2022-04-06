'use client'

import { useState, useEffect } from 'react'
import { Box, Play, Plus, Trash2, FileCode, LayoutList } from 'lucide-react'

interface ModelField {
  name: string
  field_type: string
  required: boolean
  unique: boolean
  max_length: number | null
  related_model: string | null
  on_delete: string
}

interface FormField {
  name: string
  field_type: string
  label: string
  placeholder: string
  required: boolean
}

interface CreatedModel {
  app_name: string
  model_name: string
  fields: ModelField[]
  created_at: string
}

interface CreatedForm {
  form_name: string
  style: string
  fields: FormField[]
}

type Tab = 'models' | 'endpoints' | 'forms'

const FIELD_TYPES = [
  { value: 'CharField', label: 'CHAR' },
  { value: 'TextField', label: 'TEXT' },
  { value: 'IntegerField', label: 'INT' },
  { value: 'FloatField', label: 'FLOAT' },
  { value: 'BooleanField', label: 'BOOL' },
  { value: 'DateField', label: 'DATE' },
  { value: 'DateTimeField', label: 'DT' },
  { value: 'EmailField', label: 'EMAIL' },
  { value: 'ForeignKey', label: 'FK' },
  { value: 'ManyToManyField', label: 'M2M' },
]

const FORM_FIELD_TYPES = [
  { value: 'text', label: 'TEXT' },
  { value: 'email', label: 'EMAIL' },
  { value: 'number', label: 'NUM' },
  { value: 'textarea', label: 'TEXT' },
  { value: 'select', label: 'SELECT' },
  { value: 'checkbox', label: 'CHECK' },
  { value: 'date', label: 'DATE' },
]

const OPERATIONS = ['list', 'create', 'detail', 'update', 'delete']
const STYLES = ['tailwind', 'bootstrap', 'plain']

export default function ResourcePage() {
  const [apiUrl] = useState(typeof window !== 'undefined' ? window.location.origin : 'http://localhost:6767')
  const [projectPath] = useState('.')
  const [activeTab, setActiveTab] = useState<Tab>('models')

  // Models state
  const [appName, setAppName] = useState('')
  const [modelName, setModelName] = useState('')
  const [modelFields, setModelFields] = useState<ModelField[]>([
    { name: 'name', field_type: 'CharField', required: true, unique: false, max_length: 255, related_model: null, on_delete: 'CASCADE' }
  ])
  const [migrate, setMigrate] = useState(false)
  const [createdModels, setCreatedModels] = useState<CreatedModel[]>([])
  const [enabledOps, setEnabledOps] = useState({ list: true, create: true, detail: true, update: true, delete: true })

  // Forms state
  const [formName, setFormName] = useState('')
  const [formStyle, setFormStyle] = useState('tailwind')
  const [formFields, setFormFields] = useState<FormField[]>([
    { name: 'name', field_type: 'text', label: 'Name', placeholder: '', required: true }
  ])
  const [createdForms, setCreatedForms] = useState<CreatedForm[]>([])

  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem('lazydjango_models')
    if (saved) setCreatedModels(JSON.parse(saved))
    const savedForms = localStorage.getItem('lazydjango_forms')
    if (savedForms) setCreatedForms(JSON.parse(savedForms))
    fetchApps()
  }, [])

  const fetchApps = async () => {
    try {
      const res = await fetch(apiUrl + '/api/project/apps/?project_path=' + encodeURIComponent(projectPath))
      if (res.ok) {
        const data = await res.json()
        if (data.data?.apps?.length > 0) setAppName(data.data.apps[0])
      }
    } catch (e) {}
  }

  // Model handlers
  const addModelField = () => {
    setModelFields([...modelFields, { name: '', field_type: 'CharField', required: true, unique: false, max_length: 255, related_model: null, on_delete: 'CASCADE' }])
  }

  const removeModelField = (i: number) => {
    setModelFields(modelFields.filter((_, idx) => idx !== i))
  }

  const updateModelField = (i: number, key: keyof ModelField, value: any) => {
    const newFields = [...modelFields]
    newFields[i] = { ...newFields[i], [key]: value }
    setModelFields(newFields)
  }

  const createModel = async () => {
    if (!appName || !modelName) {
      setResult({ success: false, message: 'App name and model name required' })
      return
    }
    const validFields = modelFields.filter(f => f.name)
    if (validFields.length === 0) {
      setResult({ success: false, message: 'At least one field required' })
      return
    }

    setLoading(true)
    try {
      const res = await fetch(apiUrl + '/api/models/create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app_name: appName, model_name: modelName, fields: validFields, migrate, project_path: projectPath })
      })
      const data = await res.json()
      setResult(data)
      if (data.success) {
        const newModel: CreatedModel = { app_name: appName, model_name: modelName, fields: validFields, created_at: new Date().toISOString() }
        const updated = [newModel, ...createdModels.filter(m => m.model_name !== modelName)]
        setCreatedModels(updated)
        localStorage.setItem('lazydjango_models', JSON.stringify(updated))

        await createEndpoints(newModel)
      }
    } catch (e) {
      setResult({ success: false, message: 'Failed to connect to API' })
    } finally {
      setLoading(false)
    }
  }

  const createEndpoints = async (model: CreatedModel) => {
    try {
      await fetch(apiUrl + '/api/views/create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: model.app_name,
          model_name: model.model_name,
          view_type: 'api',
          operations: enabledOps,
          project_path: projectPath
        })
      })
    } catch (e) {}
  }

  const deleteModel = (model_name: string) => {
    const updated = createdModels.filter(m => m.model_name !== model_name)
    setCreatedModels(updated)
    localStorage.setItem('lazydjango_models', JSON.stringify(updated))
  }

  // Form handlers
  const addFormField = () => {
    setFormFields([...formFields, { name: '', field_type: 'text', label: '', placeholder: '', required: true }])
  }

  const removeFormField = (i: number) => {
    setFormFields(formFields.filter((_, idx) => idx !== i))
  }

  const updateFormField = (i: number, key: keyof FormField, value: any) => {
    const newFields = [...formFields]
    newFields[i] = { ...newFields[i], [key]: value }
    setFormFields(newFields)
  }

  const createForm = async () => {
    if (!formName) {
      setResult({ success: false, message: 'Form name required' })
      return
    }

    setLoading(true)
    try {
      const res = await fetch(apiUrl + '/api/forms/create/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: appName,
          model_name: formName,
          gen_type: 'form',
          style: formStyle,
          project_path: projectPath
        })
      })
      const data = await res.json()
      setResult(data)
      if (data.success) {
        const newForm: CreatedForm = { form_name: formName, style: formStyle, fields: formFields }
        setCreatedForms([...createdForms, newForm])
        localStorage.setItem('lazydjango_forms', JSON.stringify(createdForms))
      }
    } catch (e) {
      setResult({ success: false, message: 'Failed to connect to API' })
    } finally {
      setLoading(false)
    }
  }

  const sqlPreview = () => {
    const lines: string[] = []
    lines.push('class ' + (modelName || 'ModelName') + '(models.Model):')
    for (const field of modelFields) {
      if (!field.name) continue
      let def = '    ' + field.name + ' = models.' + field.field_type
      if (field.field_type === 'CharField') def += '(max_length=' + (field.max_length || 255) + ')'
      if (['ForeignKey', 'OneToOneField'].includes(field.field_type) && field.related_model) {
        def = '    ' + field.name + ' = models.ForeignKey("' + field.related_model + '", on_delete=models.' + field.on_delete + ')'
      } else if (field.field_type === 'ManyToManyField' && field.related_model) {
        def = '    ' + field.name + ' = models.ManyToManyField("' + field.related_model + '")'
      } else if (field.field_type === 'BooleanField') {
        def = '    ' + field.name + ' = models.BooleanField(default=False)'
      }
      if (!field.required) def += ', blank=True'
      if (field.unique) def += ', unique=True'
      lines.push(def)
    }
    return lines.join('\n')
  }

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex border-b" style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}>
        <button
          onClick={() => setActiveTab('models')}
          className="flex items-center gap-2 px-6 py-3 text-xs tracking-wider font-bold"
          style={{
            background: activeTab === 'models' ? 'var(--accent)' : 'transparent',
            color: activeTab === 'models' ? 'var(--bg)' : 'var(--text-secondary)',
          }}
        >
          <Box className="w-4 h-4" />
          MODELS
        </button>
        <button
          onClick={() => setActiveTab('endpoints')}
          className="flex items-center gap-2 px-6 py-3 text-xs tracking-wider font-bold"
          style={{
            background: activeTab === 'endpoints' ? 'var(--accent)' : 'transparent',
            color: activeTab === 'endpoints' ? 'var(--bg)' : 'var(--text-secondary)',
          }}
        >
          <FileCode className="w-4 h-4" />
          ENDPOINTS
        </button>
        <button
          onClick={() => setActiveTab('forms')}
          className="flex items-center gap-2 px-6 py-3 text-xs tracking-wider font-bold"
          style={{
            background: activeTab === 'forms' ? 'var(--accent)' : 'transparent',
            color: activeTab === 'forms' ? 'var(--bg)' : 'var(--text-secondary)',
          }}
        >
          <LayoutList className="w-4 h-4" />
          FORMS
        </button>
      </div>

      {/* Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Main Panel */}
        <div className="flex-1 p-4 overflow-y-auto">
          {/* MODELS TAB */}
          {activeTab === 'models' && (
            <>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div>
                    <label className="text-xs tracking-wider mb-1 block" style={{ color: 'var(--text-muted)' }}>APP</label>
                    <input type="text" value={appName} onChange={(e) => setAppName(e.target.value)} className="w-32 text-sm" />
                  </div>
                  <div>
                    <label className="text-xs tracking-wider mb-1 block" style={{ color: 'var(--text-muted)' }}>MODEL</label>
                    <input type="text" value={modelName} onChange={(e) => setModelName(e.target.value)} placeholder="Product" className="w-32 text-sm" />
                  </div>
                  <label className="flex items-center gap-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                    <input type="checkbox" checked={migrate} onChange={(e) => setMigrate(e.target.checked)} />
                    MIGRATE
                  </label>
                </div>
                <button onClick={createModel} disabled={loading} className="flex items-center gap-2 text-sm font-bold px-4 py-2" style={{ background: 'var(--accent)', color: 'var(--bg)' }}>
                  <Play className="w-4 h-4" />
                  {loading ? '...' : 'CREATE'}
                </button>
              </div>

              <div className="flex items-center justify-between mb-2">
                <span className="text-xs tracking-wider font-bold" style={{ color: 'var(--text-muted)' }}>FIELDS</span>
                <button onClick={addModelField} className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-muted)' }}>
                  <Plus className="w-3 h-3" /> ADD
                </button>
              </div>

              <div className="border" style={{ borderColor: 'var(--border)' }}>
                <div className="grid grid-cols-[1fr_100px_80px_80px_100px_40px] gap-0 px-3 py-2 text-xs tracking-wider" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-muted)' }}>
                  <div>NAME</div><div>TYPE</div><div>MAX</div><div>NULL</div><div>FK</div><div></div>
                </div>
                {modelFields.map((field, i) => (
                  <div key={i} className="grid grid-cols-[1fr_100px_80px_80px_100px_40px] gap-0 px-3 py-2 border-t items-center" style={{ borderColor: 'var(--border)' }}>
                    <input type="text" value={field.name} onChange={(e) => updateModelField(i, 'name', e.target.value)} className="text-sm bg-transparent" />
                    <select value={field.field_type} onChange={(e) => updateModelField(i, 'field_type', e.target.value)} className="text-sm bg-transparent">
                      {FIELD_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                    <input type="number" value={field.max_length || ''} onChange={(e) => updateModelField(i, 'max_length', e.target.value ? parseInt(e.target.value) : null)} disabled={field.field_type !== 'CharField'} className="text-sm bg-transparent" />
                    <div className="flex justify-center"><input type="checkbox" checked={!field.required} onChange={(e) => updateModelField(i, 'required', !e.target.checked)} /></div>
                    <select value={field.related_model || ''} onChange={(e) => updateModelField(i, 'related_model', e.target.value || null)} className="text-sm bg-transparent">
                      <option value="">-</option>
                      {createdModels.map(m => <option key={m.model_name} value={m.model_name}>{m.model_name}</option>)}
                    </select>
                    <button onClick={() => removeModelField(i)} className="p-1" style={{ color: 'var(--text-muted)' }}><Trash2 className="w-3 h-3" /></button>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* ENDPOINTS TAB */}
          {activeTab === 'endpoints' && (
            <>
              <div className="mb-4">
                <label className="text-xs tracking-wider mb-2 block" style={{ color: 'var(--text-muted)' }}>SELECT MODEL</label>
                <select className="w-full max-w-xs" onChange={(e) => {
                  const m = createdModels.find(x => x.model_name === e.target.value)
                  if (m) {
                    setModelName(m.model_name)
                    setAppName(m.app_name)
                  }
                }}>
                  <option value="">-- Select --</option>
                  {createdModels.map(m => <option key={m.model_name} value={m.model_name}>{m.app_name}/{m.model_name}</option>)}
                </select>
              </div>

              <div className="mb-4">
                <label className="text-xs tracking-wider mb-2 block" style={{ color: 'var(--text-muted)' }}>OPERATIONS</label>
                <div className="flex gap-2">
                  {OPERATIONS.map(op => (
                    <button
                      key={op}
                      onClick={() => setEnabledOps(prev => ({ ...prev, [op]: !prev[op as keyof typeof prev] }))}
                      className="px-3 py-2 text-xs"
                      style={{
                        background: enabledOps[op as keyof typeof enabledOps] ? 'var(--accent)' : 'transparent',
                        color: enabledOps[op as keyof typeof enabledOps] ? 'var(--bg)' : 'var(--text-muted)',
                        border: '1px solid var(--border)'
                      }}
                    >
                      {op}
                    </button>
                  ))}
                </div>
              </div>

              <div className="border p-4" style={{ borderColor: 'var(--border)', background: 'var(--bg)' }}>
                <label className="text-xs tracking-wider mb-2 block" style={{ color: 'var(--text-muted)' }}>ENDPOINTS PREVIEW</label>
                <div className="space-y-1">
                  {OPERATIONS.filter(op => enabledOps[op as keyof typeof enabledOps]).map(op => {
                    const colors: Record<string, string> = { list: '#22c55e', create: '#3b82f6', detail: '#22c55e', update: '#eab308', delete: '#ef4444' }
                    const methods: Record<string, string> = { list: 'GET', create: 'POST', detail: 'GET', update: 'PUT', delete: 'DELETE' }
                    const path = '/' + (modelName || '{model}').toLowerCase() + (op === 'list' || op === 'create' ? '/' : '/{id}/')
                    return (
                      <div key={op} className="flex items-center gap-3">
                        <span className="text-xs px-2 py-1 font-bold" style={{ background: colors[op], color: '#fff' }}>{methods[op]}</span>
                        <code className="text-xs" style={{ color: 'var(--accent)' }}>{path}</code>
                      </div>
                    )
                  })}
                </div>
              </div>

              <button
                onClick={async () => {
                  const m = createdModels.find(x => x.model_name === modelName)
                  if (m) await createEndpoints(m)
                }}
                disabled={!modelName || loading}
                className="mt-4 flex items-center gap-2 text-sm font-bold px-4 py-2"
                style={{ background: 'var(--accent)', color: 'var(--bg)' }}
              >
                <Play className="w-4 h-4" />
                GENERATE
              </button>
            </>
          )}

          {/* FORMS TAB */}
          {activeTab === 'forms' && (
            <>
              <div className="mb-4">
                <label className="text-xs tracking-wider mb-1 block" style={{ color: 'var(--text-muted)' }}>FORM NAME</label>
                <input type="text" value={formName} onChange={(e) => setFormName(e.target.value)} placeholder="ContactForm" className="w-48 text-sm" />
              </div>

              <div className="mb-4">
                <label className="text-xs tracking-wider mb-2 block" style={{ color: 'var(--text-muted)' }}>STYLE</label>
                <div className="flex gap-2">
                  {STYLES.map(s => (
                    <button
                      key={s}
                      onClick={() => setFormStyle(s)}
                      className="px-3 py-2 text-xs"
                      style={{
                        background: formStyle === s ? 'var(--accent)' : 'transparent',
                        color: formStyle === s ? 'var(--bg)' : 'var(--text-secondary)',
                        border: '1px solid var(--border)'
                      }}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between mb-2">
                <span className="text-xs tracking-wider font-bold" style={{ color: 'var(--text-muted)' }}>FIELDS</span>
                <button onClick={addFormField} className="flex items-center gap-1 text-xs" style={{ color: 'var(--text-muted)' }}>
                  <Plus className="w-3 h-3" /> ADD
                </button>
              </div>

              <div className="border" style={{ borderColor: 'var(--border)' }}>
                <div className="grid grid-cols-[1fr_100px_1fr_1fr_80px_40px] gap-0 px-3 py-2 text-xs tracking-wider" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-muted)' }}>
                  <div>NAME</div><div>TYPE</div><div>LABEL</div><div>PLACEHOLDER</div><div>NULL</div><div></div>
                </div>
                {formFields.map((field, i) => (
                  <div key={i} className="grid grid-cols-[1fr_100px_1fr_1fr_80px_40px] gap-0 px-3 py-2 border-t items-center" style={{ borderColor: 'var(--border)' }}>
                    <input type="text" value={field.name} onChange={(e) => updateFormField(i, 'name', e.target.value)} className="text-sm bg-transparent" />
                    <select value={field.field_type} onChange={(e) => updateFormField(i, 'field_type', e.target.value)} className="text-sm bg-transparent">
                      {FORM_FIELD_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                    <input type="text" value={field.label} onChange={(e) => updateFormField(i, 'label', e.target.value)} className="text-sm bg-transparent" />
                    <input type="text" value={field.placeholder} onChange={(e) => updateFormField(i, 'placeholder', e.target.value)} className="text-sm bg-transparent" />
                    <div className="flex justify-center"><input type="checkbox" checked={!field.required} onChange={(e) => updateFormField(i, 'required', !e.target.checked)} /></div>
                    <button onClick={() => removeFormField(i)} className="p-1" style={{ color: 'var(--text-muted)' }}><Trash2 className="w-3 h-3" /></button>
                  </div>
                ))}
              </div>

              <button onClick={createForm} disabled={loading} className="mt-4 flex items-center gap-2 text-sm font-bold px-4 py-2" style={{ background: 'var(--accent)', color: 'var(--bg)' }}>
                <Play className="w-4 h-4" />
                {loading ? '...' : 'CREATE'}
              </button>
            </>
          )}
        </div>

        {/* Sidebar */}
        <div className="w-64 border-l p-4 overflow-y-auto" style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}>
          {activeTab === 'models' && (
            <>
              <div className="mb-4">
                <span className="text-xs tracking-wider font-bold block mb-2" style={{ color: 'var(--text-muted)' }}>SQL PREVIEW</span>
                <pre className="text-xs p-3 border" style={{ borderColor: 'var(--border)', background: 'var(--bg)', color: 'var(--accent)', maxHeight: '200px', overflow: 'auto' }}>
                  {sqlPreview() || '-- Define fields'}
                </pre>
              </div>

              <div>
                <span className="text-xs tracking-wider font-bold block mb-2" style={{ color: 'var(--text-muted)' }}>MODELS ({createdModels.length})</span>
                {createdModels.length === 0 && <div className="text-xs" style={{ color: 'var(--text-muted)' }}>No models</div>}
                {createdModels.map(m => (
                  <div key={m.model_name} className="border p-2 mb-2" style={{ borderColor: 'var(--border)' }}>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{m.model_name}</span>
                      <button onClick={() => deleteModel(m.model_name)} className="text-xs" style={{ color: 'var(--error)' }}>DEL</button>
                    </div>
                    <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{m.app_name} - {m.fields.length} fields</div>
                  </div>
                ))}
              </div>
            </>
          )}

          {activeTab === 'endpoints' && (
            <div>
              <span className="text-xs tracking-wider font-bold block mb-2" style={{ color: 'var(--text-muted)' }}>MODELS</span>
              {createdModels.map(m => (
                <div key={m.model_name} className="border p-2 mb-2" style={{ borderColor: 'var(--border)' }}>
                  <div className="text-sm font-medium">{m.model_name}</div>
                  <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{m.app_name}</div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'forms' && (
            <div>
              <span className="text-xs tracking-wider font-bold block mb-2" style={{ color: 'var(--text-muted)' }}>FORMS ({createdForms.length})</span>
              {createdForms.length === 0 && <div className="text-xs" style={{ color: 'var(--text-muted)' }}>No forms</div>}
              {createdForms.map(f => (
                <div key={f.form_name} className="border p-2 mb-2" style={{ borderColor: 'var(--border)' }}>
                  <span className="text-sm font-medium">{f.form_name}</span>
                  <div className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{f.style} - {f.fields.length} fields</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Result Toast */}
      {result && (
        <div className="absolute bottom-4 right-4 border p-3 max-w-sm" style={{ borderColor: result.success ? 'var(--success)' : 'var(--error)', background: 'var(--bg-secondary)' }}>
          <span className="text-sm" style={{ color: result.success ? 'var(--success)' : 'var(--error)' }}>{result.message}</span>
        </div>
      )}
    </div>
  )
}
