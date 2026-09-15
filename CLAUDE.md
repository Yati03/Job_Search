# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Start by finding the reference resumes with the connector to Overleaf based in INSERT PATH\Overleaf-mcp, for jobs in Quebec use the " fr" versions. Here are a short description of the resumes you can find based on their project_id:

#Shape to your resumes
- `Hardware Resume` — CV for Hardware Design & Engineering jobs.
- `Software Resume` — CV for Software Development & Engineering jobs.
- `Hardware Resume fr` & `Software Resume fr` - French equivalents of above mentionned resumes.

When you receive job description, do the following in order (ALWAYS identify the reference CV first):
- Create a folder named 'company name' in INSERT PATH\CV and create all subsequent files in it.
- Create a txt file named 'company name + prep' and write all of the feedback from following instructions in it.
- Act as a senior recuiter. Analyze my resume against the given job description. Give me a match score out of 100 and list the top five missing keywords I need.
- Create a latex file copy of the chosen resume named 'Resume + company name' (if you cannot find company name put the job name) and in that file rewrite my experience section to naturally include those keywords, see Resume Rules section for more details. If any keywords are technical concepts make sure they are listed in the Technical Summary at the bottom right. Use the Google XYZ formula: accomplish X as measured by Y by doing Z. Now loop through that file reducing the least useful information until it's length is ONLY 1 page once that is done save that file as a pdf in the same folder.
- Act as the hiring manager for this role. Ask me the three hardest technical questions you would ask, then give the perfect answer based on my background.
- Create a cover letter in a word doc name 'Cover Letter + company name' (respect Further Guidelines), if the job is in Quebec write it ENTIRELY in french and name it 'Lettre de Motivation + nom de la compagnie':
Structure
- TemplateHeader: Your contact info, date, and recipient info (for email use EMAIL).
- Paragraph 1: Introduce yourself and clearly state the specific position or program you are applying for.
- Paragraph 2-3: Detail your relevant experience, skills, and why you are interested in this specific organization or program. Use concrete examples to show how you fit the program's requirements.
- Paragraph 4: Explain how this opportunity aligns with your future aspirations and what you hope to achieve.
- Closing(conclusion): Summarize your motivation, and express eagerness for an interview.
- Sign-off: "Sincerely," followed by your name.
- Update 'Tracker.xlsx' at path 'INSERT PATH\CV' by searching for the Job name in column A and changing the same row's column D to created, follow Tracker Rules.

Resume Rules

The Resume is divided into Heading, Experience, Projects, Eduction, and Programming Skills section anything outside these sections should NEVER be touched. All changes done should also respect instructions in Further Guidelines.
Heading: 
- NEVER CHANGE ANYTHING HERE.
Introduction:
- Keep the formating.
- Should a short introduction which catches the eye with keywords relevant to the job.
Experience:
- ONLY Make Changes in the \resumeItemList parts.
- Feel free to remove or add a resumeItem if it makes sense relative to the job, NEVER go above 3 resumeItem per resumeItemList.
Projects:
- ONLY Make Changes in the \resumeItemList parts.
- Feel free to remove or add a resumeItem if it makes sense relative to the job, NEVER go above 3 resumeItem per resumeItemList.
Education:
- NEVER CHANGE ANYTHING HERE.
Skills:
- NEVER CHANGE the Language or Langage line.
- NEVER CHANGE the bolden text.
- Feel free to add additional skills outside these limits.

Tracker Rules

- Do not change row 1, leave as is.
- NEVER change anything outside columns D.
- IF you cannot find the Job Name just skip.
- IF you cannot change it, then copy the file contents in Tracker_backup.xlsx then recreate Tracker.xlsv with a copy of the updated Tracker_backup.xlsx and proceed.

Further Guidelines

- Never change the projects that you access from the mcp server.
- My email is INSERT EMAIL.
- Avoid generic statements. 
- Mention specific research, projects, or aspects of the program that excite you.
- Explain what you can contribute, not just what you want to learn.
- Limit the letter to one page.
- Do a grammar and spelling check in the corresponding language.
- If it is an FR resume, do a full accent check verifying that accents are added where they need to.
- Never Bolden, Highlight, Italic, or change the font of any characters in a segment.
- Aim to keep the structure as much as possible.

company name refers to the company name in the given job description.
