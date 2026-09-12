/**
 * Fixture data.
 *
 * Serves two purposes:
 *   1. The mock API returns this so the frontend can be built before the DB exists.
 *   2. `src/db/seed.ts` loads TUTORS into TigerData as the real seed data.
 *
 * The teaching-style bios are deliberately DISTINCT from one another. If they all
 * sound alike, their embeddings cluster and the match ranking looks arbitrary.
 */

import type {
  QuizQuestion,
  Session,
  SessionNotes,
  TutorMatch,
  User,
} from '@tutormatch/types';

/* ------------------------------------------------------------------- quiz */

export const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: 'intake',
    prompt: 'When you meet a new idea, what makes it click fastest?',
    options: [
      { value: 'visual', label: 'A diagram or picture of how it fits together' },
      { value: 'verbal', label: 'Someone talking me through it out loud' },
      { value: 'reading', label: 'Reading a clear written explanation' },
      { value: 'kinesthetic', label: 'Trying it myself and seeing what breaks' },
    ],
  },
  {
    id: 'explanation',
    prompt: 'Which explanation style do you prefer?',
    options: [
      { value: 'examples_first', label: 'Show me a worked example, then the rule' },
      { value: 'theory_first', label: 'Give me the rule, then we apply it' },
      { value: 'analogy', label: 'Compare it to something I already understand' },
      { value: 'discovery', label: 'Let me poke at it until I figure it out' },
    ],
  },
  {
    id: 'pace',
    prompt: 'What pace suits you?',
    options: [
      { value: 'slow', label: 'Slow and thorough — I want every step' },
      { value: 'moderate', label: 'Moderate — steady with room for questions' },
      { value: 'fast', label: 'Fast — hit the highlights, I fill gaps myself' },
    ],
  },
  {
    id: 'when_stuck',
    prompt: "When you're stuck, what do you want your tutor to do?",
    options: [
      { value: 'hint', label: 'Drop a small hint and let me keep trying' },
      { value: 'walkthrough', label: 'Walk me through the whole thing start to finish' },
      { value: 'socratic', label: 'Ask me questions until I find it myself' },
      { value: 'similar_example', label: 'Show a similar problem solved, then I retry' },
    ],
  },
  {
    id: 'structure',
    prompt: 'How should a session be structured?',
    options: [
      { value: 'agenda', label: 'A clear agenda we work through' },
      { value: 'freeform', label: 'Freeform — I bring questions as they come' },
      { value: 'drilling', label: 'Lots of practice problems back to back' },
      { value: 'discussion', label: 'Open discussion of the underlying concepts' },
    ],
  },
  {
    id: 'goal',
    prompt: "What are you working toward right now?",
    freeText: true,
  },
];

/* ------------------------------------------------------------------ tutors */

export interface TutorFixture {
  authSub: string;
  name: string;
  email: string;
  avatarUrl: string;
  bio: string;
  subjects: string[];
  hourlyRateSol: number;
  rating: number;
}

