import { getSessionUserId } from '@/lib/auth'
import { db } from '@/lib/db'

export const runtime = 'nodejs'

export async function GET() {
  const userId = await getSessionUserId()
  if (!userId) return Response.json({ user: null })
  const user = await db.user.findUnique({ where: { id: userId }, select: { name: true, email: true } })
  return Response.json({ user: user || null })
}
