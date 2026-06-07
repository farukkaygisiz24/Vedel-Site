import { createReadStream, statSync } from 'fs'
import { Readable } from 'stream'
import { NextRequest, NextResponse } from 'next/server'
import {
  CAMPAIGN_VIDEO_PATH,
  isAllowedVideoRequest,
} from '@/lib/campaignVideo'

export const runtime = 'nodejs'

function videoStreamResponse(
  stream: Readable,
  status: number,
  headers: Record<string, string>
) {
  return new NextResponse(Readable.toWeb(stream) as ReadableStream, {
    status,
    headers,
  })
}

export async function GET(request: NextRequest) {
  const referer = request.headers.get('referer')
  const origin = request.headers.get('origin')
  const host = request.headers.get('host')

  if (!isAllowedVideoRequest(referer, origin, host)) {
    return new NextResponse('Forbidden', { status: 403 })
  }

  let fileSize: number
  try {
    fileSize = statSync(CAMPAIGN_VIDEO_PATH).size
  } catch {
    return new NextResponse('Not found', { status: 404 })
  }

  const range = request.headers.get('range')
  const commonHeaders = {
    'Content-Type': 'video/mp4',
    'Accept-Ranges': 'bytes',
    'Cache-Control': 'private, no-store, max-age=0',
    'X-Content-Type-Options': 'nosniff',
    'Content-Disposition': 'inline',
  }

  if (range) {
    const match = /^bytes=(\d*)-(\d*)$/.exec(range)
    if (!match) {
      return new NextResponse('Invalid range', { status: 416 })
    }

    const start = match[1] ? parseInt(match[1], 10) : 0
    const end = match[2] ? parseInt(match[2], 10) : fileSize - 1

    if (Number.isNaN(start) || Number.isNaN(end) || start > end || start >= fileSize) {
      return new NextResponse('Invalid range', { status: 416 })
    }

    const safeEnd = Math.min(end, fileSize - 1)
    const chunkSize = safeEnd - start + 1

    return videoStreamResponse(createReadStream(CAMPAIGN_VIDEO_PATH, { start, end: safeEnd }), 206, {
      ...commonHeaders,
      'Content-Range': `bytes ${start}-${safeEnd}/${fileSize}`,
      'Content-Length': String(chunkSize),
    })
  }

  return videoStreamResponse(createReadStream(CAMPAIGN_VIDEO_PATH), 200, {
    ...commonHeaders,
    'Content-Length': String(fileSize),
  })
}
