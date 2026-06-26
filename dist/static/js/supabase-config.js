// Supabase Client Initialization Configuration
// Replace the placeholders below with your actual Supabase Project API credentials.
const SUPABASE_URL = "https://saguwhmcssugcujapnwi.supabase.co";
const SUPABASE_ANON_KEY = "sb_publishable_fn8zD_2iufj4kAHlia5dOQ_e8IQl_lX";

// Initialize the Supabase Client
// Note: Ensure the Supabase CDN script is loaded before this script:
// <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
let supabaseClient = null;

if (typeof supabase !== 'undefined') {
  if (SUPABASE_URL !== "YOUR_SUPABASE_URL" && SUPABASE_ANON_KEY !== "YOUR_SUPABASE_ANON_KEY") {
    supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      auth: {
        storage: window.sessionStorage,
        persistSession: true
      }
    });
    console.log("Supabase Client initialized successfully with sessionStorage.");
  } else {
    console.warn("Supabase credentials not configured yet. Please update static/js/supabase-config.js with your project credentials.");
  }
} else {
  console.error("Supabase library not loaded. Make sure the Supabase CDN script is included.");
}
