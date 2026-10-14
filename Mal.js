import { GoogleGenAI } from "@google/genai";
import 'dotenv/config'; // Loads local .env for local testing

// The SDK automatically looks for the GEMINI_API_KEY environment variable
const ai = new GoogleGenAI({}); 

async function generateText(prompt) {
  const interaction = await ai.interactions.create({
    model: "gemini-3.8-flash",
    input: prompt,
  });
  return interaction.output_text;
}
