'use server';
import { cookies } from 'next/headers';

// Mock database client for local development
export const createClient = async () => {
  const cookieStore = await cookies();
  
  // Return a mock client that mimics Supabase interface
  return {
    auth: {
      getUser: async () => ({ data: { user: null }, error: null }),
      signInWithPassword: async () => ({ data: null, error: null }),
      signUp: async () => ({ data: null, error: null }),
      signOut: async () => ({ error: null }),
    },
    from: (table: string) => ({
      select: () => ({ data: [], error: null }),
      insert: () => ({ data: null, error: null }),
      update: () => ({ data: null, error: null }),
      delete: () => ({ data: null, error: null }),
    }),
  };
};
