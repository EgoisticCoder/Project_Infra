import bcrypt from 'bcryptjs'
import { db } from '@/lib/db'
import { createSession } from '@/lib/auth'
import { notifyAdmin } from '@/lib/email'

export const runtime = 'nodejs'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const name = typeof body.name === 'string' ? body.name.trim() : ''
    const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : ''
    const password = typeof body.password === 'string' ? body.password : ''
    if (name.length < 2 || name.length > 100) return Response.json({ error: 'Name must be at least 2 characters.' }, { status: 400 })
    if (!/^\S+@\S+\.\S+$/.test(email)) return Response.json({ error: 'Please enter a valid email.' }, { status: 400 })
    if (password.length < 8) return Response.json({ error: 'Use a password with at least 8 characters.' }, { status: 400 })
    const existing = await db.user.findUnique({ where: { email } })
    if (existing) return Response.json({ error: 'An account with that email already exists.' }, { status: 409 })
    const user = await db.user.create({ data: { name, email, passwordHash: await bcrypt.hash(password, 12) } })
    await db.waitlistEntry.upsert({ where: { email }, update: { name }, create: { name, email, source: 'account-signup' } })
    await notifyAdmin({ name, email, source: 'account signup' })
    await createSession(user.id)
    return Response.json({ ok: true, user: { name: user.name, email: user.email } })
  } catch (error) {
    console.error('Signup failed:', error)
    return Response.json({ error: 'Could not create your account. Please try again.' }, { status: 500 })
  }
}
