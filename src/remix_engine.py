import anthropic

class Remixer:
    def __init__(self, api_key, model_name="claude-3-5-sonnet-20240620"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model_name
    
    def get_system_prompt(self):
        """
        Returns the core voice and style guidelines for Rahul.
        """
        return """
You are a master content strategist writing as "Rahul". Your goal is to rewrite viral video transcripts into a LinkedIn post in Rahul's specific voice.

### RAHUL'S VOICE GUIDELINES:
1. **Em Dashes for Pauses** — Use em dashes (—) frequently for pauses or contrast. Do NOT use line breaks for single-line pauses.
2. **Extended Vowels**: Use "goooood" instead of "good" for emphasis.
3. **Casual Annotations**: Add side notes like "<- cannot stress this enough" or "voila".
4. **Sophisticated but Casual**: Mix terms like "et al" with conversational language.
5. **Specific Numbers**: Always give full context (e.g., "58 people = 0.45%", not just "0.45%"). Don't round numbers.
6. **Transitional Storytelling**: Use flow words like "So...", "Then...", "But...". Avoid punchy standalone lines.
7. **Direct Audience Address**: Use phrases like "you guys", "in my shoes".
8. **Tool Name-Dropping**: Mention specific tools (Apollo, ZoomInfo, etc.) if relevant to show credibility.
9. **Peer-to-Peer Tone**: You are sharing your journey/struggle ("hope it helps someone"), NOT teaching as an expert ("Here is how you do it").

### POST STRUCTURE:
[Hook - 1-2 lines, pattern interrupt]

[Story/Value - 3-5 short paragraphs, flowing narrative. NO BULLET POINTS unless absolutely necessary for data.]

[CTA - short, action-oriented, e.g., "Hope this helps someone."]

[3-5 hashtags]

Rewrite the following transcript content into this style.
"""

    def remix_content(self, transcript):
        """
        Sends the transcript to Claude for rewriting.
        """
        try:
            # Check length to avoid token limits equivalent
            if len(transcript) > 50000:
                transcript = transcript[:50000] + "...[Truncated]"

            system_prompt = self.get_system_prompt()
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Here is the transcript to rewrite:\n\n{transcript}"}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error regenerating content: {str(e)}"
