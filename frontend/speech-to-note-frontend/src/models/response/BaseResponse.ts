import { SpeakerCommand } from "../SpeakerCommand";
import { SpeakerNote } from "../SpeakerNote";

/**
 * Standard API Response (matches FastAPI BaseResponse)
 */
export interface BaseResponse<T = any> {
  data: T | null;
  status_code: number;
  message: string;
}

/**
 * Delete Response Data
 */
export interface DeleteResponse {
  deleted_count: number;
}

/**
 * Single Delete Response Data
 */
export interface SingleDeleteResponse {
  deleted_id_note?: number;
  deleted_id_command?: number;
}

/**
 * API Error Response
 */
export interface ApiError {
  detail?: string;
  message?: string;
  status_code: number;
}

/**
 * Helper class for creating BaseResponse objects (matches Python model)
 */
export class BaseResponseBuilder {
  static success<T>(
    data: T | null = null,
    message: string = "Success",
    status_code: number = 200
  ): BaseResponse<T> {
    return {
      data,
      status_code,
      message,
    };
  }

  static error<T>(
    message: string,
    status_code: number = 400,
    data: T | null = null
  ): BaseResponse<T> {
    return {
      data,
      status_code,
      message,
    };
  }
}

/**
 * Type guards for response validation
 */
export class ResponseValidator {
  static isBaseResponse<T>(obj: any): obj is BaseResponse<T> {
    return (
      obj &&
      typeof obj.status_code === "number" &&
      typeof obj.message === "string" &&
      (obj.data !== undefined || obj.data === null)
    );
  }

  static isSpeakerNote(obj: any): obj is SpeakerNote {
    return (
      obj &&
      typeof obj._id === "string" &&
      typeof obj.id_note === "number" &&
      typeof obj.title === "string" &&
      typeof obj.content === "string" &&
      Array.isArray(obj.commands) &&
      typeof obj.schema_version === "string" &&
      typeof obj.created_at === "string" &&
      typeof obj.updated_at === "string"
    );
  }

  static isSpeakerCommand(obj: any): obj is SpeakerCommand {
    return (
      obj &&
      typeof obj._id === "string" &&
      typeof obj.id_command === "number" &&
      typeof obj.command_name === "string" &&
      typeof obj.command_vocal === "string" &&
      typeof obj.schema_version === "string" &&
      typeof obj.created_at === "string" &&
      typeof obj.updated_at === "string"
    );
  }

  static isSuccessResponse<T>(response: BaseResponse<T>): boolean {
    return response.status_code >= 200 && response.status_code < 300;
  }

  static isErrorResponse<T>(response: BaseResponse<T>): boolean {
    return response.status_code >= 400;
  }
}
