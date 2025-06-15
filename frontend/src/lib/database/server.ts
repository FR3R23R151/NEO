'use server';
import { createServerClient, type CookieOptions } from '@database/ssr';
import { cookies } from 'next/headers';

export const createClient = async () => {
  const cookieStore = await cookies();
  let databaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const databaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

  // Ensure the URL is in the proper format with http/https protocol
  if (databaseUrl && !databaseUrl.startsWith('http')) {
    // If it's just a hostname without protocol, add http://
    databaseUrl = `http://${databaseUrl}`;
  }

  // console.log('[SERVER] Supabase URL:', databaseUrl);
  // console.log('[SERVER] Supabase Anon Key:', databaseAnonKey);

  return createServerClient(databaseUrl, databaseAnonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set({ name, value, ...options }),
          );
        } catch (error) {
          // The `set` method was called from a Server Component.
          // This can be ignored if you have middleware refreshing
          // user sessions.
        }
      },
    },
  });
};
