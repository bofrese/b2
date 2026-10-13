---
name: linkedin-reply
description: This skill should be used when the user asks to "reply to a LinkedIn comment", "help me respond to a comment on my post", "draft a reply to this comment", "someone commented on my LinkedIn post", or shares a comment they received and wants help crafting a response.
---

# LinkedIn Reply

Draft a reply to a LinkedIn comment on one of the user's posts. Ground the reply in the post's content, related material, and the project's voice and positioning - without sounding polished or promotional.

---

## Step 1 - Load Project Context

Look for and read these files if they exist (skip silently if missing):

- `docs/product/positioning.md` - messaging, audience, voice signals
- `docs/product/personas.md` - who the author writes for
- `docs/product/linkedin-reply-notes.md` - project-specific reply voice, rules, and examples

These define whose voice to write in and what the content should reinforce.

---

## Step 2 - Find and Read the Post File

The user will reference a post by name, number, or file path. Use Glob to locate it:

```
brand/posts/drafts/*{reference}*
```

Read the file. Note:
- The post body and its core argument
- The `## Comments on LinkedIn` section - find the specific comment to reply to
- The `## See also` section - links to related posts and articles

---

## Step 3 - Read Related Content

Parse the `## See also` section for links to related posts and articles. Read 2–3 of the most relevant ones - prioritise files most directly connected to what the commenter raised.

Look for:
- Sharp lines or framings that extend the post's argument
- Mechanisms that explain *why* the thing the commenter observed happens
- Structural or systemic angles that deepen the specific story

Do not read all related files - be selective.

---

## Step 4 - Understand the Comment

Identify:
- What specific situation or observation is the commenter sharing?
- Is it a validation, a question, a counterpoint, or a story?
- Does the user know this person? Ask if unclear - tone should match relationship.
- What is the *underlying mechanism* the comment points to, even if the commenter didn't name it?

---

## Step 5 - Draft the Reply

A good reply does one of: extends the idea, challenges it, reframes it, adds specificity, or names the mechanism beneath the commenter's story.

General principles:
- Opens naturally, not with validation ("Great point!")
- Adds genuine insight - never just agrees
- Uses material from related posts where it sharpens the reply
- Does not pitch, promote, or mention services
- Closes with a dry, direct line - not an uplifting one, not an engagement-bait question

Length: 2–4 short paragraphs.

Apply the `plain-writing` skill in the personal-voice register, and any additional voice rules from `docs/product/linkedin-reply-notes.md` if it exists in the project.

See **`references/reply-principles.md`** for general principles on reply structure, anti-patterns, and tone calibration.

---

## Step 6 - Present and Refine

Present the draft. Briefly explain the angle taken and which related material informed it (1–2 sentences). Ask if tone and content feel right. Refine based on feedback.

---

## Step 7 - Save to Post File

Once finalised, append the reply to the post's markdown file under the comment:

```markdown
**Reply draft:**
{reply text}
```

Use Bash append to avoid encoding issues with special characters in filenames:

```bash
printf '\n**Reply draft:**\n{reply}\n' >> "{post-file-path}"
```

Verify with `tail -15` on the file.

---

## Step 8 - Capture Learnings

After the reply is finalised, reflect on whether anything new was learned during this session about how to reply well - voice adjustments the user made, framings that didn't land, a new rule that emerged from the refinement process.

If yes, prompt the user:

> "We learned something about your reply voice in this session - [one sentence summary]. Want me to save that to `docs/product/linkedin-reply-notes.md`?"

Only prompt if something genuinely non-obvious was learned. Do not save routine application of existing rules.

If the user agrees, append the learning to `docs/product/linkedin-reply-notes.md` under a `## Learnings` section (create it if it doesn't exist). Be specific - capture the rule and a brief note on where it came from.
