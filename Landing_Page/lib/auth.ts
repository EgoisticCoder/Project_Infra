import { jwtVerify, SignJWT } from 'jose'
import { cookies } from 'next/headers'

export const SESSION_COOKIE = 'infra_session'

function secret() {
  const value = process.env.AUTH_SECRET
  if (!value && process.env.NODE_ENV === 'production') throw new Error('AUTH_SECRET is required in production')
  return new TextEncoder().encode(value || 'local-development-secret-change-me')
}

export async function createSession(userId: string) {
  const token = await new SignJWT({ userId })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('30d')
    .sign(secret())

  const jar = await cookies()
  jar.set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production',
    path: '/',
    maxAge: 60 * 60 * 24 * 30,
  })
}

export async function getSessionUserId() {
  const token = (await cookies()).get(SESSION_COOKIE)?.value
  if (!token) return null
  try {
    const { payload } = await jwtVerify(token, secret())
    return typeof payload.userId === 'string' ? payload.userId : null
  } catch {
    return null
  }
}

export async function clearSession() {
  const jar = await cookies()
  jar.delete(SESSION_COOKIE)
}