export const TUTORS: TutorFixture[] = [
  {
    authSub: 'seed|tutor-01',
    name: 'Maya Okonkwo',
    email: 'maya@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=47',
    bio: 'Teaches almost entirely through diagrams. Draws the shape of a problem on a shared whiteboard before touching any algebra, and will redraw it three different ways until the picture makes the answer obvious. Best for people who need to see a thing to believe it.',
    subjects: ['calculus'],
    hourlyRateSol: 0.18,
    rating: 4.9,
  },
  {
    authSub: 'seed|tutor-02',
    name: 'Dev Raghunathan',
    email: 'dev@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=12',
    bio: 'Relentless problem-drilling. Expect twenty short problems in an hour, graded live, with the pattern named after each one. Not much theory talk — the belief here is that fluency comes from reps and that speed removes fear.',
    subjects: ['calculus'],
    hourlyRateSol: 0.12,
    rating: 4.6,
  },
  {
    authSub: 'seed|tutor-03',
    name: 'Priya Venkatesan',
    email: 'priya@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=32',
    bio: 'Socratic to a fault. Almost never gives a direct answer, instead asking narrowing questions until the student says the thing out loud themselves. Slow going at first and enormously sticky afterwards. Suits people who resent being handed answers.',
    subjects: ['calculus', 'physics'],
    hourlyRateSol: 0.2,
    rating: 4.8,
  },
  {
    authSub: 'seed|tutor-04',
    name: 'Tomas Lindqvist',
    email: 'tomas@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=52',
    bio: 'Formal and theory-first. Starts from the definition, states the theorem, proves it, and only then works an example. Dry by design. Students who want to know *why* a rule is true, rather than just how to apply it, tend to stay for months.',
    subjects: ['calculus'],
    hourlyRateSol: 0.22,
    rating: 4.5,
  },
  {
    authSub: 'seed|tutor-05',
    name: 'Rosa Delgado',
    email: 'rosa@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=45',
    bio: 'Explains everything by analogy to ordinary life — derivatives as speedometers, integrals as filling a bathtub. Warm, chatty, low-pressure sessions aimed at students who have decided they are "bad at math" and need that belief dismantled before anything else.',
    subjects: ['calculus'],
    hourlyRateSol: 0.14,
    rating: 4.7,
  },
  {
    authSub: 'seed|tutor-06',
    name: 'Ken Arai',
    email: 'ken@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=13',
    bio: 'Structured agenda every time: five minutes reviewing last session, thirty on the new topic, twenty on mixed practice, five setting homework. Sends written notes afterward. Ideal for students who are behind and need a plan more than inspiration.',
    subjects: ['calculus', 'chemistry'],
    hourlyRateSol: 0.16,
    rating: 4.8,
  },
  {
    authSub: 'seed|tutor-07',
    name: 'Amara Boateng',
    email: 'amara@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=26',
    bio: 'Runs chemistry as a visual molecular story — builds 3D models on screen and rotates them so students can see why a reaction goes one way and not the other. Very little rote memorisation; heavy emphasis on seeing the mechanism.',
    subjects: ['chemistry'],
    hourlyRateSol: 0.19,
    rating: 4.9,
  },
  {
    authSub: 'seed|tutor-08',
    name: 'Colin Mbeki',
    email: 'colin@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=14',
    bio: 'Exam-focused chemistry drilling. Works from past papers exclusively, times every question, and teaches the specific tricks markers reward. Blunt feedback. Students cramming for a date circled on the calendar do well here.',
    subjects: ['chemistry'],
    hourlyRateSol: 0.13,
    rating: 4.4,
  },
  {
    authSub: 'seed|tutor-09',
    name: 'Hannah Weiss',
    email: 'hannah@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=44',
    bio: 'Lab-first chemistry. Every concept arrives attached to an experiment, often demonstrated live on camera. Encourages students to predict the outcome before seeing it, then explains the gap between guess and result. Messy, memorable sessions.',
    subjects: ['chemistry'],
    hourlyRateSol: 0.21,
    rating: 4.7,
  },
  {
    authSub: 'seed|tutor-10',
    name: 'Yusuf Karim',
    email: 'yusuf@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=59',
    bio: 'Reads like a textbook in the best way — precise written explanations shared in the chat as the session goes, so the student leaves with a clean document. Quiet, unhurried, and excellent for learners who process by reading rather than listening.',
    subjects: ['chemistry', 'biology'],
    hourlyRateSol: 0.15,
    rating: 4.6,
  },
  {
    authSub: 'seed|tutor-11',
    name: 'Grace Sullivan',
    email: 'grace@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=31',
    bio: 'Project-based computer science. No lectures — the student builds something small and real from minute one, and concepts get introduced only when the build demands them. Suits people who lose interest in abstractions with no payoff.',
    subjects: ['computer_science'],
    hourlyRateSol: 0.2,
    rating: 4.9,
  },
  {
    authSub: 'seed|tutor-12',
    name: 'Emeka Nwosu',
    email: 'emeka@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=68',
    bio: 'Whiteboards data structures as pictures — boxes, arrows, and memory laid out visually before a single line of code. Especially good at making pointers and recursion stop being terrifying. Interview-prep heavy.',
    subjects: ['computer_science'],
    hourlyRateSol: 0.23,
    rating: 4.8,
  },
  {
    authSub: 'seed|tutor-13',
    name: 'Sofia Marchetti',
    email: 'sofia@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=49',
    bio: 'Pair-programs the entire session with the student driving and never touches the keyboard. Asks "what do you think that error means?" more than anything else. Frustrating for people in a hurry, transformative for people who want independence.',
    subjects: ['computer_science'],
    hourlyRateSol: 0.17,
    rating: 4.7,
  },
  {
    authSub: 'seed|tutor-14',
    name: 'Arjun Malhotra',
    email: 'arjun@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=56',
    bio: 'Theory-heavy computer science — complexity analysis, formal correctness, why an algorithm is optimal rather than merely working. Moves fast and assumes the student wants depth. Not the right fit for someone with a deadline tomorrow.',
    subjects: ['computer_science'],
    hourlyRateSol: 0.25,
    rating: 4.5,
  },
  {
    authSub: 'seed|tutor-15',
    name: 'Nadia Haddad',
    email: 'nadia@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=24',
    bio: 'Teaches programming through analogy and story — a queue is a checkout line, a hash map is a coat check. Patient with absolute beginners and deliberately avoids jargon until the idea has landed. Gentle pace, lots of encouragement.',
    subjects: ['computer_science'],
    hourlyRateSol: 0.14,
    rating: 4.8,
  },
  {
    authSub: 'seed|tutor-16',
    name: 'Leo Fitzgerald',
    email: 'leo@tutormatch.tech',
    avatarUrl: 'https://i.pravatar.cc/160?img=51',
    bio: 'Fast, high-level sessions for students who are already competent and want the last twenty percent. Skips fundamentals, talks in shorthand, and focuses on edge cases and elegance. Explicitly not for beginners.',
    subjects: ['computer_science', 'calculus'],
    hourlyRateSol: 0.26,
    rating: 4.6,
  },
];

