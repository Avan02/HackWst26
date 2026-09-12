/**
 * Shared API contract for TutorMatch.
 *
 * This is the single source of truth between the frontend (Brayden), the
 * realtime layer (Sam), the AI pipeline (Evan) and the API (Caden).
 * If you need a shape changed, change it HERE and tell the others.
 */

export type Role = 'student' | 'tutor';
export type SessionMode = 'video' | 'voice' | 'text';
export type SessionStatus = 'pending' | 'paid' | 'live' | 'ended' | 'processed';
export type PaymentStatus = 'pending' | 'confirmed' | 'failed';

/* ------------------------------------------------------------------ users */

export interface User {
  authSub: string;
  role: Role;
  name: string;
  email: string;
  avatarUrl?: string;
  walletAddress?: string;
}

/* ------------------------------------------------------------------- quiz */

export type QuizQuestionId =
  | 'intake'
  | 'explanation'
  | 'pace'
  | 'when_stuck'
  | 'structure'
  | 'goal';

export interface QuizOption {
  value: string;
  label: string;
}

export interface QuizQuestion {
  id: QuizQuestionId;
  prompt: string;
  /** Absent for free-text questions (currently only `goal`). */
  options?: QuizOption[];
  freeText?: boolean;
}

export interface QuizSubmission {
  /** Keyed by QuizQuestionId -> chosen option value (or free text for `goal`). */
  answers: Record<string, string>;
  subjects: string[];
  maxRateSol?: number;
}

export interface LearnerProfile {
  userId: string;
  subjects: string[];
  pace: string;
  goals: string;
  /** The natural-language sentence we embed. Handy for debugging matches. */
  profileSentence: string;
}

/* ------------------------------------------------------------------ match */

export interface TutorMatch {
  user: User;
  bio: string;
  subjects: string[];
  hourlyRateSol: number;
  rating: number;
  /** 0..1 weighted blend of style similarity, subject overlap and rating. */
  score: number;
  /** One-sentence Gemini explanation of why this tutor fits the learner. */
  rationale: string;
}

/* --------------------------------------------------------------- sessions */

export interface Session {
  id: string;
  studentId: string;
  tutorId: string;
  subject: string;
  mode: SessionMode;
  status: SessionStatus;
  roomUrl?: string;
  recordingUrl?: string;
  startedAt?: string;
  endedAt?: string;
}

export interface CreateSessionRequest {
  tutorId: string;
  subject: string;
  mode?: SessionMode;
}

/* --------------------------------------------------------------- payments */

export interface Payment {
  id: string;
  sessionId: string;
  txSignature: string;
  amountLamports: number;
  status: PaymentStatus;
  confirmedAt?: string;
}

export interface VerifyPaymentRequest {
  sessionId: string;
  txSignature: string;
}

/* --------------------------------------------------------- AI / recordings */

/**
 * A moment worth jumping to in the recording.
 *
 * `tMs` is milliseconds from the start of the recording, as an INTEGER.
 * Evan produces it; Brayden feeds it straight to the player's seek call.
 * Do not change this to seconds without telling both of them.
 */
export interface KeyMoment {
  tMs: number;
  title: string;
  why: string;
}

export interface SessionNotes {
  sessionId: string;
  summary: string;
  keyMoments: KeyMoment[];
  concepts: string[];
  actionItems: string[];
  generatedAt?: string;
}

export interface TranscriptSegment {
  sessionId: string;
  startMs: number;
  endMs: number;
  speaker: string;
  text: string;
}

/** Response from POST /recordings/upload — a presigned PUT to Vultr Object Storage. */
export interface UploadTicket {
  uploadUrl: string;
  objectKey: string;
  /** Seconds until `uploadUrl` stops working. */
  expiresIn: number;
}

/** Response from GET /sessions/:id/recording-url — a presigned GET for Gemini. */
export interface DownloadTicket {
  downloadUrl: string;
  objectKey: string;
  expiresIn: number;
}

/* ------------------------------------------------------------------ errors */

export interface ApiError {
  error: string;
  message: string;
}
