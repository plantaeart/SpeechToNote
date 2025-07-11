import { CURRENT_ENV } from '@/config/env.current'
import ENV_LOCAL from '@/config/env.local'
import ENV_DOCKER from '@/config/env.local.docker'

export class GoogleSpeechService {
  private apiKey: string
  private mediaRecorder: MediaRecorder | null = null
  private audioChunks: Blob[] = []
  private isRecording = false

  constructor() {
    const config = CURRENT_ENV === 'local_docker' ? ENV_DOCKER : ENV_LOCAL
    this.apiKey = config.GCP_API_KEY
  }

  async requestMicrophonePermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach((track) => track.stop()) // Stop immediately after permission
      return true
    } catch (error) {
      console.error('Microphone permission denied:', error)
      return false
    }
  }

  async startRecording(): Promise<MediaStream | null> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      })

      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      })

      this.audioChunks = []
      this.isRecording = true

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data)
        }
      }

      this.mediaRecorder.start(1000) // Collect data every second
      return stream
    } catch (error) {
      console.error('Failed to start recording:', error)
      return null
    }
  }

  stopRecording(): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder || !this.isRecording) {
        resolve('')
        return
      }

      this.mediaRecorder.onstop = async () => {
        try {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' })
          const transcript = await this.transcribeAudio(audioBlob)
          resolve(transcript)
        } catch (error) {
          reject(error)
        }
      }

      this.mediaRecorder.stop()
      this.isRecording = false

      // Stop all tracks
      if (this.mediaRecorder.stream) {
        this.mediaRecorder.stream.getTracks().forEach((track) => track.stop())
      }
    })
  }

  private async transcribeAudio(audioBlob: Blob): Promise<string> {
    try {
      // Convert audio to base64
      const base64Audio = await this.blobToBase64(audioBlob)

      const requestBody = {
        config: {
          encoding: 'WEBM_OPUS',
          sampleRateHertz: 16000,
          languageCode: 'fr-FR',
          enableAutomaticPunctuation: true,
          model: 'latest_short',
        },
        audio: {
          content: base64Audio.split(',')[1], // Remove data:audio/webm;base64, prefix
        },
      }

      const response = await fetch(
        `https://speech.googleapis.com/v1/speech:recognize?key=${this.apiKey}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        },
      )

      if (!response.ok) {
        throw new Error(`Google Speech API error: ${response.status}`)
      }

      const result = await response.json()

      if (result.results && result.results.length > 0) {
        return result.results[0].alternatives[0].transcript || ''
      }

      return ''
    } catch (error) {
      console.error('Transcription error:', error)
      throw error
    }
  }

  private blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  }

  getRecordingStatus(): boolean {
    return this.isRecording
  }
}
