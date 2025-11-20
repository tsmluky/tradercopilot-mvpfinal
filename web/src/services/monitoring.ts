
import { UserProfile, FollowedSignal } from '../types';
import { authService } from './auth';
import { notificationService } from './notification';

// This service simulates the "Backend Worker" that monitors open trades.
// In a real app, this logic happens on the server, pushing updates via WebSockets.
// For the demo, we run a loop in the browser to update the "Open" signals in the user profile.

export const monitoringService = {
  start: (userProfile: UserProfile, updateProfileFn: (p: UserProfile) => void) => {
    console.log("Starting Active Intelligence Monitoring...");
    
    const intervalId = setInterval(async () => {
      const current = authService.getCurrentUser();
      if (!current) return;

      let hasUpdates = false;
      const updatedSignals: FollowedSignal[] = current.portfolio.followed_signals.map(sig => {
        // Only check OPEN signals
        if (sig.status !== 'OPEN' && !sig.status) {
           // Initialize status if missing
           return { ...sig, status: 'OPEN' as const };
        }
        
        if (sig.status === 'OPEN') {
          // 10% chance to resolve a trade every 10 seconds
          const roll = Math.random();
          if (roll < 0.10) {
             const isWin = Math.random() > 0.4; // 60% Win rate simulation
             const outcome: 'WIN' | 'LOSS' = isWin ? 'WIN' : 'LOSS';
             const pnl = isWin ? 1.5 : -1.0;
             
             // Trigger Notification
             if (current.preferences.notifications.trade_updates) {
                 notificationService.notify(
                    isWin ? 'Target Hit 🎯' : 'Stop Loss Hit 🛑',
                    `${sig.token} ${sig.direction.toUpperCase()} closed. PnL: ${pnl > 0 ? '+' : ''}${pnl}R`,
                    isWin ? 'success' : 'error'
                 );
             }
             
             hasUpdates = true;
             return { ...sig, status: outcome, final_pnl: pnl };
          }
        }
        return sig;
      });

      // Random Market Alert (5% chance)
      if (current.preferences.notifications.market_volatility && Math.random() < 0.05) {
          const tokens = ['ETH', 'BTC', 'SOL'];
          const t = tokens[Math.floor(Math.random() * tokens.length)];
          notificationService.notify(
              'Market Alert ⚠️',
              `${t} volatility detected. Price moving fast.`,
              'warning'
          );
      }

      if (hasUpdates) {
        const updatedProfile: UserProfile = {
            ...current,
            portfolio: { ...current.portfolio, followed_signals: updatedSignals }
        };
        // Persist to local storage
        localStorage.setItem('tradercopilot_user', JSON.stringify(updatedProfile));
        // Update React Context
        updateProfileFn(updatedProfile);
      }

    }, 10000); // Check every 10 seconds

    return () => clearInterval(intervalId);
  }
};
