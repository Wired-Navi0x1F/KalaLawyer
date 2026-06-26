// ============================================================================
// Supabase Edge Function: send-enquiry
// ============================================================================
// Handles secure backend email routing for contact form leads using Resend.
// ============================================================================

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    if (!RESEND_API_KEY) {
      throw new Error('RESEND_API_KEY environment variable is not set in Supabase Secrets')
    }

    const { name, company, email, phone, referred_by, practice_area, message } = await req.json()

    // 1. Send lead details to advocates
    const adminEmailRes = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from: 'The Kala Lawyers Notifications <office@thekalalawyers.com>',
        to: ['advocateanujkalajodhpur@gmail.com', 'kalalawyer@gmail.com'],
        subject: `New Lead Inquiry: ${name} (${practice_area})`,
        html: `
          <div style="font-family: sans-serif; max-width: 600px; color: #2d221c;">
            <h2 style="color: #b38a66; border-bottom: 1px solid #e5dacd; padding-bottom: 0.5rem;">New Contact Form Submission</h2>
            <p>A new evaluation request has been submitted from the website:</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">
              <tr>
                <td style="padding: 0.5rem; font-weight: bold; border-bottom: 1px solid #f2ebe4;">Name:</td>
                <td style="padding: 0.5rem; border-bottom: 1px solid #f2ebe4;">${name}</td>
              </tr>
              <tr>
                <td style="padding: 0.5rem; font-weight: bold; border-bottom: 1px solid #f2ebe4;">Company:</td>
                <td style="padding: 0.5rem; border-bottom: 1px solid #f2ebe4;">${company || 'N/A'}</td>
              </tr>
              <tr>
                <td style="padding: 0.5rem; font-weight: bold; border-bottom: 1px solid #f2ebe4;">Email:</td>
                <td style="padding: 0.5rem; border-bottom: 1px solid #f2ebe4;"><a href="mailto:${email}">${email}</a></td>
              </tr>
              <tr>
                <td style="padding: 0.5rem; font-weight: bold; border-bottom: 1px solid #f2ebe4;">Phone:</td>
                <td style="padding: 0.5rem; border-bottom: 1px solid #f2ebe4;"><a href="tel:${phone}">${phone}</a></td>
              </tr>
              <tr>
                <td style="padding: 0.5rem; font-weight: bold; border-bottom: 1px solid #f2ebe4;">Referred By:</td>
                <td style="padding: 0.5rem; border-bottom: 1px solid #f2ebe4;">${referred_by}</td>
              </tr>
              <tr>
                <td style="padding: 0.5rem; font-weight: bold; border-bottom: 1px solid #f2ebe4;">Practice Area:</td>
                <td style="padding: 0.5rem; border-bottom: 1px solid #f2ebe4; color: #b38a66; font-weight: bold;">${practice_area}</td>
              </tr>
            </table>
            <h4 style="margin-top: 1.5rem; margin-bottom: 0.5rem;">Message Detail:</h4>
            <div style="background-color: #fcfbfa; border: 1px solid #e5dacd; padding: 1rem; border-radius: 6px; font-style: italic;">
              ${message.replace(/\n/g, '<br/>')}
            </div>
            <p style="margin-top: 2rem; font-size: 0.85rem; color: #6b5a50; border-top: 1px solid #e5dacd; padding-top: 1rem;">
              This notification was generated automatically by your website's Supabase Edge Function.
            </p>
          </div>
        `,
      }),
    })

    const adminEmailData = await adminEmailRes.json()
    if (!adminEmailRes.ok) {
      throw new Error(`Failed to send email to admin: ${JSON.stringify(adminEmailData)}`)
    }

    // 2. Send receipt copy to the client
    const clientEmailRes = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from: 'The Kala Lawyers Office <office@thekalalawyers.com>',
        to: [email],
        subject: 'Enquiry Received - The Kala Lawyers',
        html: `
          <div style="font-family: sans-serif; max-width: 600px; color: #2d221c; line-height: 1.6;">
            <h3 style="color: #b38a66;">Dear ${name},</h3>
            <p>Thank you for reaching out to **The Kala Lawyers**. We have successfully received your case evaluation enquiry.</p>
            <p>Our legal team will review your query details and get in touch with you shortly.</p>
            <hr style="border: 0; border-top: 1px solid #e5dacd; margin: 1.5rem 0;" />
            <h4 style="color: #2d221c; margin-bottom: 0.5rem;">Here is a copy of the details you submitted:</h4>
            <p><strong>Area of concern:</strong> ${practice_area}</p>
            <p><strong>Your Message:</strong></p>
            <div style="background-color: #fcfbfa; border: 1px solid #e5dacd; padding: 1rem; border-radius: 6px; font-style: italic; color: #6b5a50;">
              ${message.replace(/\n/g, '<br/>')}
            </div>
            <hr style="border: 0; border-top: 1px solid #e5dacd; margin: 1.5rem 0;" />
            <p>If you have any urgent matters, please feel free to call us at **+91 98281 17145** or reply directly to this email.</p>
            <br />
            <p>Best regards,<br/><strong>Office Administration</strong><br/>The Kala Lawyers</p>
          </div>
        `,
      }),
    })

    const clientEmailData = await clientEmailRes.json()
    if (!clientEmailRes.ok) {
      console.warn(`Failed to send confirmation receipt to client: ${JSON.stringify(clientEmailData)}`)
    }

    return new Response(JSON.stringify({ success: true }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200,
    })

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400,
    })
  }
})
