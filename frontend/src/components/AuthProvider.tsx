'use client';

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from 'react';
import { createClient } from '@/lib/database/client';
import { User, Session } from '@database/database-js';
import { SupabaseClient } from '@database/database-js';

type AuthContextType = {
  database: SupabaseClient;
  session: Session | null;
  user: User | null;
  isLoading: boolean;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const database = createClient();
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getInitialSession = async () => {
      const {
        data: { session: currentSession },
      } = await database.auth.getSession();
      setSession(currentSession);
      setUser(currentSession?.user ?? null);
      setIsLoading(false);
    };

    getInitialSession();

    const { data: authListener } = database.auth.onAuthStateChange(
      (_event, newSession) => {
        setSession(newSession);
        setUser(newSession?.user ?? null);
        // No need to set loading state here as initial load is done
        // and subsequent changes shouldn't show a loading state for the whole app
        if (isLoading) setIsLoading(false);
      },
    );

    return () => {
      authListener?.subscription.unsubscribe();
    };
  }, [database, isLoading]); // Added isLoading to dependencies to ensure it runs once after initial load completes

  const signOut = async () => {
    await database.auth.signOut();
    // State updates will be handled by onAuthStateChange
  };

  const value = {
    database,
    session,
    user,
    isLoading,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
