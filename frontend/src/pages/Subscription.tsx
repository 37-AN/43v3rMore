import React, { useState } from 'react';
import { Check, Zap } from 'lucide-react';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import type { PlanInfo } from '@/types';
import { toast } from '@/components/ui/Toast';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

const plans: PlanInfo[] = [
  {
    name: 'Basic',
    price: 500,
    signalsPerDay: '5 signals/day',
    features: [
      'Major currency pairs',
      'Email delivery',
      'Basic support',
      '75% accuracy guarantee',
    ],
  },
  {
    name: 'Pro',
    price: 1000,
    signalsPerDay: '10 signals/day',
    features: [
      'All currency pairs',
      'Multi-channel delivery',
      'Priority support',
      '85% accuracy guarantee',
      'Advanced analytics',
    ],
    popular: true,
  },
  {
    name: 'Premium',
    price: 2000,
    signalsPerDay: 'Unlimited signals',
    features: [
      'All pairs + commodities',
      'Real-time delivery',
      '24/7 VIP support',
      '95% accuracy guarantee',
      'Advanced analytics',
      'Custom alerts',
    ],
  },
  {
    name: 'Bot License',
    price: 3000,
    signalsPerDay: 'Automated trading',
    features: [
      'Automated trading bot',
      'All Premium features',
      'Risk management',
      'Performance tracking',
      'Bot customization',
    ],
  },
  {
    name: 'Enterprise',
    price: 10000,
    signalsPerDay: 'Custom solutions',
    features: [
      'All features',
      'API access',
      'Custom integrations',
      'Dedicated account manager',
      'Custom strategies',
      'White-label options',
    ],
  },
];

const Subscription: React.FC = () => {
  const { user } = useAuthStore();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubscribe = async (planName: string) => {
    setIsLoading(true);
    setSelectedPlan(planName);

    try {
      await api.createSubscription(planName.toLowerCase());
      toast.success(`Successfully subscribed to ${planName} plan!`);
    } catch (error) {
      toast.error('Failed to create subscription. Please try again.');
    } finally {
      setIsLoading(false);
      setSelectedPlan(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
          Choose Your Plan
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-400">
          Select the perfect plan for your trading needs. All plans include
          quantum-powered signal generation and comprehensive support.
        </p>
      </div>

      {/* Current Plan */}
      {user?.plan && (
        <Card padding="md" className="max-w-2xl mx-auto bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Current Plan
              </p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white capitalize">
                {user.plan}
              </p>
            </div>
            <Badge variant="success">Active</Badge>
          </div>
        </Card>
      )}

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {plans.map((plan) => (
          <Card
            key={plan.name}
            padding="md"
            variant={plan.popular ? 'elevated' : 'default'}
            className={`relative ${
              plan.popular
                ? 'ring-2 ring-primary-600 dark:ring-primary-400'
                : ''
            }`}
          >
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <Badge variant="info" className="px-3 py-1">
                  <Zap className="w-3 h-3 mr-1 inline" />
                  Popular
                </Badge>
              </div>
            )}

            <div className="space-y-4">
              {/* Plan Name */}
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                  {plan.name}
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {plan.signalsPerDay}
                </p>
              </div>

              {/* Price */}
              <div>
                <div className="flex items-baseline gap-1">
                  <span className="text-3xl font-bold text-slate-900 dark:text-white">
                    R{plan.price.toLocaleString()}
                  </span>
                  <span className="text-slate-600 dark:text-slate-400">
                    /month
                  </span>
                </div>
              </div>

              {/* Features */}
              <ul className="space-y-3">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-slate-700 dark:text-slate-300">
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <Button
                variant={plan.popular ? 'primary' : 'ghost'}
                size="lg"
                className="w-full"
                onClick={() => handleSubscribe(plan.name)}
                isLoading={isLoading && selectedPlan === plan.name}
                disabled={
                  user?.plan?.toLowerCase() === plan.name.toLowerCase()
                }
              >
                {user?.plan?.toLowerCase() === plan.name.toLowerCase()
                  ? 'Current Plan'
                  : 'Subscribe'}
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* FAQ Section */}
      <div className="max-w-3xl mx-auto mt-12">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
          Frequently Asked Questions
        </h2>
        <div className="space-y-4">
          <Card padding="md">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
              Can I change my plan later?
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Yes, you can upgrade or downgrade your plan at any time. Changes
              will be reflected in your next billing cycle.
            </p>
          </Card>
          <Card padding="md">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
              What payment methods do you accept?
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              We accept all major credit cards and PayFast for South African
              payments.
            </p>
          </Card>
          <Card padding="md">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-2">
              Is there a free trial?
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Yes! All new users get a 7-day free trial on any plan to test
              our signal accuracy.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Subscription;
