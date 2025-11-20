
import { User, UserProfile, SignalLite, FollowedSignal } from '../types';

// Mock user database
const MOCK_USER: User = {
  id: 'u_123',
  email: 'demo@tradercopilot.com',
  name: 'Pancho Trader',
  role: 'admin',
  avatar_url: 'https://ui-avatars.com/api/?name=Pancho+Trader&background=10b981&color=fff',
  subscription_status: 'active',
  onboarding_completed: false // Default to false for demo to show the widget
};

const DEFAULT_PROFILE: UserProfile = {
  user: MOCK_USER,
  preferences: {
    favorite_tokens: ['eth', 'btc', 'sol'],
    default_timeframe: '30m',
    notifications: {
        trade_updates: true,
        market_volatility: true,
        system_status: false
    }
  },
  portfolio: {
    followed_signals: []
  }
};

export const authService = {
  login: async (email: string, password: string): Promise<UserProfile> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));

    if (email === 'demo@tradercopilot.com' && password === 'demo') {
      // Try to load from local storage to persist between reloads
      const stored = localStorage.getItem('tradercopilot_user');
      let profile = stored ? JSON.parse(stored) : DEFAULT_PROFILE;
      
      // Ensure notification prefs exist if loading old profile format
      if (!profile.preferences.notifications) {
          profile.preferences.notifications = DEFAULT_PROFILE.preferences.notifications;
      }
      
      localStorage.setItem('tradercopilot_user', JSON.stringify(profile));
      return profile;
    }
    throw new Error('Invalid credentials');
  },

  logout: async () => {
    localStorage.removeItem('tradercopilot_user');
  },

  getCurrentUser: (): UserProfile | null => {
    const stored = localStorage.getItem('tradercopilot_user');
    if (!stored) return null;
    const profile = JSON.parse(stored);
    // Migration check for new fields
    if (!profile.preferences.notifications) {
        profile.preferences.notifications = DEFAULT_PROFILE.preferences.notifications;
    }
    return profile;
  },

  updateProfile: async (name: string, favorites: string[]): Promise<UserProfile> => {
    const current = authService.getCurrentUser();
    if (!current) throw new Error('No session');

    const updated: UserProfile = {
      ...current,
      user: { ...current.user, name, avatar_url: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=10b981&color=fff` },
      preferences: { ...current.preferences, favorite_tokens: favorites }
    };

    localStorage.setItem('tradercopilot_user', JSON.stringify(updated));
    return updated;
  },

  toggleFollowSignal: async (signal: SignalLite): Promise<UserProfile> => {
    const current = authService.getCurrentUser();
    if (!current) throw new Error('No session');

    const existingIdx = current.portfolio.followed_signals.findIndex(
      s => s.timestamp === signal.timestamp && s.token === signal.token
    );

    let newSignals = [...current.portfolio.followed_signals];

    if (existingIdx >= 0) {
      // Unfollow
      newSignals.splice(existingIdx, 1);
    } else {
      // Follow (Mocking a status for the portfolio view)
      const newSignal: FollowedSignal = {
        ...signal,
        followed_at: new Date().toISOString(),
        status: 'OPEN', 
        final_pnl: 0,
        notes: ''
      };
      newSignals.push(newSignal);
    }

    const updated = {
      ...current,
      portfolio: { ...current.portfolio, followed_signals: newSignals }
    };

    localStorage.setItem('tradercopilot_user', JSON.stringify(updated));
    return updated;
  },

  updateSignalNote: async (timestamp: string, token: string, note: string): Promise<UserProfile> => {
    const current = authService.getCurrentUser();
    if (!current) throw new Error('No session');

    const newSignals = current.portfolio.followed_signals.map(s => {
      if (s.timestamp === timestamp && s.token === token) {
        return { ...s, notes: note };
      }
      return s;
    });

    const updated = {
      ...current,
      portfolio: { ...current.portfolio, followed_signals: newSignals }
    };

    localStorage.setItem('tradercopilot_user', JSON.stringify(updated));
    return updated;
  },

  completeOnboarding: async (): Promise<UserProfile> => {
    const current = authService.getCurrentUser();
    if (!current) throw new Error('No session');
    
    const updated = {
        ...current,
        user: { ...current.user, onboarding_completed: true }
    };
    localStorage.setItem('tradercopilot_user', JSON.stringify(updated));
    return updated;
  }
};
