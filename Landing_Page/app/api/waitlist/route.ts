import { db } from '@/lib/db'
import { notifyAdmin } from '@/lib/email'

export const runtime = 'nodejs'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const name = typeof body.name === 'string' ? body.name.trim() : ''
    const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : ''

    if (name.length < 2 || name.length > 100) return Response.json({ error: 'Please enter your name.' }, { status: 400 })
    if (!/^\S+@\S+\.\S+$/.test(email)) return Response.json({ error: 'Please enter a valid email.' }, { status: 400 })

    const entry = await db.waitlistEntry.upsert({
      where: { email },
      update: { name, source: 'landing-page' },
      create: { name, email, source: 'landing-page' },
    })
    await notifyAdmin({ name: entry.name, email: entry.email })
    return Response.json({ ok: true, message: 'You are on the list.' })
  } catch (error) {
    console.error('Waitlist request failed:', error)
    return Response.json({ error: 'We could not save that yet. Please try again.' }, { status: 500 })
  }
}
