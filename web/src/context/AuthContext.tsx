import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile } from '../types';
import { api } from '../services/api';

interface AuthContextType {
    isAuthenticated: boolean;
    isLoading: boolean;
    userProfile: UserProfile | null;
    login: (email?: string, password?: string) => Promise<void>;
    logout: () => void;
    completeOnboarding: () => void;
    updateProfile: (name: string, favorites: string[]) => Promise<void>;
    updateSignalNote: (timestamp: string, token: string, note: string) => Promise<void>;
    toggleFollow: (signal: any) => void;
    upgradeSubscription: (planId: 'free' | 'trader' | 'pro') => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('auth_token');
            if (token) {
                try {
                    // Validate token with backend
                    const data = await api.getMe();

                    // Fetch Entitlements (Permissions/Tokens)
                    let allowedTokens = ['BTC', 'ETH', 'SOL'];
                    try {
                        const ent = await api.get('/auth/me/entitlements');
                        if (ent && ent.allowed_tokens) {
                            allowedTokens = ent.allowed_tokens;
                        }
                    } catch (e) {
                        console.warn('Failed to fetch entitlements', e);
                    }

                    // Map Backend Plan (FREE, PRO, OWNER) to Frontend (free, trader, pro)
                    const backendPlan = data.plan?.toUpperCase() || 'FREE';
                    let frontendPlan: 'free' | 'trader' | 'pro' = 'free';

                    if (backendPlan === 'PRO') frontendPlan = 'trader';
                    if (backendPlan === 'OWNER') frontendPlan = 'pro'; // Owner gets top tier

                    setUserProfile({
                        user: {
                            ...data,
                            role: data.role, // ensure role is passed
                            subscription_status: frontendPlan,
                            onboarding_completed: localStorage.getItem('onboarding_completed') === 'true',
                            avatar_url: data.avatar_url || `https://ui-avatars.com/api/?name=${data.name}&background=10b981&color=fff`,
                            allowed_tokens: allowedTokens
                        },
                        preferences: {
                            favorite_tokens: ['eth', 'btc'],
                            default_timeframe: '30m',
                            notifications: { trade_updates: true, market_volatility: true, system_status: true }
                        },
                        portfolio: { followed_signals: JSON.parse(localStorage.getItem('followed_signals') || '[]') }
                    });
                    setIsAuthenticated(true);
                } catch (err) {
                    console.error('Token validation failed', err);
                    localStorage.removeItem('auth_token');
                    setIsAuthenticated(false);
                }
            }
            setIsLoading(false);
        };
        checkAuth();
    }, []);

    const login = async (email?: string, password?: string) => {
        setIsLoading(true);
        try {
            // For demo simplicity, we still support the mock bypass if no creds are passed, 
            // but if creds ARE passed, we use real API.
            if (email && password) {
                const data = await api.login(email, password);
                localStorage.setItem('auth_token', data.access_token);

                // Fetch profile immediately
                const user = data.user;
                // Map Backend Plan (FREE, PRO, OWNER) to Frontend (free, trader, pro)
                const backendPlan = user.plan?.toUpperCase() || 'FREE';
                let frontendPlan: 'free' | 'trader' | 'pro' = 'free';

                if (backendPlan === 'PRO') frontendPlan = 'trader';
                if (backendPlan === 'OWNER') frontendPlan = 'pro';

                setUserProfile({
                    user: {
                        ...user,
                        role: user.role,
                        subscription_status: frontendPlan,
                        onboarding_completed: false,
                        avatar_url: `https://ui-avatars.com/api/?name=${user.name}&background=10b981&color=fff`
                    },
                    preferences: {
                        favorite_tokens: ['eth', 'btc'],
                        default_timeframe: '30m',
                        notifications: { trade_updates: true, market_volatility: true, system_status: true }
                    },
                    portfolio: { followed_signals: [] }
                });
                setIsAuthenticated(true);
            } else {
                throw new Error("Credentials required");
            }
        } catch (err) {
            console.error('Login failed', err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        setIsAuthenticated(false);
        setUserProfile(null);
        localStorage.removeItem('auth_token');
    };

    const completeOnboarding = () => {
        if (userProfile) {
            const updatedProfile = {
                ...userProfile,
                user: {
                    ...userProfile.user,
                    onboarding_completed: true
                }
            };
            setUserProfile(updatedProfile);
            localStorage.setItem('onboarding_completed', 'true');
        }
    };

    const updateProfile = async (name: string, favorites: string[]) => {
        if (!userProfile) return;
        await new Promise(resolve => setTimeout(resolve, 500));
        setUserProfile({
            ...userProfile,
            user: { ...userProfile.user, name },
            preferences: { ...userProfile.preferences, favorite_tokens: favorites }
        });
    };

    const updateSignalNote = async (timestamp: string, token: string, note: string) => {
        console.log('Updating signal note:', { timestamp, token, note });
        await new Promise(resolve => setTimeout(resolve, 500));
    };

    const toggleFollow = (signal: any) => {
        if (!userProfile) return;

        const currentFollowed = userProfile.portfolio?.followed_signals || [];
        const isFollowed = currentFollowed.some(
            (s) => s.timestamp === signal.timestamp && s.token === signal.token
        );

        let updatedFollowed;
        if (isFollowed) {
            updatedFollowed = currentFollowed.filter(
                (s) => !(s.timestamp === signal.timestamp && s.token === signal.token)
            );
        } else {
            updatedFollowed = [
                ...currentFollowed,
                {
                    timestamp: signal.timestamp,
                    token: signal.token,
                    direction: signal.direction,
                    entry: signal.entry,
                    tp: signal.tp,
                    sl: signal.sl,
                    note: '',
                },
            ];
        }

        const updatedProfile = {
            ...userProfile,
            portfolio: {
                ...userProfile.portfolio,
                followed_signals: updatedFollowed,
            },
        };

        setUserProfile(updatedProfile);
        localStorage.setItem('followed_signals', JSON.stringify(updatedFollowed));
    };

    const upgradeSubscription = async (planId: 'free' | 'trader' | 'pro') => {
        setIsLoading(true);
        // Simulate API Payment Delay
        await new Promise(resolve => setTimeout(resolve, 2000));

        if (userProfile) {
            setUserProfile({
                ...userProfile,
                user: {
                    ...userProfile.user,
                    subscription_status: planId
                }
            });
            // Persist to local storage to survive refresh if needed
            localStorage.setItem('user_plan', planId);
        }
        setIsLoading(false);
    };

    return (
        <AuthContext.Provider
            value={{
                isAuthenticated,
                isLoading,
                userProfile,
                login,
                logout,
                completeOnboarding,
                updateProfile,
                updateSignalNote,
                toggleFollow,
                upgradeSubscription,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
