
import React, { useState } from 'react';
import { Check, X, Zap, Crown, Shield, Activity, ArrowRight, Star } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const MembershipPage: React.FC = () => {
  const { userProfile } = useAuth();
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  return (
    <div className="p-6 md:p-12 max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-4 tracking-tight">
          Unlock Full <span className="text-emerald-400">Market Alpha</span>
        </h1>
        <p className="text-slate-400 max-w-2xl mx-auto text-lg">
          Join the top 1% of traders using AI-driven signals, RAG contextual analysis, and automated risk management.
        </p>
        
        {/* Toggle */}
        <div className="mt-8 flex justify-center items-center gap-4">
            <span className={`text-sm font-bold ${billingCycle === 'monthly' ? 'text-white' : 'text-slate-500'}`}>Monthly</span>
            <button 
                onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                className="w-14 h-7 bg-slate-800 rounded-full relative border border-slate-700 transition-colors"
            >
                <div className={`absolute top-1 w-5 h-5 bg-emerald-500 rounded-full transition-all shadow-lg ${billingCycle === 'monthly' ? 'left-1' : 'left-7'}`}></div>
            </button>
            <span className={`text-sm font-bold ${billingCycle === 'yearly' ? 'text-white' : 'text-slate-500'}`}>
                Yearly <span className="text-emerald-400 text-xs ml-1">(Save 20%)</span>
            </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        
        {/* STARTER (Free) */}
        <PlanCard 
            title="Starter" 
            price="$0" 
            period="mo"
            description="For casual traders."
            features={[
                "5 LITE Signals / day",
                "1 PRO Analysis / day",
                "Basic Dashboard Access",
                "Community Leaderboard"
            ]}
            missing={[
                "Advisor (Risk AI)",
                "Real-time Telegram Alerts",
                "API Access",
                "Unlimited Signals"
            ]}
            current={userProfile?.user.subscription_status === 'inactive' || userProfile?.user.subscription_status === 'trial'}
        />

        {/* PLUS ($20) */}
        <PlanCard 
            title="Plus" 
            price={billingCycle === 'monthly' ? "$20" : "$16"} 
            period="mo"
            description="For serious daily traders."
            highlight
            features={[
                "50 LITE Signals / day",
                "25 PRO Analysis / day",
                "25 Advisor Prompts / day",
                "Priority Telegram Alerts",
                "Unlimited Signal Tracking"
            ]}
            missing={[
                "Direct API Access",
                "Unlimited Requests",
                "Whale Club Access"
            ]}
            buttonText="Upgrade to Plus"
            current={userProfile?.user.subscription_status === 'active' && userProfile.user.role === 'user'}
        />

        {/* PRO ($35) */}
        <PlanCard 
            title="Pro Unlimited" 
            price={billingCycle === 'monthly' ? "$35" : "$28"} 
            period="mo"
            description="Maximum power & automation."
            features={[
                "Unlimited LITE Signals",
                "Unlimited PRO Analysis",
                "Unlimited Advisor Mode",
                "Direct API Access",
                "Scenario Management",
                "Priority Support"
            ]}
            buttonText="Go Unlimited"
            current={userProfile?.user.role === 'admin'} // Mock logic for top tier
        />
      </div>

      <div className="mt-16 border-t border-slate-800 pt-12">
        <h3 className="text-center text-xl font-bold text-white mb-8">Frequently Asked Questions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <FAQ q="How accurate are the signals?" a="Our LITE signals maintain a historic 65-72% win rate. Evaluation logs are open and transparent in the app." />
            <FAQ q="Can I cancel anytime?" a="Yes, you can manage your subscription directly from the dashboard. No hidden fees or lock-ins." />
            <FAQ q="What exchanges are supported?" a="Our analysis works for any major CEX (Binance, Bybit) or DEX. The price feed is aggregated from top sources." />
            <FAQ q="Do you offer refunds?" a="We offer a 7-day money-back guarantee if the AI performance does not match the advertised logs." />
        </div>
      </div>
    </div>
  );
};

const PlanCard = ({ title, price, period, description, features, missing, highlight, buttonText, current }: any) => {
    const [loading, setLoading] = useState(false);

    const handleSubscribe = () => {
        setLoading(true);
        // Mock payment flow
        setTimeout(() => {
            setLoading(false);
            alert("Redirecting to Stripe Checkout... (Mock)");
        }, 1000);
    };

    return (
        <div className={`rounded-2xl p-8 flex flex-col relative ${highlight ? 'bg-slate-900 border-2 border-emerald-500 shadow-2xl shadow-emerald-900/20 transform md:-translate-y-4' : 'bg-slate-900 border border-slate-800'}`}>
            {highlight && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-emerald-500 text-white px-4 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1">
                    <Star size={12} fill="currentColor" /> Most Popular
                </div>
            )}
            
            <div className="mb-6">
                <h3 className={`text-lg font-bold ${highlight ? 'text-emerald-400' : 'text-white'}`}>{title}</h3>
                <div className="mt-4 flex items-baseline text-white">
                    <span className="text-4xl font-bold tracking-tight">{price}</span>
                    {period && <span className="ml-1 text-xl font-semibold text-slate-500">/{period}</span>}
                </div>
                <p className="mt-4 text-slate-400 text-sm leading-6">{description}</p>
            </div>

            <ul className="mb-8 space-y-4 flex-1">
                {features.map((feature: string) => (
                    <li key={feature} className="flex items-start gap-3">
                        <Check className={`flex-shrink-0 w-5 h-5 ${highlight ? 'text-emerald-500' : 'text-slate-500'}`} />
                        <span className="text-sm text-slate-300">{feature}</span>
                    </li>
                ))}
                {missing?.map((feature: string) => (
                    <li key={feature} className="flex items-start gap-3 opacity-50">
                        <X className="flex-shrink-0 w-5 h-5 text-slate-600" />
                        <span className="text-sm text-slate-500">{feature}</span>
                    </li>
                ))}
            </ul>

            <button 
                onClick={handleSubscribe}
                disabled={current || loading}
                className={`w-full py-3 px-4 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2 ${
                    current 
                    ? 'bg-slate-800 text-slate-400 cursor-default'
                    : highlight 
                        ? 'bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg shadow-emerald-500/25' 
                        : 'bg-slate-800 hover:bg-slate-700 text-white'
                }`}
            >
                {loading ? 'Processing...' : current ? 'Current Plan' : (buttonText || 'Get Started')}
                {!current && !loading && <ArrowRight size={16} />}
            </button>
        </div>
    );
};

const FAQ = ({ q, a }: { q: string, a: string }) => (
    <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
        <h4 className="font-bold text-white text-sm mb-2">{q}</h4>
        <p className="text-sm text-slate-400 leading-relaxed">{a}</p>
    </div>
);