/* -------------------------------------------------------------- mock users */

export const MOCK_STUDENT: User = {
  authSub: 'auth0|mock-student',
  role: 'student',
  name: 'Alex Rivera',
  email: 'alex@example.com',
  avatarUrl: 'https://i.pravatar.cc/160?img=8',
  walletAddress: '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU',
};

/** Hand-written rationales so the mock match screen looks like the real thing. */
const MOCK_RATIONALES: Record<string, string> = {
  'seed|tutor-01':
    'You said diagrams make things click — Maya draws the shape of every problem before touching the algebra.',
  'seed|tutor-05':
    'Rosa leans on everyday analogies and a low-pressure pace, which fits your preference for intuition over formalism.',
  'seed|tutor-12':
    'Emeka whiteboards structures visually before any code, matching how you said you take in new ideas.',
};

export function mockMatches(): TutorMatch[] {
  const picks = ['seed|tutor-01', 'seed|tutor-05', 'seed|tutor-12'];
  return picks.map((sub, i) => {
    const t = TUTORS.find((x) => x.authSub === sub)!;
    return {
      user: {
        authSub: t.authSub,
        role: 'tutor' as const,
        name: t.name,
        email: t.email,
        avatarUrl: t.avatarUrl,
      },
      bio: t.bio,
      subjects: t.subjects,
      hourlyRateSol: t.hourlyRateSol,
      rating: t.rating,
      score: [0.91, 0.84, 0.79][i],
      rationale: MOCK_RATIONALES[sub],
    };
  });
}

/* ----------------------------------------------------------- mock session */

export const MOCK_SESSION_ID = '11111111-2222-3333-4444-555555555555';

export const MOCK_SESSION: Session = {
  id: MOCK_SESSION_ID,
  studentId: MOCK_STUDENT.authSub,
  tutorId: 'seed|tutor-01',
  subject: 'calculus',
  mode: 'video',
  status: 'processed',
  roomUrl: 'https://tutormatch.daily.co/mock-room',
  recordingUrl: 'https://example.com/mock-recording.mp4',
  startedAt: '2026-09-12T18:00:00.000Z',
  endedAt: '2026-09-12T18:42:00.000Z',
};

/**
 * Realistic notes payload. Brayden builds the recap page against this;
 * Evan's pipeline must produce this exact shape.
 */
export const MOCK_NOTES: SessionNotes = {
  sessionId: MOCK_SESSION_ID,
  summary:
    'Worked through the chain rule, starting from why composition requires it rather than how to apply it. Alex could differentiate simple polynomials confidently but stalled whenever a function appeared inside another. Maya drew the "outer box / inner box" diagram three times with different examples until Alex applied it unprompted to sin(3x²). Ended with four practice problems, three correct.',
  keyMoments: [
    {
      tMs: 154000,
      title: 'The outer/inner box diagram',
      why: 'First time the chain rule is drawn visually — this is the explanation that finally landed.',
    },
    {
      tMs: 428000,
      title: 'Alex misapplies the rule to sin(3x²)',
      why: 'The inner derivative gets dropped. Worth rewatching to see exactly where the slip happens.',
    },
    {
      tMs: 612000,
      title: 'Correction and the "peel the onion" rule of thumb',
      why: 'Maya reframes the mistake as a peeling order, which Alex repeats back correctly.',
    },
    {
      tMs: 1187000,
      title: 'Alex solves one unassisted',
      why: 'The turning point — full chain rule applied with no prompting.',
    },
    {
      tMs: 1502000,
      title: 'Homework set and next session planned',
      why: 'Four problems assigned; quotient rule flagged as the next gap.',
    },
  ],
  concepts: [
    'Chain rule',
    'Function composition',
    'Derivative of trigonometric functions',
    'Power rule (review)',
  ],
  actionItems: [
    'Finish problems 3 and 4 from the practice set',
    'Rewatch 2:34 if the outer/inner split stops being obvious',
    'Come to next session with one quotient-rule question',
  ],
  generatedAt: '2026-09-12T18:47:12.000Z',
};
