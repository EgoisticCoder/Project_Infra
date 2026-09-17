import nodemailer from 'nodemailer'

const adminEmail = process.env.ADMIN_EMAIL || 'admin.team.infra@gmail.com'

function escapeHtml(value: string) {
  return value.replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character] || character)
}

export async function notifyAdmin({ name, email, source = 'Infra landing page' }: { name: string; email: string; source?: string }) {
  const smtpUser = process.env.SMTP_USER || adminEmail
  const smtpPassword = process.env.SMTP_APP_PASSWORD
  if (!smtpPassword) {
    console.warn('Waitlist saved, but Gmail SMTP is not configured. Set SMTP_APP_PASSWORD.')
    return false
  }

  const safeName = escapeHtml(name)
  const safeEmail = escapeHtml(email)
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: { user: smtpUser, pass: smtpPassword },
  })

  await transporter.sendMail({
    from: `Infra / Forma <${smtpUser}>`,
    to: adminEmail,
    replyTo: email,
    subject: `New Forma early-access request from ${name}`,
    html: `<div style="font-family:Arial,sans-serif;line-height:1.6"><h2>New Forma early-access request</h2><p><strong>${safeName}</strong> (${safeEmail}) joined the list.</p><p>Source: ${escapeHtml(source)}</p><p>Reply directly to this email to continue the conversation.</p></div>`,
  })
  return true
}
