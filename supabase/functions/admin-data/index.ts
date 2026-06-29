import { createClient } from "npm:@supabase/supabase-js@2";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY");
const SUPABASE_SERVICE_ROLE_KEY =
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") || Deno.env.get("SUPABASE_SERVICE_KEY");

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

  try {
    if (!SUPABASE_URL || !SUPABASE_ANON_KEY || !SUPABASE_SERVICE_ROLE_KEY) {
      throw new Error("Supabase function secrets are not configured.");
    }

    const authHeader = req.headers.get("Authorization") || "";
    if (!authHeader.startsWith("Bearer ")) {
      return jsonResponse({ success: false, error: "Unauthorized" }, 401);
    }

    const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      global: { headers: { Authorization: authHeader } },
    });
    const { data: userData, error: userError } = await userClient.auth.getUser(
      authHeader.replace("Bearer ", ""),
    );
    if (userError || !userData?.user) {
      return jsonResponse({ success: false, error: "Unauthorized" }, 401);
    }

    const adminClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
    const { action, table, id, payload } = await req.json();

    if (!["case_wins", "diary_records", "practice_areas"].includes(table)) {
      return jsonResponse({ success: false, error: "Unsupported table" }, 400);
    }

    if (action === "insert") {
      const rows = Array.isArray(payload) ? payload : [payload];
      const { data, error } = await adminClient.from(table).insert(rows).select();
      if (error) throw error;
      return jsonResponse({ success: true, data });
    }

    if (action === "update") {
      if (!id) {
        return jsonResponse({ success: false, error: "id is required" }, 400);
      }
      const { data, error } = await adminClient
        .from(table)
        .update(payload)
        .eq("id", id)
        .select();
      if (error) throw error;
      return jsonResponse({ success: true, data });
    }

    if (action === "delete") {
      if (!id) {
        return jsonResponse({ success: false, error: "id is required" }, 400);
      }
      const { data, error } = await adminClient.from(table).delete().eq("id", id).select();
      if (error) throw error;
      return jsonResponse({ success: true, data });
    }

    return jsonResponse({ success: false, error: "Unsupported action" }, 400);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return jsonResponse({ success: false, error: message }, 400);
  }
});
