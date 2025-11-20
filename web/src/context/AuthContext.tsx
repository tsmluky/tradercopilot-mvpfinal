import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile } from '../types';

interface AuthContextType {
    isAuthenticated: boolean;
    isLoading: boolean;
    userProfile: UserProfile | null;
    login: () => Promise<void>;
    logout: () => void;
    completeOnboarding: () => void;
    updateProfile: (name: string, favorites: string[]) => Promise<void>;
    updateSignalNote: (timestamp: string, token: string, note: string) => Promise<void>;
    toggleFollow: (signal: any) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

    useEffect(() => {
        const checkAuth = async () => {
            await new Promise(resolve => setTimeout(resolve, 500));
            const token = localStorage.getItem('auth_token');
            const savedSignals = localStorage.getItem('followed_signals');

            if (token || true) {
                setIsAuthenticated(true);
                setUserProfile({
                    user: {
                        id: 'demo-user',
                        name: 'Commander',
                        email: 'demo@tradercopilot.com',
                        role: 'user',
                        subscription_status: 'active',
                        onboarding_completed: localStorage.getItem('onboarding_completed') === 'true',
                        avatar_url: 'https://ui-avatars.com/api/?name=Commander&background=10b981&color=fff'
                    },
                    preferences: {
                        favorite_tokens: ['eth', 'btc', 'sol'],
                        default_timeframe: '30m',
                        notifications: {
                            trade_updates: true,
                            market_volatility: true,
                            system_status: true
                        }
                    },
                    portfolio: {
                        followed_signals: savedSignals ? JSON.parse(savedSignals) : []
                    }
                });
            }
            setIsLoading(false);
        };

        checkAuth();
    }, []);

    const login = async () => {
        setIsLoading(true);
        await new Promise(resolve => setTimeout(resolve, 1000));
        setIsAuthenticated(true);
        setUserProfile({
            user: {
                id: 'demo-user',
                name: 'Commander',
                email: 'demo@tradercopilot.com',
                role: 'user',
                subscription_status: 'active',
                onboarding_completed: false,
                avatar_url: 'https://ui-avatars.com/api/?name=Commander&background=10b981&color=fff'
            },
            preferences: {
                favorite_tokens: ['eth', 'btc'],
                default_timeframe: '30m',
                notifications: {
                    trade_updates: true,
                    market_volatility: true,
                    system_status: true
                }
            },
            portfolio: {
                followed_signals: []
            }
        });
        localStorage.setItem('auth_token', 'demo-token');
        setIsLoading(false);
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
