import { NextRequest } from 'next/server'

const DJANGO = process.env.DJANGO_URL || 'http://127.0.0.1:8000'

async function proxy(req: NextRequest, path: string[]) {
  let destPath = `/api/${path.join('/')}`
  if (!destPath.endsWith('/')) destPath += '/'

  const dest = `${DJANGO}${destPath}${new URL(req.url).search}`
  const headers = new Headers()
  const auth = req.headers.get('authorization')
  const contentType = req.headers.get('content-type')
  if (auth) headers.set('authorization', auth)
  if (contentType) headers.set('content-type', contentType)

  const body =
    req.method === 'GET' || req.method === 'HEAD' ? undefined : await req.arrayBuffer()

  const res = await fetch(dest, {
    method: req.method,
    headers,
    body,
    redirect: 'follow',
  })

  return new Response(res.body, {
    status: res.status,
    headers: {
      'content-type': res.headers.get('content-type') || 'application/json',
    },
  })
}

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  return proxy(req, (await ctx.params).path)
}

export async function POST(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  return proxy(req, (await ctx.params).path)
}

export async function DELETE(
  req: NextRequest,
  ctx: { params: Promise<{ path: string[] }> },
) {
  return proxy(req, (await ctx.params).path)
}
