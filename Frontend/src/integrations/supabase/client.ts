// Centralized Supabase client using environment-based configuration
import { createClient } from '@supabase/supabase-js';
import type { Database } from './types';
import config from '@/lib/config';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || config.supabase.url;
const SUPABASE_PUBLISHABLE_KEY =
  import.meta.env.VITE_SUPABASE_ANON_KEY ||
  (import.meta.env as any).VITE_SUPABASE_PUBLISHABLE_KEY ||
  config.supabase.anonKey;

if (!SUPABASE_URL || !SUPABASE_PUBLISHABLE_KEY) {
  // eslint-disable-next-line no-console
  console.warn('[Supabase] Missing configuration. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.');
}

// Import the supabase client like this:
// import { supabase } from "@/integrations/supabase/client";

export const supabase = createClient<Database>(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
  auth: {
    storage: localStorage,
    persistSession: true,
    autoRefreshToken: true,
  }
});