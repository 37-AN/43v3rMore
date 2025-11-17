import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { Input } from '@/components/ui/Input';
import { Switch } from '@/components/ui/Switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { Separator } from '@/components/ui/Separator';
import { Save, RefreshCw, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api';

export const Configuration: React.FC = () => {
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getConfig();
      setConfig(data || mockConfig);
    } catch (err) {
      console.error('Failed to fetch configuration:', err);
      setConfig(mockConfig);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (section: string) => {
    try {
      setSaving(true);
      await apiClient.updateConfig(section, config[section]);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save configuration:', err);
    } finally {
      setSaving(false);
    }
  };

  // Mock config
  const mockConfig = {
    quantum: {
      default_qubits: 5,
      backend: 'ibmq_qasm_simulator',
      error_mitigation: true,
      min_confidence: 0.95,
    },
    mt5: {
      server: 'Demo-MT5',
      account: '********',
      auto_trading: false,
      max_position_size: 0.1,
      risk_per_trade: 1.0,
    },
    notifications: {
      telegram_token: '********',
      whatsapp_enabled: true,
      smtp_server: 'smtp.gmail.com',
      sms_provider: 'Twilio',
    },
    payfast: {
      merchant_id: '********',
      merchant_key: '********',
      sandbox_mode: true,
    },
  };

  if (loading || !config) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">System Configuration</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Configure system-wide settings and integrations
        </p>
      </div>

      {saveSuccess && (
        <Alert variant="success" title="Configuration Saved">
          Your changes have been saved successfully. Some changes may require a service restart.
        </Alert>
      )}

      <Tabs defaultValue="quantum" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="quantum">Quantum Engine</TabsTrigger>
          <TabsTrigger value="mt5">MT5 Connector</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="payments">Payments</TabsTrigger>
        </TabsList>

        <TabsContent value="quantum" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Quantum Engine Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Default Qubits</label>
                <Input
                  type="number"
                  value={config.quantum.default_qubits}
                  min={3}
                  max={10}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      quantum: { ...config.quantum, default_qubits: parseInt(e.target.value) },
                    })
                  }
                />
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  Range: 3-10 qubits. Restart required.
                </p>
              </div>

              <Separator />

              <div>
                <label className="block text-sm font-medium mb-2">IBM Quantum Backend</label>
                <Select
                  value={config.quantum.backend}
                  onValueChange={(value) =>
                    setConfig({
                      ...config,
                      quantum: { ...config.quantum, backend: value },
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ibmq_qasm_simulator">ibmq_qasm_simulator</SelectItem>
                    <SelectItem value="ibm_brisbane">ibm_brisbane</SelectItem>
                    <SelectItem value="ibm_kyoto">ibm_kyoto</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Restart required.</p>
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm font-medium">Error Mitigation</label>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    Enable quantum error mitigation techniques
                  </p>
                </div>
                <Switch
                  checked={config.quantum.error_mitigation}
                  onCheckedChange={(checked) =>
                    setConfig({
                      ...config,
                      quantum: { ...config.quantum, error_mitigation: checked },
                    })
                  }
                />
              </div>

              <Separator />

              <div>
                <label className="block text-sm font-medium mb-2">Minimum Signal Confidence</label>
                <Input
                  type="number"
                  step="0.01"
                  min="0.80"
                  max="0.99"
                  value={config.quantum.min_confidence}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      quantum: { ...config.quantum, min_confidence: parseFloat(e.target.value) },
                    })
                  }
                />
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  Range: 0.80-0.99. Signals below this threshold will be filtered.
                </p>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={fetchConfig} disabled={saving}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button onClick={() => handleSave('quantum')} disabled={saving}>
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="mt5" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">MT5 Connection Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">MT5 Server</label>
                <Input
                  value={config.mt5.server}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      mt5: { ...config.mt5, server: e.target.value },
                    })
                  }
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Account Number</label>
                <Input type="password" value={config.mt5.account} />
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  Encrypted and stored securely
                </p>
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm font-medium">Auto-Trading Enabled</label>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    Automatically execute trades based on signals
                  </p>
                </div>
                <Switch
                  checked={config.mt5.auto_trading}
                  onCheckedChange={(checked) =>
                    setConfig({
                      ...config,
                      mt5: { ...config.mt5, auto_trading: checked },
                    })
                  }
                />
              </div>

              <Alert variant="warning" title="Caution">
                Auto-trading can result in financial losses. Only enable if you understand the risks.
              </Alert>

              <Separator />

              <div>
                <label className="block text-sm font-medium mb-2">Max Position Size (lots)</label>
                <Input
                  type="number"
                  step="0.01"
                  min="0.01"
                  max="10.0"
                  value={config.mt5.max_position_size}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      mt5: { ...config.mt5, max_position_size: parseFloat(e.target.value) },
                    })
                  }
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Risk Per Trade (%)</label>
                <Input
                  type="number"
                  step="0.1"
                  min="0.1"
                  max="5.0"
                  value={config.mt5.risk_per_trade}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      mt5: { ...config.mt5, risk_per_trade: parseFloat(e.target.value) },
                    })
                  }
                />
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={fetchConfig}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button onClick={() => handleSave('mt5')}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Notification Services</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Telegram Bot Token</label>
                <Input type="password" value={config.notifications.telegram_token} />
              </div>

              <div className="flex items-center justify-between">
                <label className="block text-sm font-medium">WhatsApp API Enabled</label>
                <Switch checked={config.notifications.whatsapp_enabled} />
              </div>

              <Separator />

              <div>
                <label className="block text-sm font-medium mb-2">SMTP Server</label>
                <Input value={config.notifications.smtp_server} />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">SMS Provider</label>
                <Select value={config.notifications.sms_provider}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Twilio">Twilio</SelectItem>
                    <SelectItem value="AWS SNS">AWS SNS</SelectItem>
                    <SelectItem value="Africa's Talking">Africa's Talking</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={fetchConfig}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button onClick={() => handleSave('notifications')}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="payments" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">PayFast Integration</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Merchant ID</label>
                <Input type="password" value={config.payfast.merchant_id} />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Merchant Key</label>
                <Input type="password" value={config.payfast.merchant_key} />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm font-medium">Sandbox Mode</label>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    Use PayFast sandbox for testing
                  </p>
                </div>
                <Switch checked={config.payfast.sandbox_mode} />
              </div>

              <Alert variant="info" title="Security Notice">
                Payment credentials are encrypted at rest and in transit. Never share your merchant
                keys.
              </Alert>

              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={fetchConfig}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button onClick={() => handleSave('payfast')}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Configuration;
