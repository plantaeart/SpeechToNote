/**
 * Speaker Command Model (from database)
 */
export class SpeakerCommand {
  _id: string;
  id_command: number;
  command_name: string;
  command_vocal: string;
  command_description?: string;
  schema_version: string;
  created_at: string;
  updated_at: string;

  constructor(params: {
    _id: string;
    id_command: number;
    command_name: string;
    command_vocal: string;
    command_description?: string;
    schema_version: string;
    created_at: string;
    updated_at: string;
  }) {
    this._id = params._id;
    this.id_command = params.id_command;
    this.command_name = params.command_name;
    this.command_vocal = params.command_vocal;
    this.command_description = params.command_description;
    this.schema_version = params.schema_version;
    this.created_at = params.created_at;
    this.updated_at = params.updated_at;
  }
}
