
import { ToastAlert } from '../types';

type Listener = (toast: ToastAlert) => void;

class NotificationService {
  private listeners: Listener[] = [];

  subscribe(listener: Listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify(title: string, message: string, type: ToastAlert['type'] = 'info') {
    const toast: ToastAlert = {
      id: Date.now().toString(),
      title,
      message,
      type
    };
    this.listeners.forEach(l => l(toast));
  }
}

export const notificationService = new NotificationService();
