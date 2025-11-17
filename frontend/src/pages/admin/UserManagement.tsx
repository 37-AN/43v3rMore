import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import StatCard from '@/components/dashboard/StatCard';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Input from '@/components/ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/Select';
import { Users, UserPlus, UserCheck, UserX, Search } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

interface User {
  id: string;
  name: string;
  email: string;
  phone: string;
  plan: string;
  status: string;
  created_at: string;
  last_active: string;
  mrr_contribution: number;
}

export const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [planFilter, setPlanFilter] = useState('all');

  useEffect(() => {
    fetchUsers();
  }, [statusFilter, planFilter]);

  const fetchUsers = async () => {
    try {
      const params: any = { limit: 100 };
      if (statusFilter !== 'all') params.status = statusFilter;
      if (planFilter !== 'all') params.plan = planFilter;

      const response = await apiClient.getUsers(params);
      setUsers(response.users || mockUsers);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setUsers(mockUsers);
    }
  };

  // Mock data
  const mockUsers: User[] = [
    {
      id: '1',
      name: 'John Trader',
      email: 'john@example.com',
      phone: '+27 82 123 4567',
      plan: 'pro',
      status: 'active',
      created_at: '2025-10-15T10:30:00Z',
      last_active: '2025-11-17T09:15:00Z',
      mrr_contribution: 1000,
    },
    {
      id: '2',
      name: 'Sarah Investor',
      email: 'sarah@example.com',
      phone: '+27 83 234 5678',
      plan: 'premium',
      status: 'active',
      created_at: '2025-09-20T14:20:00Z',
      last_active: '2025-11-16T18:45:00Z',
      mrr_contribution: 2000,
    },
    {
      id: '3',
      name: 'Mike Charts',
      email: 'mike@example.com',
      phone: '+27 84 345 6789',
      plan: 'basic',
      status: 'trial',
      created_at: '2025-11-10T08:00:00Z',
      last_active: '2025-11-17T07:30:00Z',
      mrr_contribution: 0,
    },
  ];

  const filteredUsers = users.filter((user) =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalUsers = users.length;
  const activeUsers = users.filter((u) => u.status === 'active').length;
  const trialUsers = users.filter((u) => u.status === 'trial').length;
  const totalMRR = users.reduce((sum, u) => sum + u.mrr_contribution, 0);

  const getPlanBadgeVariant = (plan: string) => {
    switch (plan) {
      case 'premium':
        return 'default';
      case 'pro':
        return 'info';
      case 'basic':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'trial':
        return 'warning';
      case 'inactive':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">User Management</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            Manage subscribers and user accounts
          </p>
        </div>
        <Button variant="primary">
          <UserPlus className="h-4 w-4 mr-2" />
          Add User
        </Button>
      </div>

      {/* User Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Users"
          value={totalUsers}
          icon={Users}
          color="blue"
          trend={{ value: 15, label: 'vs last month' }}
        />
        <StatCard
          title="Active Subscribers"
          value={activeUsers}
          icon={UserCheck}
          color="green"
        />
        <StatCard
          title="Trial Users"
          value={trialUsers}
          icon={UserX}
          color="yellow"
        />
        <StatCard
          title="Total MRR"
          value={formatCurrency(totalMRR, 'ZAR')}
          icon={Users}
          color="green"
          trend={{ value: 22, label: 'vs last month' }}
        />
      </div>

      {/* Filters and Search */}
      <Card className="p-6">
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search users by name or email..."
              value={searchTerm}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-full md:w-40">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="trial">Trial</SelectItem>
              <SelectItem value="inactive">Inactive</SelectItem>
            </SelectContent>
          </Select>
          <Select value={planFilter} onValueChange={setPlanFilter}>
            <SelectTrigger className="w-full md:w-40">
              <SelectValue placeholder="Plan" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Plans</SelectItem>
              <SelectItem value="basic">Basic</SelectItem>
              <SelectItem value="pro">Pro</SelectItem>
              <SelectItem value="premium">Premium</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Users Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="text-left p-3">Name</th>
                <th className="text-left p-3">Email</th>
                <th className="text-left p-3">Phone</th>
                <th className="text-left p-3">Plan</th>
                <th className="text-left p-3">Status</th>
                <th className="text-right p-3">MRR</th>
                <th className="text-left p-3">Registered</th>
                <th className="text-left p-3">Last Active</th>
                <th className="text-right p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id} className="border-b border-slate-100 dark:border-slate-800">
                  <td className="p-3 font-medium">{user.name}</td>
                  <td className="p-3 text-slate-600 dark:text-slate-400">{user.email}</td>
                  <td className="p-3 text-slate-600 dark:text-slate-400">{user.phone}</td>
                  <td className="p-3">
                    <Badge variant={getPlanBadgeVariant(user.plan)}>
                      {user.plan.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge variant={getStatusBadgeVariant(user.status)}>
                      {user.status}
                    </Badge>
                  </td>
                  <td className="p-3 text-right font-medium">
                    {formatCurrency(user.mrr_contribution, 'ZAR')}
                  </td>
                  <td className="p-3 text-sm text-slate-600 dark:text-slate-400">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="p-3 text-sm text-slate-600 dark:text-slate-400">
                    {new Date(user.last_active).toLocaleDateString()}
                  </td>
                  <td className="p-3 text-right">
                    <Button size="sm" variant="secondary">
                      View
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredUsers.length === 0 && (
          <div className="text-center py-12 text-slate-600 dark:text-slate-400">
            No users found matching your filters
          </div>
        )}
      </Card>
    </div>
  );
};

export default UserManagement;
