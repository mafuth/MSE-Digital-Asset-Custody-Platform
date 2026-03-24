import { browser } from '$app/environment';
import { getMe } from './api';

class AuthState {
	token = $state<string | null>(browser ? localStorage.getItem('auth_token') : null);
	user = $state<any>(null);
	initialized = $state(false);

	async init() {
		if (this.token) {
			try {
				this.user = await getMe(this.token);
			} catch (e) {
				console.error('Failed to restore session:', e);
				this.logout();
			}
		}
		this.initialized = true;
	}

	setToken(token: string) {
		this.token = token;
		if (browser) {
			localStorage.setItem('auth_token', token);
		}
	}

	logout() {
		this.token = null;
		this.user = null;
		if (browser) {
			localStorage.removeItem('auth_token');
		}
	}
}

export const auth = new AuthState();
