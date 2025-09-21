I need you to help me create a clean, repeatable software development workflow, I am a Human developer but any developer at any skill level should be able to adopt these practices you help be determine. In today's coding landscape solo and small team developers are using a myriad of AI LLM coding assistant tools from Cladue, Codex, Gemini, Grok, Cursor, and more and in my experience the issue is keeping both the Human In The Loop (HITL) organized, and in the correct loop of development as well as the AI agents being used. 
My own personal experience has produced a lot of confusion, hallucination, AI LLM agents lying about actual development completions, producing fake stubbed code, mock data, not following the desired intentions of a Developers design, making assumptions and not validating with the HITL, or checking design documentation. The human is also at fault of what I call 'squirrel brain' to veer off scope, bouncing between multiple AI LLM terminal cli windows and the human themself forgetting context and what they are actually doing. 
My projects have spiraled from initial great ideas and planning mode to initial development then the product gets lost in so many errant conversations, issues during coding sessions, lost context, not sticking to a development plan, and just general loss of memory by both the AI LLM agent and the HITL together. 
This produces a huge frustration, products that never ship and sit in the project folder or unfinished Github committed projects. 
I have spent hundreds of development hours wasted planning, prompting with the LLM cli agent in terminal, too many competing created documents (usually in markdown the agent creates) so many confusing versioned documents, different plans, veered ideas, nothing converges to a working product. Broken code, mock code, non-production ready, initial idea and plans not followed. disorganized codebase with files all over the place that causes spaghetti code and just a huge mess of files that discourages the developer to even continue and shelf the idea. 
I am not the only one who has had these frustrations and More. in today's AI LLM age these AI tools are great, Humans have great ideas (they don't have to be a developer) and these ideas can improve existing tech or create new markets, but unfortunately never will see production time and real users due to all these issues in the development process. I have gone around in circles with ideas to fix these issues but they keep falling short and I can never get them fully developed because I too in the process to try and dogfood a development to create a solution to this fall flat and shelf the idea too. Its a horrible cycle that just never ends I need your help to research and look for how we can stop this madness and get a working solution, that is solid, repeatable, industry can adopt and use and we can finally create a development solution around the process. I have looked at spec driven design as a tool but even that has flaws and the human or AI break the chain at points. I think spec drive design with Documentation First approach is definitely the path to go but we can't get there fully due to all the concerns I already laid out. 
I don't want to scrap my recent project to try and resolve this, but my general idea is pretty much what I think creating a standard around. I coined a term call Nexus Protocol I want to wrap around this idea of creating a industry standard practice workflow to develop with AI LLMs and HITL process, using a spec driven workflow of 'Specify → Plan → Tasks → Build → Deploy' with core pieces of all this below:
Specification-First
Define WHAT you want to build before HOW
AI-Augmented
Leverage AI intelligently throughout the process
Technology Agnostic
Works with ANY language, framework, or stack
the The NEXUS Workflow
A systematic, AI-augmented approach that ensures you build the right thing, the right way, every time.
Describe > Analyze > Specify > Plan > Tasks > Build
the Nexus Build Cycle Architecture
REVIEW -> BUILD -> VALIDATE -> TEST -> FIX -> COMPLETE (cycle back to review when needed)
Nexus Core Principles
1. Intent-Driven
Specifications define the 'what' before the 'how'
2. Rich Specification
Using guardrails and organizational principles
3. Multi-Step Refinement
Rather than one-shot code generation
4. AI-Powered
Heavy reliance on advanced AI model capabilities
this all is the first part of Ideation to a detailed plan/tasks which seems fine, but the issue is when we actually get to the build phase it all falls apart. I started a project too that follows these principles above and Nexus protocls called Nexus Project Box with the intent to be a tool that stores all the project data info created in the initial ideation Nexus workflow to then guide the AI LLM and HITL through the whole process, I think I am on a good path but I keep veering and squirelling with this too. I have 'sessions' in which I engaged the tool I am using Claude Code CLI and I chat with it to build, but it keeps lying and say it does stuff but many times its not true or it creates fake partial code. one thing I have been trying is a cycled coding sessions
1. Coding Review session -  initial review and kick off of project planning initial real coding session
2. Real coding session where code is truly written
3. Coding Review session where tests, validation of previous Session # like a QA session
4. Coding Fix session review session findings
5. Real Coding session continued
6. Coding Review
7. Coding Fix
and so on... but this needs to be programatic, git version controlled, use git worktree sessions somehow for features during development and multiple agents working on features/phases, tasks and so forth.
You need to really review all my ideas, issues, concerns and the overall problems I have explained. really ultrathink and help me find a way to get to a true production ready workflow for all this and be able to stop this insanity cycle.
