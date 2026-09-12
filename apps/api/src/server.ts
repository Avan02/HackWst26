/**
 * TutorMatch API.
 *
 * PHASE 1 (now): every route returns fixture data so the frontend and the AI
 * pipeline can be built before TigerData exists. No database, no auth.
 *
 * PHASE 2: routes get swapped for real implementations ONE AT A TIME, so the
 * frontend never fully breaks. Each mock route below is marked with the phase
 * that replaces it.
 */

import Fastify from 'fastify';
import cors from '@fastify/cors';
import type {
  DownloadTicket,
  LearnerProfile,
  Payment,
  QuizSubmission,
  Session,
  UploadTicket,
} from '@tutormatch/types';
import {
  MOCK_NOTES,
  MOCK_SESSION,
  MOCK_SESSION_ID,
  MOCK_STUDENT,
  QUIZ_QUESTIONS,
  mockMatches,
} from './fixtures.ts';

const PORT = Number(process.env.PORT ?? 3000);
const HOST = process.env.HOST ?? '0.0.0.0';

const app = Fastify({ logger: true });

// Wide open on purpose: teammates run the frontend from localhost, from each
// other's machines, and from the .tech domain. Tighten before anything real.
await app.register(cors, { origin: true });

/* ------------------------------------------------------------------ health */

app.get('/health', async () => ({ ok: true, phase: 'mock', ts: new Date().toISOString() }));

/* -------------------------------------------------------------------- me */
// PHASE 3: replaced by JWT validation + lazy upsert into TigerData.

app.get('/me', async () => MOCK_STUDENT);

/* ------------------------------------------------------------------ quiz */

// Static content — this route is real already, no phase 2 needed.
app.get('/quiz/questions', async () => QUIZ_QUESTIONS);

// PHASE 4: answers -> profile sentence -> Gemini embedding -> learner_profiles.
app.post<{ Body: QuizSubmission }>('/quiz', async (req) => {
  const { answers, subjects } = req.body ?? { answers: {}, subjects: [] };
  const profile: LearnerProfile = {
    userId: MOCK_STUDENT.authSub,
    subjects: subjects ?? [],
    pace: answers?.pace ?? 'moderate',
    goals: answers?.goal ?? '',
    profileSentence:
      'Visual learner who prefers worked examples over abstract theory, moderate pace, wants to build intuition for calculus before exams.',
  };
  return profile;
});

/* ----------------------------------------------------------------- match */
// PHASE 4: replaced by the pgvector query + cached Gemini rationales.

app.get('/match', async () => mockMatches());

/* -------------------------------------------------------------- sessions */
// PHASE 5: real rows in TigerData; roomUrl comes from Sam's room-creation helper.

app.post('/sessions', async (req): Promise<Session> => {
  const body = (req.body ?? {}) as { tutorId?: string; subject?: string; mode?: Session['mode'] };
  return {
    ...MOCK_SESSION,
    tutorId: body.tutorId ?? MOCK_SESSION.tutorId,
    subject: body.subject ?? MOCK_SESSION.subject,
    mode: body.mode ?? 'video',
    status: 'pending',
  };
});

app.get<{ Params: { id: string } }>('/sessions/:id', async (req): Promise<Session> => ({
  ...MOCK_SESSION,
  id: req.params.id,
}));

/* -------------------------------------------------------------- payments */
// PHASE 5: getTransaction() against devnet, verify recipient + amount, persist.

app.post('/payments/verify', async (req): Promise<Payment> => {
  const body = (req.body ?? {}) as { sessionId?: string; txSignature?: string };
  return {
    id: 'mock-payment-0001',
    sessionId: body.sessionId ?? MOCK_SESSION_ID,
    txSignature: body.txSignature ?? 'MockSignature1111111111111111111111111111111111111111111111111111',
    amountLamports: 180_000_000,
    status: 'confirmed',
    confirmedAt: new Date().toISOString(),
  };
});

/* ------------------------------------------------- recordings + AI notes */

// PHASE 2: real presigned PUT against Vultr Object Storage. Sam consumes this.
app.post('/recordings/upload', async (req): Promise<UploadTicket> => {
  const body = (req.body ?? {}) as { sessionId?: string; contentType?: string };
  const sessionId = body.sessionId ?? MOCK_SESSION_ID;
  return {
    uploadUrl: `https://mock-bucket.vultrobjects.com/recordings/${sessionId}.mp4?mock-presigned=true`,
    objectKey: `recordings/${sessionId}.mp4`,
    expiresIn: 3600,
  };
});

// PHASE 2: real presigned GET. Evan consumes this to feed Gemini.
app.get<{ Params: { id: string } }>(
  '/sessions/:id/recording-url',
  async (req): Promise<DownloadTicket> => ({
    downloadUrl: `https://mock-bucket.vultrobjects.com/recordings/${req.params.id}.mp4?mock-presigned=true`,
    objectKey: `recordings/${req.params.id}.mp4`,
    expiresIn: 3600,
  }),
);

// PHASE 5: reads session_notes. Evan writes the row; Brayden renders it.
app.get<{ Params: { id: string } }>('/sessions/:id/notes', async (req) => ({
  ...MOCK_NOTES,
  sessionId: req.params.id,
}));

// PHASE 5: Evan POSTs finished notes here and we persist them.
app.post<{ Params: { id: string } }>('/sessions/:id/notes', async (req) => {
  app.log.info({ sessionId: req.params.id }, 'notes received (mock — not persisted)');
  return { ok: true, persisted: false };
});

/* ------------------------------------------------------------------ boot */

try {
  await app.listen({ port: PORT, host: HOST });
  app.log.info(`TutorMatch API (mock) listening on http://localhost:${PORT}`);
} catch (err) {
  app.log.error(err);
  process.exit(1);
}
