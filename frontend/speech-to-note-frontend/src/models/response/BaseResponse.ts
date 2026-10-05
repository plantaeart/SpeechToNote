import { SpeakerCommand } from "../SpeakerCommand";
import { SpeakerNote } from "../SpeakerNote";

/**
 * Standard API Response (matches FastAPI BaseResponse)
 */
export interface BaseResponse<T = unknown> {
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
 *
 * Each guard names the properties it requires, so the expected API shape is
 * visible here rather than hidden behind a generic record check.
 */
export class ResponseValidator {
  static isBaseResponse<T>(obj: unknown): obj is BaseResponse<T> {
    return (
      typeof obj === "object" &&
      obj !== null &&
      "status_code" in obj &&
      typeof obj.status_code === "number" &&
      "message" in obj &&
      typeof obj.message === "string" &&
      "data" in obj
    );
  }

  static isSpeakerNote(obj: unknown): obj is SpeakerNote {
    return (
      typeof obj === "object" &&
      obj !== null &&
      "_id" in obj &&
      typeof obj._id === "string" &&
      "id_note" in obj &&
      typeof obj.id_note === "number" &&
      "title" in obj &&
      typeof obj.title === "string" &&
      "content" in obj &&
      typeof obj.content === "string" &&
      "commands" in obj &&
      Array.isArray(obj.commands) &&
      "schema_version" in obj &&
      typeof obj.schema_version === "string" &&
      "created_at" in obj &&
      typeof obj.created_at === "string" &&
      "updated_at" in obj &&
      typeof obj.updated_at === "string"
    );
  }

  static isSpeakerCommand(obj: unknown): obj is SpeakerCommand {
    return (
      typeof obj === "object" &&
      obj !== null &&
      "_id" in obj &&
      typeof obj._id === "string" &&
      "id_command" in obj &&
      typeof obj.id_command === "number" &&
      "command_name" in obj &&
      typeof obj.command_name === "string" &&
      "command_vocal" in obj &&
      typeof obj.command_vocal === "string" &&
      "schema_version" in obj &&
      typeof obj.schema_version === "string" &&
      "created_at" in obj &&
      typeof obj.created_at === "string" &&
      "updated_at" in obj &&
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
