import {
  CURRENT_ENV,
  GCP_STT_API_COLLECT_EVERY_X_MS,
  GCP_STT_API_TRANSCRIBE_EVERY_X_MS,
} from '@/config/env.current'
import ENV_LOCAL from '@/config/env.local'
import ENV_DOCKER from '@/config/env.local.docker'
import axios from 'axios'

export class GoogleSpeechService {
  private apiKey: string
  private mediaRecorder: MediaRecorder | null = null
  private audioChunks: Blob[] = []
  private isRecording = false
  private onTranscriptCallback: ((transcript: string) => void) | null = null
  private transcriptionInterval: number | null = null

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

  setTranscriptCallback(callback: (transcript: string) => void) {
    this.onTranscriptCallback = callback
  }

  async startRecording(): Promise<MediaStream | null> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 48000,
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

      this.mediaRecorder.start(GCP_STT_API_COLLECT_EVERY_X_MS) // Collect data every 1 second

      // Start continuous transcription every 2 seconds
      this.transcriptionInterval = setInterval(async () => {
        if (this.audioChunks.length > 0 && this.onTranscriptCallback) {
          try {
            // Take all current chunks for transcription
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' })
            const transcript = await this.transcribeAudio(audioBlob)
            if (transcript.trim()) {
              console.log('Real-time transcript:', transcript)
              this.onTranscriptCallback(transcript)
            }
          } catch (error) {
            console.warn('Real-time transcription error:', error)
          }
        }
      }, GCP_STT_API_TRANSCRIBE_EVERY_X_MS) // Transcribe every 2 seconds

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

      // Clear the transcription interval
      if (this.transcriptionInterval) {
        clearInterval(this.transcriptionInterval)
        this.transcriptionInterval = null
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

      if (this.mediaRecorder.stream) {
        this.mediaRecorder.stream.getTracks().forEach((track) => track.stop())
      }
    })
  }

  private async transcribeAudio(audioBlob: Blob): Promise<string> {
    try {
      // Convert webm to base64
      const base64Audio = await this.blobToBase64(audioBlob)
      const audioContent = base64Audio.split(',')[1] // Remove data:audio/webm;base64, prefix

      // Validate that we have actual audio content
      if (!audioContent || audioContent.length < 100) {
        console.warn('Audio content too small, skipping transcription')
        return ''
      }

      const requestBody = {
        config: {
          encoding: 'WEBM_OPUS',
          sampleRateHertz: 48000,
          languageCode: 'fr-FR',
          enableAutomaticPunctuation: false,
          model: 'default',
          audioChannelCount: 1,
        },
        audio: {
          content: audioContent,
        },
      }

      const response = await axios.post(
        `https://speech.googleapis.com/v1/speech:recognize?key=${this.apiKey}`,
        requestBody,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        },
      )

      const result = response.data

      if (result.results && result.results.length > 0) {
        return result.results[0].alternatives[0].transcript || ''
      }

      return ''
    } catch (error) {
      console.error('Transcription error:', error)
      if (axios.isAxiosError(error)) {
        console.error('Axios error details:', error.response?.data)
        throw new Error(
          `Google Speech API error: ${error.response?.status} - ${error.response?.data}`,
        )
      }
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
