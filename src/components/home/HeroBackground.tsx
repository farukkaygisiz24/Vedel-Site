'use client'

import { useEffect, useRef, useState } from 'react'
import Image from 'next/image'
import { CAMPAIGN_SURFACE_CLASS } from '@/config/campaign'

type HeroBackgroundProps = {
  imageSrc: string
  imageAlt: string
  imageClassName: string
  videoClassName?: string
  videoSrc?: string
  posterSrc?: string
  overlayClassName: string
  showPattern: boolean
  fitContain?: boolean
  aspectBoxLayout?: boolean
  contentInsetClassName?: string
}

export default function HeroBackground({
  imageSrc,
  imageAlt,
  imageClassName,
  videoClassName,
  videoSrc,
  posterSrc,
  overlayClassName,
  showPattern,
  fitContain = false,
  aspectBoxLayout = false,
  contentInsetClassName = 'px-4 sm:px-6 md:px-8 lg:px-12',
}: HeroBackgroundProps) {
  const [useVideo, setUseVideo] = useState(false)
  const [videoReady, setVideoReady] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (!videoSrc) return

    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    const connection = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection

    const syncVideo = () => {
      const saveData = connection?.saveData ?? false
      const allowVideo = !motionQuery.matches && !saveData

      if (!allowVideo) {
        setUseVideo(false)
        setVideoReady(false)
        return
      }

      setUseVideo(true)
    }

    syncVideo()

    motionQuery.addEventListener('change', syncVideo)

    return () => {
      motionQuery.removeEventListener('change', syncVideo)
    }
  }, [videoSrc])

  useEffect(() => {
    const video = videoRef.current
    if (!useVideo || !video) return

    const playVideo = () => {
      video.play().catch(() => {
        setUseVideo(false)
        setVideoReady(false)
      })
    }

    if (video.readyState >= HTMLMediaElement.HAVE_FUTURE_DATA) {
      playVideo()
      return
    }

    video.addEventListener('canplay', playVideo, { once: true })
    return () => video.removeEventListener('canplay', playVideo)
  }, [useVideo, videoSrc])

  const poster = posterSrc ?? imageSrc
  const resolvedVideoClassName = videoClassName ?? imageClassName

  const media = (
    <>
      {showPattern && (
        <div className="absolute inset-0 z-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iMzYgMzR2LTRoLTR2NGg0em0wLTh2LTRoLTR2NGg0em0wLTh2LTRoLTR2NGg0em0wLThWMmgtNHY0aDR6TTYgMzR2LTRIMnY0aDR6bTAtOHYtNEgydjRoNHptMC04di00SDJ2NGg0em0wLThWMkgydjRoNHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-10" />
      )}

      <Image
        src={imageSrc}
        alt={imageAlt}
        fill
        priority
        quality={90}
        sizes="(max-width: 1280px) 100vw, 1280px"
        className={`${imageClassName} transition-opacity duration-700 ${useVideo && videoReady ? 'opacity-0' : 'opacity-100'}`}
      />

      {useVideo && videoSrc && (
        <video
          ref={videoRef}
          autoPlay
          muted
          loop
          playsInline
          poster={poster}
          preload="metadata"
          aria-hidden
          disablePictureInPicture
          controlsList="nodownload noremoteplayback"
          onContextMenu={(event) => event.preventDefault()}
          onDragStart={(event) => event.preventDefault()}
          onCanPlay={() => setVideoReady(true)}
          className={`absolute inset-0 z-[1] h-full w-full select-none transition-opacity duration-700 ${videoReady ? 'opacity-100' : 'opacity-0'} ${resolvedVideoClassName}`}
        >
          <source src={videoSrc} type="video/mp4" />
        </video>
      )}

      <div className={`absolute inset-0 z-10 ${overlayClassName}`} />
    </>
  )

  if (aspectBoxLayout) {
    return <div className="absolute inset-0">{media}</div>
  }

  return (
    <div className={`absolute inset-0 ${fitContain ? `${CAMPAIGN_SURFACE_CLASS} ${contentInsetClassName}` : ''}`}>
      <div className={fitContain ? 'relative mx-auto h-full w-full max-w-7xl' : 'absolute inset-0'}>
        {media}
      </div>
    </div>
  )
}
