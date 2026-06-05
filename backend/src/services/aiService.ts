import Anthropic from '@anthropic-ai/sdk';
import { IAssignment } from '../types';
import dotenv from 'dotenv';
dotenv.config();

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || 'dummy_key'
});

export const buildPrompt = (assignment: IAssignment): string => {
  return `
You are an expert curriculum designer and teacher. Create a question paper based on the following requirements:

Subject: ${assignment.subject}
Topic: ${assignment.topic}
Grade Level: ${assignment.gradeLevel}
Total Marks: ${assignment.totalMarks}
Number of Questions: ${assignment.numberOfQuestions}
Difficulty: ${assignment.difficulty}
Question Types: ${assignment.questionTypes.join(', ')}
Additional Instructions: ${assignment.additionalInstructions || 'None'}

Context Material from teacher (if any):
${assignment.fileText ? assignment.fileText : 'None'}

OUTPUT FORMAT:
You MUST return ONLY valid JSON matching this exact structure, with no markdown formatting or extra text outside the JSON:

{
  "title": "Topic Test: ${assignment.topic}",
  "subject": "${assignment.subject}",
  "grade": "${assignment.gradeLevel}",
  "totalMarks": ${assignment.totalMarks},
  "timeAllowed": "1 Hour",
  "sections": [
    {
      "sectionLabel": "A",
      "sectionTitle": "Multiple Choice Questions",
      "instruction": "Attempt all questions",
      "marks": 10,
      "questions": [
        {
          "questionNumber": 1,
          "text": "What is...?",
          "options": ["A", "B", "C", "D"], // Only if MCQ
          "difficulty": "Easy", // Must be "Easy", "Moderate", or "Hard"
          "marks": 2,
          "type": "MCQ"
        }
      ]
    }
  ]
}

Ensure the sum of marks of all questions equals ${assignment.totalMarks}.
Ensure the number of questions equals ${assignment.numberOfQuestions}.
The question difficulties should reflect the requested difficulty: ${assignment.difficulty}.
`;
};

export const generatePaper = async (prompt: string): Promise<any> => {
  // If no API key is provided, we can return a mock for testing without failing
  if (!process.env.ANTHROPIC_API_KEY) {
    console.log("WARNING: NO ANTHROPIC_API_KEY provided, returning mock data.");
    return {
      title: "Mock AI Generated Paper",
      subject: "Math",
      grade: "Grade 10",
      totalMarks: 10,
      timeAllowed: "1 Hour",
      sections: [
        {
          "sectionLabel": "A",
          "sectionTitle": "General Questions",
          "instruction": "Attempt all",
          "marks": 10,
          "questions": [
            {
              "questionNumber": 1,
              "text": "What is 2+2?",
              "options": ["3", "4", "5", "6"],
              "difficulty": "Easy",
              "marks": 10,
              "type": "MCQ"
            }
          ]
        }
      ]
    };
  }

  const msg = await anthropic.messages.create({
    model: 'claude-3-5-sonnet-20241022',
    max_tokens: 4000,
    temperature: 0.2,
    messages: [
      { role: 'user', content: prompt }
    ]
  });
  
  let responseText = msg.content[0].text;
  
  // Clean markdown if AI returned it
  if (responseText.includes('```json')) {
    responseText = responseText.split('```json')[1].split('```')[0].trim();
  } else if (responseText.includes('```')) {
    responseText = responseText.split('```')[1].split('```')[0].trim();
  }
  
  return JSON.parse(responseText);
};
