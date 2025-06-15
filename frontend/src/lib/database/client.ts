/**
 * NEO API Client
 * 
 * Replaces Supabase client with custom API client for NEO backend.
 */

class NEOClient {
  private baseUrl: string;
  private accessToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.loadTokenFromStorage();
  }

  private loadTokenFromStorage() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('neo_access_token');
    }
  }

  private saveTokenToStorage(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('neo_access_token', token);
      this.accessToken = token;
    }
  }

  private removeTokenFromStorage() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('neo_access_token');
      localStorage.removeItem('neo_refresh_token');
      localStorage.removeItem('neo_session_token');
      this.accessToken = null;
    }
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired, try to refresh
        await this.refreshToken();
        // Retry the request
        return this.makeRequest(endpoint, options);
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Authentication methods
  async signUp(email: string, password: string, fullName?: string) {
    const response = await this.makeRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    });

    this.saveTokenToStorage(response.access_token);
    if (typeof window !== 'undefined') {
      localStorage.setItem('neo_refresh_token', response.refresh_token);
      localStorage.setItem('neo_session_token', response.session_token);
    }

    return response;
  }

  async signIn(email: string, password: string) {
    const response = await this.makeRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
      }),
    });

    this.saveTokenToStorage(response.access_token);
    if (typeof window !== 'undefined') {
      localStorage.setItem('neo_refresh_token', response.refresh_token);
      localStorage.setItem('neo_session_token', response.session_token);
    }

    return response;
  }

  async signOut() {
    try {
      await this.makeRequest('/auth/logout', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.removeTokenFromStorage();
    }
  }

  async refreshToken() {
    if (typeof window === 'undefined') return;

    const refreshToken = localStorage.getItem('neo_refresh_token');
    if (!refreshToken) {
      this.removeTokenFromStorage();
      throw new Error('No refresh token available');
    }

    try {
      const response = await this.makeRequest('/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({
          refresh_token: refreshToken,
        }),
      });

      this.saveTokenToStorage(response.access_token);
      return response;
    } catch (error) {
      this.removeTokenFromStorage();
      throw error;
    }
  }

  async getUser() {
    return this.makeRequest('/auth/me');
  }

  // Database-like methods for compatibility
  from(table: string) {
    return {
      select: (columns = '*') => ({
        eq: (column: string, value: any) => this.makeRequest(`/api/${table}?${column}=${value}`),
        order: (column: string, options?: { ascending?: boolean }) => ({
          limit: (count: number) => this.makeRequest(`/api/${table}?order=${column}&limit=${count}`),
        }),
      }),
      insert: (data: any) => this.makeRequest(`/api/${table}`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
      update: (data: any) => ({
        eq: (column: string, value: any) => this.makeRequest(`/api/${table}?${column}=${value}`, {
          method: 'PUT',
          body: JSON.stringify(data),
        }),
      }),
      delete: () => ({
        eq: (column: string, value: any) => this.makeRequest(`/api/${table}?${column}=${value}`, {
          method: 'DELETE',
        }),
      }),
    };
  }

  // Storage methods
  storage = {
    from: (bucket: string) => ({
      upload: async (path: string, file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('path', path);

        const response = await fetch(`${this.baseUrl}/api/storage/${bucket}/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.accessToken}`,
          },
          body: formData,
        });

        return response.json();
      },
      getPublicUrl: (path: string) => ({
        data: {
          publicUrl: `${this.baseUrl}/api/storage/${bucket}/${path}`,
        },
      }),
    }),
  };

  // Real-time subscriptions (placeholder)
  channel(topic: string) {
    return {
      on: (event: string, callback: Function) => {
        // TODO: Implement WebSocket subscriptions
        console.log(`Subscribing to ${topic}:${event}`);
        return this;
      },
      subscribe: () => {
        console.log('Subscription started');
        return Promise.resolve();
      },
    };
  }
}

export const createClient = () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return new NEOClient(apiUrl);
};
