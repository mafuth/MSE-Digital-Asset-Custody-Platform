export interface MetalPrice {
	code: string;
	name: string;
	price_kg: number;
	updated_at: string;
}

export interface UserCreate {
	name: string;
	email: string;
	password: string;
}

export interface UserLogin {
	email: string;
	password: string;
}

export interface Token {
	access_token: string;
	token_type: string;
}

const BASE_URL = '/api/v1';

export async function getMarketPrices(): Promise<MetalPrice[]> {
	try {
		const response = await fetch(`${BASE_URL}/public/prices`);
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		return await response.json();
	} catch (error) {
		console.error('Failed to fetch market prices:', error);
		return [];
	}
}

export async function login(data: UserLogin): Promise<Token> {
	const response = await fetch(`${BASE_URL}/auth/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(data)
	});
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Login failed');
	}
	return await response.json();
}

export async function register(data: UserCreate): Promise<any> {
	const response = await fetch(`${BASE_URL}/auth/register`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(data)
	});
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Registration failed');
	}
	return await response.json();
}

export async function getMe(token: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/accounts/me`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok) {
		throw new Error('Failed to fetch user profile');
	}
	return await response.json();
}

export async function requestPasswordReset(email: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/auth/password-reset-request`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ email })
	});
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Reset request failed');
	}
	return await response.json();
}

export async function resetPasswordConfirm(token: string, new_password: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/auth/password-reset-confirm`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ token, new_password })
	});
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Password reset failed');
	}
	return await response.json();
}

export async function verifyOtp(otp: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/auth/verify-otp`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ otp })
	});
	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Verification failed');
	}
	return await response.json();
}

export async function getPortfolio(token: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/accounts/portfolio`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok) {
		throw new Error('Failed to fetch portfolio');
	}
	return await response.json();
}

export async function getTransactionHistory(token: string, startDate?: string, endDate?: string): Promise<any[]> {
	const url = new URL(`${BASE_URL}/transactions/history`, window.location.origin);
	if (startDate) url.searchParams.append('start_date', startDate);
	if (endDate) url.searchParams.append('end_date', endDate);
	
	const response = await fetch(url.toString(), {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok) {
		throw new Error('Failed to fetch transactions');
	}
	return await response.json();
}

export async function getMetals(token: string): Promise<any[]> {
	const response = await fetch(`${BASE_URL}/metals/`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok) {
		throw new Error('Failed to fetch metals');
	}
	return await response.json();
}

export async function getMetalHistory(token: string, metalId: string): Promise<any[]> {
	const response = await fetch(`${BASE_URL}/metals/${metalId}/history`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok) {
		throw new Error('Failed to fetch metal history');
	}
	return await response.json();
}

export async function buyStorage(token: string, planId: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/accounts/buy-storage?plan_id=${planId}`, {
		method: 'POST',
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok) {
		throw new Error('Failed to purchase storage');
	}
	return await response.json();
}

export async function getVaults(token: string): Promise<any[]> {
	const response = await fetch(`${BASE_URL}/vaults/`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok) {
		throw new Error('Failed to fetch vaults');
	}
	return await response.json();
}

export async function depositMetal(token: string, data: {
	metal_id: string;
	quantity_kg: number;
	storage_type: string;
	vault_id: string;
	serial_number?: string;
}): Promise<any> {
	const response = await fetch(`${BASE_URL}/transactions/deposit`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) {
		const err = await response.json();
		throw new Error(err.detail || 'Failed to deposit metal');
	}
	return await response.json();
}

export async function withdrawMetal(token: string, data: {
	metal_id: string;
	quantity_kg: number;
	storage_type: string;
	vault_id: string;
	serial_number?: string;
}): Promise<any> {
	const response = await fetch(`${BASE_URL}/transactions/withdraw`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) {
		const err = await response.json();
		throw new Error(err.detail || 'Failed to withdraw metal');
	}
	return await response.json();
}

// Admin API functions
export async function getAdminAccounts(token: string): Promise<any[]> {
	const response = await fetch(`${BASE_URL}/admin/accounts`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok) {
		throw new Error('Failed to fetch admin accounts');
	}
	return await response.json();
}

export async function updateAdminAccount(token: string, accountId: string, data: any): Promise<any> {
	const response = await fetch(`${BASE_URL}/admin/accounts/${accountId}`, {
		method: 'PATCH',
		headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) {
		const err = await response.json();
		throw new Error(err.detail || 'Failed to update account');
	}
	return await response.json();
}

export async function getAdminAccountPortfolio(token: string, accountId: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/admin/accounts/${accountId}/portfolio`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!response.ok) {
		throw new Error('Failed to fetch account portfolio');
	}
	return await response.json();
}

export async function addMetal(token: string, data: any): Promise<any> {
	const response = await fetch(`${BASE_URL}/admin/metals`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(data)
	});
	if (!response.ok) {
		const err = await response.json();
		throw new Error(err.detail || 'Failed to add metal');
	}
	return await response.json();
}
