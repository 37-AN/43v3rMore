import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock } from 'lucide-react';
import { useAuthStore } from '@/store/auth';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { toast } from '@/components/ui/Toast';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading, error } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await login(email, password);
      toast.success('Login successful!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(error || 'Login failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-slate-950 dark:to-slate-900 px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-xl" />
            <span className="text-2xl font-bold text-slate-900 dark:text-white">
              Quantum Trading AI
            </span>
          </div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">
            Welcome Back
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mt-2">
            Sign in to access your trading signals
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl p-8 border border-slate-200 dark:border-slate-800">
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              leftIcon={<Mail className="w-5 h-5" />}
              required
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              leftIcon={<Lock className="w-5 h-5" />}
              required
            />

            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="w-4 h-4 text-primary-600 border-slate-300 rounded focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-slate-600 dark:text-slate-400">
                  Remember me
                </span>
              </label>
              <Link
                to="/forgot-password"
                className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              isLoading={isLoading}
            >
              Sign In
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Don't have an account?{' '}
              <Link
                to="/signup"
                className="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400"
              >
                Sign up
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-slate-500 dark:text-slate-500 mt-8">
          By signing in, you agree to our{' '}
          <a href="#" className="underline hover:text-slate-700 dark:hover:text-slate-300">
            Terms of Service
          </a>{' '}
          and{' '}
          <a href="#" className="underline hover:text-slate-700 dark:hover:text-slate-300">
            Privacy Policy
          </a>
        </p>
      </div>
    </div>
  );
};

export default Login;
