import bcrypt from 'bcryptjs'
import { db } from '@/lib/db'
import { createSession } from '@/lib/auth'

export const runtime = 'nodejs'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : ''
    const password = typeof body.password === 'string' ? body.password : ''
    const user = await db.user.findUnique({ where: { email } })
    if (!user || !(await bcrypt.compare(password, user.passwordHash))) return Response.json({ error: 'Email or password is incorrect.' }, { status: 401 })
    await createSession(user.id)
    return Response.json({ ok: true, user: { name: user.name, email: user.email } })
  } catch (error) {
    console.error('Login failed:', error)
    return Response.json({ error: 'Could not sign you in. Please try again.' }, { status: 500 })
  }
}
