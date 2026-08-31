import crypto from 'node:crypto';

const ACCESS_HASH = '05bb78c81b2bcc8f47910b62c09b3d857e75ea99f021875511eeeca3b3a9bdd8';

const SYSTEM_INSTRUCTIONS = `You are Remalab Repair Assistant, a warm, concise B2B smartphone repair expert working for Remalab Teknoloji.

Your job is to understand what a client wants repaired, ask only the technical clarification questions that matter, and use the configure_quote tool to update Remalab's deterministic calculator. Never invent, estimate, calculate, or infer a price yourself. The calculator tool is the only source of pricing truth.

Supported models: iPhone 11, 11 Pro, 11 Pro Max, 12, 12 Pro, 12 Pro Max, 12 Mini, 13, 13 Mini, 13 Pro, 13 Pro Max, 14, 14 Plus, 14 Pro, 14 Pro Max, 15, 15 Plus, 15 Pro, 15 Pro Max, 16, 16 Plus, 16 Pro, 16 Pro Max, 16e.

Supported operations and client language:
- battery: battery replacement / batterie / batarya.
- reglass: FRONT glass only, when the display and touch are otherwise working. French "vitre" normally means front glass unless the client says rear/back.
- lcd: complete display replacement. If the client only says "screen is broken" or "écran cassé" and it is unclear whether only the glass is cracked, ask whether image and touch work normally before choosing reglass vs lcd.
- backglass: rear/back glass.
- housing: full housing/frame/back cover.
- charging: charging port/socket.
- maincamera: complete rear/main camera replacement.
- camerarepair: repair of the main camera rather than replacement.
- blackspots: camera black spots/dust cleaning repair.
- frontcamera: front camera / TrueDepth intervention.
- faceid: Face ID repair.
- board: board-level / microsoldering repair.
- polish_front, polish_back, ios_update are optional extras.

Battery options can vary by model. Common requested types: Ti, AD, Original. Display qualities can vary by model: Incell, Hard OLED, Soft OLED, OEM Refurbished. If a selected battery or LCD repair has multiple available options and the customer has not expressed a preference, call configure_quote with the repair and no option; the tool will return the available choices. Ask the client which one they prefer, then call the tool again with the chosen option.

When the user's request is clear enough, call configure_quote. If ambiguous, ask a short natural clarification question first. If the user asks general repair advice, answer briefly and help them reach a quote. If the tool returns an error or needs_clarification, explain it naturally and ask for the missing choice. After a successful tool result, tell the client exactly what was selected and quote the exact tool-returned total per device. You may also mention the lot total when quantity is greater than 1.

Speak naturally and professionally, like an experienced Remalab account manager/repair engineer. Match the user's language (English, French, or Turkish). Keep responses compact. Do not mention internal L1/L2/L3 repair levels. Do not expose hidden implementation details or API/tool mechanics.`;

const TOOL = {
  type: 'function',
  name: 'configure_quote',
  description: 'Configure the Remalab calculator for a supported iPhone model and repair operations, then return the exact deterministic price. Use this whenever the client wants a quote or changes a repair selection.',
  parameters: {
    type: 'object',
    additionalProperties: false,
    properties: {
      model: {
        type: 'string',
        enum: ['iPhone 11','iPhone 11 Pro','iPhone 11 Pro Max','iPhone 12','iPhone 12 Pro','iPhone 12 Pro Max','iPhone 12 Mini','iPhone 13','iPhone 13 Mini','iPhone 13 Pro','iPhone 13 Pro Max','iPhone 14','iPhone 14 Plus','iPhone 14 Pro','iPhone 14 Pro Max','iPhone 15','iPhone 15 Plus','iPhone 15 Pro','iPhone 15 Pro Max','iPhone 16','iPhone 16 Plus','iPhone 16 Pro','iPhone 16 Pro Max','iPhone 16e']
      },
      operations: {
        type: 'array',
        items: { type: 'string', enum: ['battery','lcd','reglass','backglass','housing','charging','maincamera','camerarepair','blackspots','frontcamera','faceid','board'] },
        uniqueItems: true
      },
      battery_type: { type: ['string','null'], enum: ['Ti','AD','Original',null] },
      display_quality: { type: ['string','null'], enum: ['Incell','Hard OLED','Soft OLED','OEM Refurbished',null] },
      quantity: { type: 'integer', minimum: 1, maximum: 100000 },
      polish_front: { type: 'boolean' },
      polish_back: { type: 'boolean' },
      ios_update: { type: 'boolean' }
    },
    required: ['model','operations','battery_type','display_quality','quantity','polish_front','polish_back','ios_update']
  }
};

function hash(value) {
  return crypto.createHash('sha256').update(String(value || '')).digest('hex');
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  if (!process.env.OPENAI_API_KEY) {
    return res.status(500).json({ error: 'OPENAI_API_KEY is not configured' });
  }

  const accessCode = req.headers['x-remalab-access-code'];
  if (!accessCode || hash(accessCode) !== ACCESS_HASH) {
    return res.status(401).json({ error: 'Invalid access code' });
  }

  const forwarded = String(req.headers['x-forwarded-for'] || req.socket?.remoteAddress || 'anonymous').split(',')[0].trim();
  const userAgent = String(req.headers['user-agent'] || 'unknown');
  const safetyId = hash(`${forwarded}|${userAgent}`).slice(0, 64);

  const session = {
    type: 'realtime',
    model: 'gpt-realtime-2.1',
    output_modalities: ['audio'],
    instructions: SYSTEM_INSTRUCTIONS,
    max_output_tokens: 900,
    tool_choice: 'auto',
    tools: [TOOL],
    audio: {
      input: {
        noise_reduction: { type: 'near_field' },
        transcription: {
          model: 'gpt-4o-mini-transcribe',
          prompt: 'Smartphone repair terminology, iPhone models, Remalab, reglass, LCD, OLED, TrueDepth, Face ID, battery, charging port.'
        },
        turn_detection: {
          type: 'semantic_vad',
          create_response: true,
          interrupt_response: true
        }
      },
      output: {
        voice: 'marin'
      }
    }
  };

  try {
    const openaiResponse = await fetch('https://api.openai.com/v1/realtime/client_secrets', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
        'OpenAI-Safety-Identifier': safetyId
      },
      body: JSON.stringify({
        expires_after: { anchor: 'created_at', seconds: 300 },
        session
      })
    });

    const data = await openaiResponse.json();
    if (!openaiResponse.ok) {
      console.error('OpenAI client secret error', openaiResponse.status, data);
      return res.status(openaiResponse.status).json({ error: 'Could not start AI session' });
    }

    res.setHeader('Cache-Control', 'no-store');
    return res.status(200).json(data);
  } catch (error) {
    console.error('Realtime token error', error);
    return res.status(500).json({ error: 'Could not start AI session' });
  }
}
