/**
 * Speaker Note Model (from database)
 */
export class SpeakerNote {
  _id: string;
  id_note: number;
  title: string;
  content: string;
  commands: string[];
  schema_version: string;
  created_at: string;
  updated_at: string;

  constructor(params: {
    _id: string;
    id_note: number;
    title: string;
    content: string;
    commands: string[];
    schema_version: string;
    created_at: string;
    updated_at: string;
  }) {
    this._id = params._id;
    this.id_note = params.id_note;
    this.title = params.title;
    this.content = params.content;
    this.commands = params.commands;
    this.schema_version = params.schema_version;
    this.created_at = params.created_at;
    this.updated_at = params.updated_at;
  }
}
