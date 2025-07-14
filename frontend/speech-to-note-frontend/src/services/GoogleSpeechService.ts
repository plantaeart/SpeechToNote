import {
  GCP_STT_API_COLLECT_EVERY_X_MS,
  GCP_STT_API_TRANSCRIBE_EVERY_X_MS,
  getEnvironmentConfig,
} from '@/config/env.current'
import { useRecordingStore } from '@/stores/recording-store'
import axios from 'axios'

export class GoogleSpeechService {
  private apiKey: string
  private mediaRecorder: MediaRecorder | null = null
  private audioChunks: Blob[] = []
  private onTranscriptCallback: ((transcript: string) => void) | null = null
  private transcriptionInterval: number | null = null
  private recordingStore = useRecordingStore()

  constructor() {
    const config = getEnvironmentConfig()
    this.apiKey = config.GCP_API_KEY
  }

  /**
   * Requests permission to use the microphone.
   * @returns Promise<boolean> - Returns true if permission is granted, false otherwise.
   */
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

  /**
   * Sets the callback function to handle real-time transcription updates.
   * @param callback - Function to call with the real-time transcript.
   */
  setTranscriptCallback(callback: (transcript: string) => void) {
    this.onTranscriptCallback = callback
  }

  /**
   * Starts recording audio from the microphone and sets up real-time transcription.
   * @returns Promise<MediaStream | null> - Returns the MediaStream if successful, null otherwise.
   */
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

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data)
        }
      }

      this.mediaRecorder.start(GCP_STT_API_COLLECT_EVERY_X_MS) // Collect data every X ms

      // Start continuous transcription every X ms
      this.transcriptionInterval = setInterval(async () => {
        // Check if recording is still active before transcribing
        if (
          this.audioChunks.length > 0 &&
          this.onTranscriptCallback &&
          this.recordingStore.isRecording
        ) {
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
      }, GCP_STT_API_TRANSCRIBE_EVERY_X_MS)

      return stream
    } catch (error) {
      console.error('Failed to start recording:', error)
      return null
    }
  }

  /**
   * Stops the recording and returns the final transcript.
   * @returns Promise<string> - Returns the final transcript after stopping the recording.
   */
  stopRecording(): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        resolve('')
        return
      }

      // Clear the transcription interval immediately
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

      if (this.mediaRecorder.stream) {
        this.mediaRecorder.stream.getTracks().forEach((track) => track.stop())
      }
    })
  }

  /**
   * Transcribes the audio blob using Google Speech-to-Text API.
   * @param audioBlob - The audio blob to transcribe.
   * @returns Promise<string> - Returns the transcribed text.
   */
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

  /**
   * Converts a Blob to a Base64 string.
   * @param blob - The Blob to convert.
   * @returns Promise<string> - Returns the Base64 string representation of the Blob.
   */
  private blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  }

  /**
   * Returns the current recording status.
   * @returns boolean - True if currently recording, false otherwise.
   */
  getRecordingStatus(): boolean {
    return this.recordingStore.isRecording
  }
}
